#!/usr/bin/env python3
"""
Gestionnaire de Paper Trading (Mode simulation)
"""

import json
import os
from datetime import datetime
import config

class PaperTradingManager:
    def __init__(self):
        # Valeurs par défaut si config manquante
        self.track_file = getattr(config, 'PAPER_TRADING_TRACK_FILE', 'paper_trading_history.json')
        initial_balance = getattr(config, 'PAPER_TRADING_INITIAL_BALANCE', 1000)
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.open_positions = []
        self.closed_positions = []
        self.load_state()

    def load_state(self):
        """Charge l'état du paper trading depuis le fichier"""
        try:
            # Vérifier si un fichier de test existe pour le développement
            test_file = 'data/paper_trading_data.json'
            if os.path.exists(test_file):
                with open(test_file, 'r') as f:
                    data = json.load(f)
                    self.balance = data.get('balance', self.initial_balance)
                    self.initial_balance = data.get('initial_balance', self.initial_balance)
                    self.open_positions = data.get('open_positions', [])
                    self.closed_positions = data.get('closed_positions', [])
                    print(f"✓ Chargé depuis le fichier de test: {test_file}")
                    print(f"  - {len(self.closed_positions)} trades fermés disponibles pour les tests")
                    return

            # Sinon, utiliser le fichier normal
            if os.path.exists(self.track_file):
                with open(self.track_file, 'r') as f:
                    data = json.load(f)
                    self.balance = data.get('balance', self.initial_balance)
                    self.initial_balance = data.get('initial_balance', self.initial_balance)
                    self.open_positions = data.get('open_positions', [])
                    self.closed_positions = data.get('closed_positions', [])
                    print(f"✓ Chargé depuis {self.track_file}")
            else:
                print(f"⚠️ Aucun fichier de paper trading trouvé ({self.track_file})")
        except Exception as e:
            print(f"✗ Erreur lors du chargement du paper trading: {e}")

    def save_state(self):
        """Sauvegarde l'état du paper trading"""
        try:
            data = {
                'balance': self.balance,
                'initial_balance': self.initial_balance,
                'open_positions': self.open_positions,
                'closed_positions': self.closed_positions,
                'last_update': datetime.now().isoformat()
            }
            with open(self.track_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du paper trading: {e}")

    def can_open_position(self):
        """Vérifie si on peut ouvrir une nouvelle position"""
        max_positions = getattr(config, 'PAPER_TRADING_MAX_POSITIONS', 3)
        if len(self.open_positions) >= max_positions:
            return False, f"Maximum de positions ouvertes atteint ({max_positions})"

        if self.balance <= 0:
            return False, "Balance insuffisante"

        return True, "OK"

    def open_position(self, signal, analysis):
        """Ouvre une position virtuelle"""
        can_open, reason = self.can_open_position()
        if not can_open:
            return None, reason

        # Récupérer les paramètres de levier
        leverage = getattr(config, 'PAPER_TRADING_LEVERAGE', 1)
        simulate_liquidation = getattr(config, 'PAPER_TRADING_SIMULATE_LIQUIDATION', True)
        liquidation_threshold = getattr(config, 'PAPER_TRADING_LIQUIDATION_THRESHOLD', 0.8)

        # Calculer la marge requise (capital à investir)
        position_size_percent = getattr(config, 'PAPER_TRADING_POSITION_SIZE_PERCENT', 2)
        margin_usdt = self.balance * (position_size_percent / 100)

        # Calculer la taille de position avec effet de levier
        position_size_usdt = margin_usdt * leverage
        position_size_crypto = position_size_usdt / signal['entry']

        # Calculer le prix de liquidation
        liquidation_price = None
        if simulate_liquidation and leverage > 1:
            if signal['type'] == 'LONG':
                # Pour un LONG, liquidation si le prix descend trop
                liquidation_price = signal['entry'] * (1 - (liquidation_threshold / leverage))
            else:  # SHORT
                # Pour un SHORT, liquidation si le prix monte trop
                liquidation_price = signal['entry'] * (1 + (liquidation_threshold / leverage))

        # Créer la position
        position = {
            'id': f"{analysis['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'symbol': analysis['symbol'],
            'type': signal['type'],
            'entry_price': signal['entry'],
            'current_price': signal['entry'],
            'tp': signal['tp'],
            'sl': signal['sl'],
            'size_usdt': position_size_usdt,  # Taille totale avec levier
            'margin_usdt': margin_usdt,  # Capital réellement investi
            'size_crypto': position_size_crypto,
            'leverage': leverage,
            'liquidation_price': liquidation_price,
            'opened_at': datetime.now().isoformat(),
            'confidence': signal['confidence'],
            'risk_reward': signal['risk_reward'],
            'pnl_usdt': 0,
            'pnl_percent': 0,
            'status': 'open'
        }

        # Retirer la marge (capital réel) de la balance, pas la position totale
        self.balance -= margin_usdt

        self.open_positions.append(position)
        self.save_state()

        return position, "Position ouverte avec succès"

    def update_positions(self, symbol, current_price):
        """Met à jour les positions ouvertes et vérifie les TP/SL/Liquidation"""
        updated_positions = []
        closed_count = 0

        for position in self.open_positions:
            if position['symbol'] != symbol:
                updated_positions.append(position)
                continue

            # Mettre à jour le prix courant
            position['current_price'] = current_price

            # Calculer le P&L (déjà amplifié par le levier via size_crypto)
            if position['type'] == 'LONG':
                pnl_usdt = (current_price - position['entry_price']) * position['size_crypto']
                pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100

                # Calculer le P&L en % de la marge investie (avec effet de levier)
                margin = position.get('margin_usdt', position.get('size_usdt', 0))
                if margin > 0:
                    pnl_percent_on_margin = (pnl_usdt / margin) * 100
                else:
                    pnl_percent_on_margin = 0

                # Vérifier LIQUIDATION en premier
                liquidation_price = position.get('liquidation_price')
                if liquidation_price and current_price <= liquidation_price:
                    self.close_position(position, liquidation_price, 'LIQUIDATED')
                    closed_count += 1
                    continue

                # TRAILING STOP pour LONG
                trailing_stop_enabled = getattr(config, 'PAPER_TRADING_TRAILING_STOP', False)
                if trailing_stop_enabled:
                    trailing_stop_percent = getattr(config, 'PAPER_TRADING_TRAILING_STOP_PERCENT', 0.5) / 100
                    # Calculer le nouveau SL basé sur le prix actuel
                    new_sl = current_price * (1 - trailing_stop_percent)
                    # Le SL ne peut que monter (jamais descendre)
                    if new_sl > position['sl']:
                        position['sl'] = new_sl

                # TRAILING TAKE PROFIT pour LONG
                trailing_tp_enabled = getattr(config, 'PAPER_TRADING_TRAILING_TP', False)
                if trailing_tp_enabled:
                    # Suivre le prix le plus haut atteint
                    highest_price = position.get('highest_price', position['entry_price'])
                    if current_price > highest_price:
                        highest_price = current_price
                        position['highest_price'] = highest_price

                        # Calculer le nouveau TP basé sur le nouveau pic
                        trailing_tp_percent = getattr(config, 'PAPER_TRADING_TRAILING_TP_PERCENT', 2.0) / 100
                        new_tp = highest_price * (1 + trailing_tp_percent)
                        # Le TP ne peut que monter (jamais descendre)
                        if new_tp > position['tp']:
                            position['tp'] = new_tp

                # Vérifier TP/SL
                if current_price >= position['tp']:
                    self.close_position(position, current_price, 'TP_HIT')
                    closed_count += 1
                    continue
                elif current_price <= position['sl']:
                    self.close_position(position, current_price, 'SL_HIT')
                    closed_count += 1
                    continue
            else:  # SHORT
                pnl_usdt = (position['entry_price'] - current_price) * position['size_crypto']
                pnl_percent = ((position['entry_price'] - current_price) / position['entry_price']) * 100

                # Calculer le P&L en % de la marge investie (avec effet de levier)
                margin = position.get('margin_usdt', position.get('size_usdt', 0))
                if margin > 0:
                    pnl_percent_on_margin = (pnl_usdt / margin) * 100
                else:
                    pnl_percent_on_margin = 0

                # Vérifier LIQUIDATION en premier
                liquidation_price = position.get('liquidation_price')
                if liquidation_price and current_price >= liquidation_price:
                    self.close_position(position, liquidation_price, 'LIQUIDATED')
                    closed_count += 1
                    continue

                # TRAILING STOP pour SHORT
                trailing_stop_enabled = getattr(config, 'PAPER_TRADING_TRAILING_STOP', False)
                if trailing_stop_enabled:
                    trailing_stop_percent = getattr(config, 'PAPER_TRADING_TRAILING_STOP_PERCENT', 0.5) / 100
                    # Calculer le nouveau SL basé sur le prix actuel
                    new_sl = current_price * (1 + trailing_stop_percent)
                    # Le SL ne peut que descendre (jamais monter)
                    if new_sl < position['sl']:
                        position['sl'] = new_sl

                # TRAILING TAKE PROFIT pour SHORT
                trailing_tp_enabled = getattr(config, 'PAPER_TRADING_TRAILING_TP', False)
                if trailing_tp_enabled:
                    # Suivre le prix le plus bas atteint
                    lowest_price = position.get('lowest_price', position['entry_price'])
                    if current_price < lowest_price:
                        lowest_price = current_price
                        position['lowest_price'] = lowest_price

                        # Calculer le nouveau TP basé sur le nouveau creux
                        trailing_tp_percent = getattr(config, 'PAPER_TRADING_TRAILING_TP_PERCENT', 2.0) / 100
                        new_tp = lowest_price * (1 - trailing_tp_percent)
                        # Le TP ne peut que descendre (jamais monter pour un SHORT)
                        if new_tp < position['tp']:
                            position['tp'] = new_tp

                # Vérifier TP/SL
                if current_price <= position['tp']:
                    self.close_position(position, current_price, 'TP_HIT')
                    closed_count += 1
                    continue
                elif current_price >= position['sl']:
                    self.close_position(position, current_price, 'SL_HIT')
                    closed_count += 1
                    continue

            position['pnl_usdt'] = pnl_usdt
            position['pnl_percent'] = pnl_percent
            position['pnl_percent_on_margin'] = pnl_percent_on_margin
            updated_positions.append(position)

        self.open_positions = updated_positions
        self.save_state()

        return closed_count

    def close_position(self, position, exit_price, reason):
        """Ferme une position"""
        # Récupérer la marge (capital réellement investi)
        margin = position.get('margin_usdt', position.get('size_usdt', 0))

        # Calculer le P&L final
        if position['type'] == 'LONG':
            pnl_usdt = (exit_price - position['entry_price']) * position['size_crypto']
            pnl_percent = ((exit_price - position['entry_price']) / position['entry_price']) * 100
        else:  # SHORT
            pnl_usdt = (position['entry_price'] - exit_price) * position['size_crypto']
            pnl_percent = ((position['entry_price'] - exit_price) / position['entry_price']) * 100

        # En cas de liquidation, limiter la perte à la marge investie
        if reason == 'LIQUIDATED':
            pnl_usdt = -margin  # Perte totale de la marge
            pnl_percent = -100  # 100% de perte sur la marge

        # Calculer le P&L en % de la marge (avec effet de levier)
        if margin > 0:
            pnl_percent_on_margin = (pnl_usdt / margin) * 100
        else:
            pnl_percent_on_margin = 0

        # Mettre à jour la balance: rendre la marge + P&L (ou 0 si liquidé)
        if reason == 'LIQUIDATED':
            # En cas de liquidation, on perd toute la marge
            self.balance += 0
        else:
            self.balance += margin + pnl_usdt

        # Finaliser la position
        position['exit_price'] = exit_price
        position['closed_at'] = datetime.now().isoformat()
        position['pnl_usdt'] = pnl_usdt
        position['pnl_percent'] = pnl_percent
        position['pnl_percent_on_margin'] = pnl_percent_on_margin
        position['close_reason'] = reason
        position['status'] = 'closed'

        # Calculer la durée
        opened = datetime.fromisoformat(position['opened_at'])
        closed = datetime.fromisoformat(position['closed_at'])
        duration = (closed - opened).total_seconds() / 3600  # en heures
        position['duration_hours'] = duration

        self.closed_positions.append(position)
        self.save_state()

        return position

    def get_statistics(self):
        """Calcule les statistiques de performance"""
        # Calculer le capital total (balance libre + marge dans positions ouvertes + P&L non réalisé)
        # Utiliser margin_usdt car c'est le capital réellement investi
        open_capital = sum(p.get('margin_usdt', p.get('size_usdt', 0)) for p in self.open_positions)
        open_pnl = sum(p.get('pnl_usdt', 0) for p in self.open_positions)
        total_portfolio_value = self.balance + open_capital + open_pnl

        if not self.closed_positions:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'total_pnl_percent': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'best_trade': 0,
                'worst_trade': 0,
                'open_positions': len(self.open_positions),
                'current_balance': self.balance,
                'total_portfolio_value': total_portfolio_value,
                'open_positions_value': open_capital,
                'unrealized_pnl': open_pnl,
                'initial_balance': self.initial_balance,
                'roi': ((total_portfolio_value - self.initial_balance) / self.initial_balance) * 100
            }

        wins = [p for p in self.closed_positions if p['pnl_usdt'] > 0]
        losses = [p for p in self.closed_positions if p['pnl_usdt'] <= 0]

        total_pnl = sum(p['pnl_usdt'] for p in self.closed_positions)
        roi = ((total_portfolio_value - self.initial_balance) / self.initial_balance) * 100

        stats = {
            'total_trades': len(self.closed_positions),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': (len(wins) / len(self.closed_positions)) * 100 if self.closed_positions else 0,
            'total_pnl': total_pnl,
            'total_pnl_percent': (total_pnl / self.initial_balance) * 100,
            'avg_win': sum(p['pnl_usdt'] for p in wins) / len(wins) if wins else 0,
            'avg_loss': sum(p['pnl_usdt'] for p in losses) / len(losses) if losses else 0,
            'best_trade': max(p['pnl_usdt'] for p in self.closed_positions) if self.closed_positions else 0,
            'worst_trade': min(p['pnl_usdt'] for p in self.closed_positions) if self.closed_positions else 0,
            'open_positions': len(self.open_positions),
            'current_balance': self.balance,
            'total_portfolio_value': total_portfolio_value,
            'open_positions_value': open_capital,
            'unrealized_pnl': open_pnl,
            'initial_balance': self.initial_balance,
            'roi': roi,
            'avg_trade_duration': sum(p.get('duration_hours', 0) for p in self.closed_positions) / len(self.closed_positions) if self.closed_positions else 0
        }

        return stats

    def format_position_message(self, position, action="OPENED"):
        """Formate un message de position pour Pushover"""
        if action == "OPENED":
            leverage = position.get('leverage', 1)
            margin = position.get('margin_usdt', position.get('size_usdt', 0))
            liquidation_price = position.get('liquidation_price')

            message = f"""
📊 PAPER TRADING - Position ouverte

{position['type']} sur {position['symbol']}"""

            if leverage > 1:
                message += f" (Levier {leverage}x)"

            message += f"""

Entrée: ${position['entry_price']:.4f}
TP: ${position['tp']:.4f}
SL: ${position['sl']:.4f}"""

            if liquidation_price:
                message += f"""
Liquidation: ${liquidation_price:.4f}"""

            message += f"""
Taille position: ${position['size_usdt']:.2f}
Marge investie: ${margin:.2f}
R/R: 1:{position['risk_reward']:.2f}

Balance: ${self.balance:.2f}
Positions ouvertes: {len(self.open_positions)}/{getattr(config, 'PAPER_TRADING_MAX_POSITIONS', 3)}

🔗 Lien Bitget: {bitget_url}
"""
        else:  # CLOSED
            emoji = "🟢" if position['pnl_usdt'] > 0 else "🔴"

            # Emoji spécial pour liquidation
            if position.get('close_reason') == 'LIQUIDATED':
                emoji = "💀"

            # Calculer la valeur totale du portefeuille
            stats = self.get_statistics()
            portfolio_value = stats.get('total_portfolio_value', self.balance)

            leverage = position.get('leverage', 1)
            margin = position.get('margin_usdt', position.get('size_usdt', 0))
            pnl_percent_on_margin = position.get('pnl_percent_on_margin', position.get('pnl_percent', 0))

            # Générer l'URL Bitget
            bitget_url = f"https://www.bitget.site/fr/futures/usdt/{position['symbol']}"

            message = f"""
{emoji} PAPER TRADING - Position fermée

{position['type']} sur {position['symbol']}"""

            if leverage > 1:
                message += f" (Levier {leverage}x)"

            message += f"""
Raison: {position['close_reason']}

Entrée: ${position['entry_price']:.4f}
Sortie: ${position['exit_price']:.4f}
Durée: {position.get('duration_hours', 0):.1f}h

P&L: ${position['pnl_usdt']:.2f}"""

            if leverage > 1:
                message += f" ({pnl_percent_on_margin:+.2f}% sur marge)"
            else:
                message += f" ({position['pnl_percent']:+.2f}%)"

            message += f"""
Portefeuille: ${portfolio_value:.2f} (ROI: {stats['roi']:.2f}%)

Total trades: {len(self.closed_positions)}
Win rate: {(len([p for p in self.closed_positions if p['pnl_usdt'] > 0]) / len(self.closed_positions) * 100):.1f}%

🔗 Lien Bitget: {bitget_url}
"""
        return message

    def get_open_position_by_symbol(self, symbol):
        """Récupère une position ouverte par symbole"""
        for position in self.open_positions:
            if position['symbol'] == symbol:
                return position
        return None

    def reset(self):
        """Réinitialise le paper trading"""
        initial_balance = getattr(config, 'PAPER_TRADING_INITIAL_BALANCE', 1000)
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.open_positions = []
        self.closed_positions = []
        self.save_state()
        print("Paper trading réinitialisé")
