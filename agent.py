#!/usr/bin/env python3
"""
Agent de trading autonome avec alertes Pushover et validation LLM
"""

import ccxt
import pandas as pd
import ta
import time
import json
import requests
import os
from datetime import datetime
from mistralai import Mistral
import config
from paper_trading import PaperTradingManager

# Fichier pour stocker l'état des signaux
# Utilise /app/data dans Docker, sinon ./data
DATA_DIR = "/app/data" if os.path.exists("/app/data") else "data"
# Créer le dossier data s'il n'existe pas
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
STATE_FILE = os.path.join(DATA_DIR, "signals_state.json")

class TradingAgent:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.mistral_client = Mistral(api_key=config.MISTRAL_API_KEY)
        self.active_signals = self.load_state()

        # Initialiser le paper trading si activé
        paper_trading_enabled = getattr(config, 'PAPER_TRADING_ENABLED', False)
        if paper_trading_enabled:
            self.paper_trading = PaperTradingManager()
            print(f"📊 Paper Trading activé - Balance: ${self.paper_trading.balance:.2f}")
        else:
            self.paper_trading = None

    def load_state(self):
        """Charge l'état des signaux actifs depuis le fichier"""
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_state(self):
        """Sauvegarde l'état des signaux actifs"""
        with open(STATE_FILE, 'w') as f:
            json.dump(self.active_signals, f, indent=2)

    def is_trading_hours(self):
        """Vérifie si on est dans les horaires de trading autorisés"""
        if not config.TRADING_HOURS_ENABLED:
            return True

        now = datetime.now()
        current_hour = now.hour
        current_day = now.weekday()  # 0=Lundi, 6=Dimanche

        # Vérifier le jour
        if current_day not in config.TRADING_ENABLED_DAYS:
            return False

        # Vérifier l'heure
        if current_hour < config.TRADING_HOURS_START or current_hour >= config.TRADING_HOURS_END:
            return False

        return True

    def get_ohlcv_data(self, symbol, timeframe=config.TIMEFRAME, limit=200):
        """Récupère les données OHLCV depuis Binance"""
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    def calculate_indicators(self, df):
        """Calcule tous les indicateurs techniques"""
        # Moyennes mobiles
        df['MA_9'] = ta.trend.sma_indicator(df['close'], window=9)
        df['MA_21'] = ta.trend.sma_indicator(df['close'], window=21)
        df['MA_50'] = ta.trend.sma_indicator(df['close'], window=50)
        df['EMA_12'] = ta.trend.ema_indicator(df['close'], window=12)
        df['EMA_50'] = ta.trend.ema_indicator(df['close'], window=50)

        # RSI
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)

        # MACD
        macd = ta.trend.MACD(df['close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()

        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['close'])
        df['BB_High'] = bollinger.bollinger_hband()
        df['BB_Low'] = bollinger.bollinger_lband()
        df['BB_Mid'] = bollinger.bollinger_mavg()

        # ATR pour volatilité
        df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)

        # Volume
        df['Volume_MA'] = df['volume'].rolling(window=20).mean()

        return df

    def analyze_crypto(self, df, symbol):
        """Analyse une crypto et génère un rapport complet"""
        last = df.iloc[-1]
        prev = df.iloc[-2]

        price = last['close']

        # Analyse de tendance
        trend = "NEUTRE"
        if price > last['MA_21'] and price > last['MA_50']:
            trend = "HAUSSIERE"
        elif price < last['MA_21'] and price < last['MA_50']:
            trend = "BAISSIERE"

        # Score de force (0-100)
        score = 0
        signals = []

        # Analyse RSI
        if 30 <= last['RSI'] <= 70:
            score += 20
            if last['RSI'] > 50:
                signals.append(f"RSI haussier ({last['RSI']:.1f})")
            else:
                signals.append(f"RSI baissier ({last['RSI']:.1f})")
        elif last['RSI'] < 30:
            score += 30
            signals.append(f"RSI SURVENDU ({last['RSI']:.1f}) - Opportunité LONG")
        elif last['RSI'] > 70:
            score += 30
            signals.append(f"RSI SURACHETÉ ({last['RSI']:.1f}) - Opportunité SHORT")

        # Analyse MACD
        if last['MACD'] > last['MACD_Signal']:
            score += 15
            signals.append("MACD au-dessus du signal (haussier)")
        else:
            score += 15
            signals.append("MACD en-dessous du signal (baissier)")

        # Croisement MACD récent
        if prev['MACD'] <= prev['MACD_Signal'] and last['MACD'] > last['MACD_Signal']:
            score += 25
            signals.append("CROISEMENT MACD HAUSSIER")
        elif prev['MACD'] >= prev['MACD_Signal'] and last['MACD'] < last['MACD_Signal']:
            score += 25
            signals.append("CROISEMENT MACD BAISSIER")
        else:
            score += 10

        # Analyse Bollinger Bands
        if price <= last['BB_Low']:
            score += 20
            signals.append("Prix sur Bollinger inférieure - Rebond possible (LONG)")
        elif price >= last['BB_High']:
            score += 20
            signals.append("Prix sur Bollinger supérieure - Correction possible (SHORT)")
        else:
            score += 10

        # Analyse de tendance MA
        if price > last['MA_9'] and last['MA_9'] > last['MA_21']:
            score += 15
            signals.append("Tendance MA haussière")
        elif price < last['MA_9'] and last['MA_9'] < last['MA_21']:
            score += 15
            signals.append("Tendance MA baissière")
        else:
            score += 5

        # Volume
        if last['volume'] > last['Volume_MA'] * 1.5:
            score += 15
            signals.append("Volume élevé - Momentum fort")
        else:
            score += 5

        return {
            'symbol': symbol,
            'price': price,
            'trend': trend,
            'score': min(score, 100),
            'rsi': last['RSI'],
            'macd': last['MACD'],
            'macd_signal': last['MACD_Signal'],
            'ma_21': last['MA_21'],
            'ma_50': last['MA_50'],
            'ema_12': last['EMA_12'],
            'ema_50': last['EMA_50'],
            'ema_12_prev': prev['EMA_12'],
            'ema_50_prev': prev['EMA_50'],
            'bb_low': last['BB_Low'],
            'bb_high': last['BB_High'],
            'atr': last['ATR'],
            'volume': last['volume'],
            'volume_ma': last['Volume_MA'],
            'signals': signals
        }

    def generate_trading_signal(self, analysis):
        """Génère un signal de trading LONG ou SHORT avec TP/SL"""
        price = analysis['price']
        atr = analysis['atr']

        # Calcul dynamique des TP/SL basés sur l'ATR
        atr_multiplier_tp = 2.5
        atr_multiplier_sl = 1.5

        signal = None

        # Vérifier le croisement EMA 12/50 (OBLIGATOIRE)
        ema_cross_bullish = analysis['ema_12'] > analysis['ema_50']  # EMA12 au-dessus d'EMA50
        ema_cross_bearish = analysis['ema_12'] < analysis['ema_50']  # EMA12 en-dessous d'EMA50

        # Conditions pour LONG (sans EMA)
        long_conditions = [
            analysis['rsi'] < 40,
            analysis['price'] > analysis['ma_21'],
            analysis['macd'] > analysis['macd_signal'],
            analysis['score'] >= config.MIN_CONFIDENCE_SCORE
        ]

        # Conditions pour SHORT (sans EMA)
        short_conditions = [
            analysis['rsi'] > 60,
            analysis['price'] < analysis['ma_21'],
            analysis['macd'] < analysis['macd_signal'],
            analysis['score'] >= config.MIN_CONFIDENCE_SCORE
        ]

        # Conditions alternatives pour LONG (rebond sur support, sans EMA)
        long_support = [
            analysis['price'] <= analysis['bb_low'] * 1.02,
            analysis['rsi'] < 35,
            analysis['trend'] != "BAISSIERE"
        ]

        # Conditions alternatives pour SHORT (rejet de résistance, sans EMA)
        short_resistance = [
            analysis['price'] >= analysis['bb_high'] * 0.98,
            analysis['rsi'] > 65,
            analysis['trend'] != "HAUSSIERE"
        ]

        # VÉRIFICATION OBLIGATOIRE DE L'EMA + conditions
        if ema_cross_bullish and (sum(long_conditions) >= 3 or sum(long_support) >= 2):
            signal = {
                'type': 'LONG',
                'entry': price,
                'tp': price + (atr * atr_multiplier_tp),
                'sl': price - (atr * atr_multiplier_sl),
                'confidence': analysis['score']
            }
        elif ema_cross_bearish and (sum(short_conditions) >= 3 or sum(short_resistance) >= 2):
            signal = {
                'type': 'SHORT',
                'entry': price,
                'tp': price - (atr * atr_multiplier_tp),
                'sl': price + (atr * atr_multiplier_sl),
                'confidence': analysis['score']
            }

        # Vérifier le ratio Risk/Reward
        if signal:
            risk_reward = abs((signal['tp'] - signal['entry']) / (signal['sl'] - signal['entry']))
            if risk_reward < config.MIN_RISK_REWARD:
                return None
            signal['risk_reward'] = risk_reward

        return signal

    def validate_signal_with_llm(self, analysis, signal):
        """Valide le signal avec Mistral AI"""
        prompt = f"""Tu es un expert en trading de cryptomonnaies. Analyse ce signal de trading et donne ton avis.

CRYPTOMONNAIE: {analysis['symbol']}
PRIX ACTUEL: ${analysis['price']:.4f}
TENDANCE: {analysis['trend']}

INDICATEURS TECHNIQUES:
- RSI: {analysis['rsi']:.1f}
- MACD: {analysis['macd']:.4f} | Signal: {analysis['macd_signal']:.4f}
- MA21: ${analysis['ma_21']:.4f}
- MA50: ${analysis['ma_50']:.4f}
- EMA12: ${analysis['ema_12']:.4f}
- EMA50: ${analysis['ema_50']:.4f}
- Croisement EMA: {'EMA12 > EMA50 (Haussier)' if analysis['ema_12'] > analysis['ema_50'] else 'EMA12 < EMA50 (Baissier)'}
- Bollinger Bands: ${analysis['bb_low']:.4f} - ${analysis['bb_high']:.4f}
- Volume: {analysis['volume']:.0f} (Moyenne: {analysis['volume_ma']:.0f})

SIGNAUX DÉTECTÉS:
{chr(10).join(['- ' + s for s in analysis['signals']])}

SIGNAL PROPOSÉ:
- Type: {signal['type']}
- Entrée: ${signal['entry']:.4f}
- Take Profit: ${signal['tp']:.4f} ({((signal['tp']-signal['entry'])/signal['entry']*100):.2f}%)
- Stop Loss: ${signal['sl']:.4f} ({((signal['sl']-signal['entry'])/signal['entry']*100):.2f}%)
- Risk/Reward: 1:{signal['risk_reward']:.2f}
- Score de confiance: {signal['confidence']}/100

Analyse ce signal et réponds en format JSON avec cette structure:
{{
  "valid": true/false,
  "confidence_adjusted": 0-100,
  "analysis": "ton analyse détaillée en 2-3 phrases",
  "recommendation": "STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL"
}}

Sois critique et objectif. Ne valide que les signaux vraiment solides."""

        try:
            response = self.mistral_client.chat.complete(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )

            content = response.choices[0].message.content

            # S'assurer que content est bien une string
            if content is None:
                return {"valid": False, "analysis": "Réponse LLM vide"}

            content_str = str(content)

            # Extraire le JSON de la réponse
            import re
            json_match = re.search(r'\{.*\}', content_str, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                return {"valid": False, "analysis": "Erreur de parsing de la réponse LLM"}

        except Exception as e:
            print(f"Erreur validation LLM: {e}")
            return {"valid": False, "analysis": f"Erreur: {str(e)}"}

    def send_pushover_notification(self, title, message, priority=1):
        """Envoie une notification via Pushover"""
        try:
            response = requests.post("https://api.pushover.net/1/messages.json", data={
                "token": config.PUSHOVER_APP_TOKEN,
                "user": config.PUSHOVER_USER_KEY,
                "title": title,
                "message": message,
                "priority": priority,
                "sound": "cosmic"
            })

            if response.status_code == 200:
                print(f"✓ Notification envoyée: {title}")
                return True
            else:
                print(f"✗ Erreur Pushover: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Erreur lors de l'envoi de la notification: {e}")
            return False

    def is_signal_already_active(self, symbol, signal_type):
        """Vérifie si un signal est déjà actif pour éviter les doublons"""
        signal_key = f"{symbol}_{signal_type}"

        if signal_key in self.active_signals:
            # Vérifier si le signal est encore récent (moins de 4 heures)
            last_time = datetime.fromisoformat(self.active_signals[signal_key])
            time_diff = (datetime.now() - last_time).total_seconds()

            if time_diff < 14400:  # 4 heures
                return True
            else:
                # Signal trop vieux, on peut en envoyer un nouveau
                del self.active_signals[signal_key]
                self.save_state()

        return False

    def mark_signal_as_sent(self, symbol, signal_type):
        """Marque un signal comme envoyé"""
        signal_key = f"{symbol}_{signal_type}"
        self.active_signals[signal_key] = datetime.now().isoformat()
        self.save_state()

    def analyze_and_alert(self):
        """Analyse toutes les cryptos et envoie des alertes si nécessaire"""
        print(f"\n{'='*70}")
        print(f"🔍 Scan du marché - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Afficher le statut du paper trading
        if self.paper_trading:
            stats = self.paper_trading.get_statistics()
            portfolio_value = stats.get('total_portfolio_value', stats['current_balance'])
            print(f"💰 Paper Trading: ${portfolio_value:.2f} (Libre: ${stats['current_balance']:.2f}) | ROI: {stats['roi']:.2f}% | Trades: {stats['total_trades']} | Win Rate: {stats['win_rate']:.1f}%")

        print(f"{'='*70}\n")

        for symbol in config.SYMBOLS:
            try:
                # Récupération et analyse
                df = self.get_ohlcv_data(symbol)
                df = self.calculate_indicators(df)
                analysis = analyze_crypto(df, symbol)

                # Mettre à jour les positions paper trading existantes
                if self.paper_trading:
                    current_price = analysis['price']
                    closed_count = self.paper_trading.update_positions(symbol, current_price)

                    # Si des positions ont été fermées, envoyer une notification
                    if closed_count > 0:
                        for position in self.paper_trading.closed_positions[-closed_count:]:
                            if position['symbol'] == symbol:
                                message = self.paper_trading.format_position_message(position, "CLOSED")
                                title = f"{'🟢' if position['pnl_usdt'] > 0 else '🔴'} Position fermée - {symbol}"
                                self.send_pushover_notification(title, message, priority=1)

                signal = self.generate_trading_signal(analysis)

                if signal:
                    # Vérifier si on a déjà envoyé ce signal récemment
                    if self.is_signal_already_active(symbol, signal['type']):
                        print(f"⏭️  {symbol}: Signal {signal['type']} déjà actif, ignoré")
                        continue

                    # Filtre haute confiance si activé
                    if config.NOTIFY_ON_HIGH_CONFIDENCE_ONLY and signal['confidence'] < 75:
                        print(f"⚠️  {symbol}: Signal {signal['type']} détecté mais confiance trop faible ({signal['confidence']}/100)")
                        continue

                    # Validation par le LLM
                    print(f"🤖 Validation LLM du signal {signal['type']} pour {symbol}...")
                    llm_validation = self.validate_signal_with_llm(analysis, signal)

                    if llm_validation.get('valid', False):
                        # Vérifier les horaires de trading avant d'envoyer
                        if not self.is_trading_hours():
                            print(f"⏰ {symbol}: Signal {signal['type']} validé mais hors horaires de trading (Lun-Ven 9h-20h)")
                            continue

                        # Ouvrir une position paper trading si activé
                        position_opened = False
                        if self.paper_trading:
                            position, msg = self.paper_trading.open_position(signal, analysis)
                            if position:
                                print(f"📊 {symbol}: Position paper trading ouverte - ${position['size_usdt']:.2f}")
                                # Envoyer notification de position ouverte
                                pt_message = self.paper_trading.format_position_message(position, "OPENED")
                                pt_title = f"📊 PAPER - {signal['type']} {symbol}"
                                self.send_pushover_notification(pt_title, pt_message, priority=1)
                                self.mark_signal_as_sent(symbol, signal['type'])
                                print(f"✅ {symbol}: Position ouverte et alerte envoyée!")
                                position_opened = True
                            else:
                                print(f"⚠️  {symbol}: Impossible d'ouvrir position paper trading - {msg}")
                                print(f"   Notification non envoyée car position non ouverte")

                        # Signal validé, envoi de l'alerte (seulement si paper trading désactivé)
                        if not self.paper_trading and not position_opened:
                            message = f"""
{signal['type']} sur {symbol}

Prix: ${signal['entry']:.4f}
TP: ${signal['tp']:.4f} ({((signal['tp']-signal['entry'])/signal['entry']*100):.2f}%)
SL: ${signal['sl']:.4f} ({((signal['sl']-signal['entry'])/signal['entry']*100):.2f}%)

Risk/Reward: 1:{signal['risk_reward']:.2f}
Confiance: {signal['confidence']}/100
LLM: {llm_validation.get('recommendation', 'N/A')}

Analyse LLM:
{llm_validation.get('analysis', 'N/A')}

Tendance: {analysis['trend']}
RSI: {analysis['rsi']:.1f}
"""

                            title = f"🚀 {signal['type']} {symbol}"

                            if self.send_pushover_notification(title, message, priority=1):
                                self.mark_signal_as_sent(symbol, signal['type'])
                                print(f"✅ {symbol}: Alerte {signal['type']} envoyée!")
                    else:
                        print(f"❌ {symbol}: Signal {signal['type']} rejeté par le LLM")
                        print(f"   Raison: {llm_validation.get('analysis', 'N/A')}")
                else:
                    print(f"⏸️  {symbol}: Pas de signal (Score: {analysis['score']}/100)")

            except Exception as e:
                print(f"❌ Erreur pour {symbol}: {e}")

        print(f"\n{'='*70}")
        print(f"⏰ Prochain scan dans {config.CHECK_INTERVAL // 60} minutes")
        print(f"{'='*70}\n")

    def run(self):
        """Lance l'agent en mode continu"""
        print("\n" + "="*70)
        print("🤖 AGENT DE TRADING AUTONOME - DÉMARRÉ")
        print("="*70)
        print(f"Cryptos surveillées: {', '.join(config.SYMBOLS)}")
        print(f"Timeframe: {config.TIMEFRAME}")
        print(f"Intervalle d'analyse: {config.CHECK_INTERVAL // 60} minutes")
        print(f"Score minimum: {config.MIN_CONFIDENCE_SCORE}/100")
        print(f"Risk/Reward minimum: 1:{config.MIN_RISK_REWARD}")
        print("="*70 + "\n")

        # Envoyer une notification de démarrage
        self.send_pushover_notification(
            "🤖 Agent de Trading",
            "L'agent de trading autonome est maintenant actif et surveille le marché.",
            priority=0
        )

        try:
            while True:
                self.analyze_and_alert()
                time.sleep(config.CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\n\n🛑 Arrêt de l'agent...")
            self.send_pushover_notification(
                "🛑 Agent de Trading",
                "L'agent de trading a été arrêté.",
                priority=0
            )

def analyze_crypto(df, symbol):
    """Fonction standalone pour l'analyse (utilisée par l'agent)"""
    last = df.iloc[-1]
    prev = df.iloc[-2]
    price = last['close']

    trend = "NEUTRE"
    if price > last['MA_21'] and price > last['MA_50']:
        trend = "HAUSSIERE"
    elif price < last['MA_21'] and price < last['MA_50']:
        trend = "BAISSIERE"

    score = 0
    signals = []

    if 30 <= last['RSI'] <= 70:
        score += 20
        if last['RSI'] > 50:
            signals.append(f"RSI haussier ({last['RSI']:.1f})")
        else:
            signals.append(f"RSI baissier ({last['RSI']:.1f})")
    elif last['RSI'] < 30:
        score += 30
        signals.append(f"RSI SURVENDU ({last['RSI']:.1f})")
    elif last['RSI'] > 70:
        score += 30
        signals.append(f"RSI SURACHETÉ ({last['RSI']:.1f})")

    if last['MACD'] > last['MACD_Signal']:
        score += 15
        signals.append("MACD haussier")
    else:
        score += 15
        signals.append("MACD baissier")

    if prev['MACD'] <= prev['MACD_Signal'] and last['MACD'] > last['MACD_Signal']:
        score += 25
        signals.append("CROISEMENT MACD HAUSSIER")
    elif prev['MACD'] >= prev['MACD_Signal'] and last['MACD'] < last['MACD_Signal']:
        score += 25
        signals.append("CROISEMENT MACD BAISSIER")
    else:
        score += 10

    if price <= last['BB_Low']:
        score += 20
        signals.append("Support Bollinger")
    elif price >= last['BB_High']:
        score += 20
        signals.append("Résistance Bollinger")
    else:
        score += 10

    if price > last['MA_9'] and last['MA_9'] > last['MA_21']:
        score += 15
        signals.append("Tendance MA haussière")
    elif price < last['MA_9'] and last['MA_9'] < last['MA_21']:
        score += 15
        signals.append("Tendance MA baissière")
    else:
        score += 5

    if last['volume'] > last['Volume_MA'] * 1.5:
        score += 15
        signals.append("Volume élevé")
    else:
        score += 5

    return {
        'symbol': symbol,
        'price': price,
        'trend': trend,
        'score': min(score, 100),
        'rsi': last['RSI'],
        'macd': last['MACD'],
        'macd_signal': last['MACD_Signal'],
        'ma_21': last['MA_21'],
        'ma_50': last['MA_50'],
        'ema_12': last['EMA_12'],
        'ema_50': last['EMA_50'],
        'ema_12_prev': prev['EMA_12'],
        'ema_50_prev': prev['EMA_50'],
        'bb_low': last['BB_Low'],
        'bb_high': last['BB_High'],
        'atr': last['ATR'],
        'volume': last['volume'],
        'volume_ma': last['Volume_MA'],
        'signals': signals
    }

if __name__ == "__main__":
    agent = TradingAgent()
    agent.run()
