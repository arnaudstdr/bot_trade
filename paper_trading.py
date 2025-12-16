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
            if os.path.exists(self.track_file):
                with open(self.track_file, 'r') as f:
                    data = json.load(f)
                    self.balance = data.get('balance', self.initial_balance)
                    self.initial_balance = data.get('initial_balance', self.initial_balance)
                    self.open_positions = data.get('open_positions', [])
                    self.closed_positions = data.get('closed_positions', [])
        except Exception as e:
            print(f"Erreur lors du chargement du paper trading: {e}")

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

        # Calculer la taille de position
        position_size_percent = getattr(config, 'PAPER_TRADING_POSITION_SIZE_PERCENT', 2)
        position_size_usdt = self.balance * (position_size_percent / 100)
        position_size_crypto = position_size_usdt / signal['entry']

        # Créer la position
        position = {
            'id': f"{analysis['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'symbol': analysis['symbol'],
            'type': signal['type'],
            'entry_price': signal['entry'],
            'current_price': signal['entry'],
            'tp': signal['tp'],
            'sl': signal['sl'],
            'size_usdt': position_size_usdt,
            'size_crypto': position_size_crypto,
            'opened_at': datetime.now().isoformat(),
            'confidence': signal['confidence'],
            'risk_reward': signal['risk_reward'],
            'pnl_usdt': 0,
            'pnl_percent': 0,
            'status': 'open'
        }

        # Retirer le capital investi de la balance
        self.balance -= position_size_usdt

        self.open_positions.append(position)
        self.save_state()

        return position, "Position ouverte avec succès"

    def update_positions(self, symbol, current_price):
        """Met à jour les positions ouvertes et vérifie les TP/SL"""
        updated_positions = []
        closed_count = 0

        for position in self.open_positions:
            if position['symbol'] != symbol:
                updated_positions.append(position)
                continue

            # Mettre à jour le prix courant
            position['current_price'] = current_price

            # Calculer le P&L
            if position['type'] == 'LONG':
                pnl_usdt = (current_price - position['entry_price']) * position['size_crypto']
                pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100

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
            updated_positions.append(position)

        self.open_positions = updated_positions
        self.save_state()

        return closed_count

    def close_position(self, position, exit_price, reason):
        """Ferme une position"""
        # Calculer le P&L final
        if position['type'] == 'LONG':
            pnl_usdt = (exit_price - position['entry_price']) * position['size_crypto']
            pnl_percent = ((exit_price - position['entry_price']) / position['entry_price']) * 100
        else:  # SHORT
            pnl_usdt = (position['entry_price'] - exit_price) * position['size_crypto']
            pnl_percent = ((position['entry_price'] - exit_price) / position['entry_price']) * 100

        # Mettre à jour la balance
        self.balance += position['size_usdt'] + pnl_usdt

        # Finaliser la position
        position['exit_price'] = exit_price
        position['closed_at'] = datetime.now().isoformat()
        position['pnl_usdt'] = pnl_usdt
        position['pnl_percent'] = pnl_percent
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
        # Calculer le capital total (balance libre + capital dans positions ouvertes + P&L non réalisé)
        open_capital = sum(p['size_usdt'] for p in self.open_positions)
        open_pnl = sum(p['pnl_usdt'] for p in self.open_positions)
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
            message = f"""
📊 PAPER TRADING - Position ouverte

{position['type']} sur {position['symbol']}

Entrée: ${position['entry_price']:.4f}
TP: ${position['tp']:.4f}
SL: ${position['sl']:.4f}
Taille: ${position['size_usdt']:.2f} ({position['size_crypto']:.6f})
R/R: 1:{position['risk_reward']:.2f}

Balance: ${self.balance:.2f}
Positions ouvertes: {len(self.open_positions)}/{getattr(config, 'PAPER_TRADING_MAX_POSITIONS', 3)}
"""
        else:  # CLOSED
            emoji = "🟢" if position['pnl_usdt'] > 0 else "🔴"

            # Calculer la valeur totale du portefeuille
            stats = self.get_statistics()
            portfolio_value = stats.get('total_portfolio_value', self.balance)

            message = f"""
{emoji} PAPER TRADING - Position fermée

{position['type']} sur {position['symbol']}
Raison: {position['close_reason']}

Entrée: ${position['entry_price']:.4f}
Sortie: ${position['exit_price']:.4f}
Durée: {position.get('duration_hours', 0):.1f}h

P&L: ${position['pnl_usdt']:.2f} ({position['pnl_percent']:.2f}%)
Portefeuille: ${portfolio_value:.2f} (ROI: {stats['roi']:.2f}%)

Total trades: {len(self.closed_positions)}
Win rate: {(len([p for p in self.closed_positions if p['pnl_usdt'] > 0]) / len(self.closed_positions) * 100):.1f}%
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
