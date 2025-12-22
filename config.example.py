# Configuration de l'agent de trading autonome
# Copiez ce fichier vers config.py et remplissez vos clés API

# Pushover - Pour les notifications
# Obtenez vos clés sur https://pushover.net/
PUSHOVER_USER_KEY = "votre_user_key_ici"
PUSHOVER_APP_TOKEN = "votre_app_token_ici"

# Mistral API - Pour la validation des signaux
# Obtenez votre clé sur https://console.mistral.ai/
MISTRAL_API_KEY = "votre_api_key_mistral_ici"

# Configuration de l'analyse
TIMEFRAME = "15m"  # Timeframe pour le day trading (1m, 5m, 15m, 30m, 1h, 4h, 1d)
CHECK_INTERVAL = 900  # Intervalle entre chaque analyse en secondes (900s = 15 min)

# Cryptomonnaies à surveiller
SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT']

# Paramètres de trading
MIN_CONFIDENCE_SCORE = 65  # Score minimum pour générer un signal (0-100)
MIN_RISK_REWARD = 1.5  # Ratio Risk/Reward minimum acceptable

# Options de notification
NOTIFY_ON_HIGH_CONFIDENCE_ONLY = True  # N'envoyer que les signaux haute confiance (score >= 75)

# Horaires de trading (heures locales)
TRADING_HOURS_ENABLED = True  # Activer/désactiver les restrictions d'horaires
TRADING_HOURS_START = 9   # Début des notifications à 9h
TRADING_HOURS_END = 20    # Fin des notifications à 20h
TRADING_ENABLED_DAYS = [0, 1, 2, 3, 4]  # Lun-Ven (0=Lundi, 6=Dimanche)

# Paper Trading (Mode simulation)
PAPER_TRADING_ENABLED = True  # Activer le trading simulé
PAPER_TRADING_INITIAL_BALANCE = 1000  # Capital de départ en USDT
PAPER_TRADING_POSITION_SIZE_PERCENT = 2  # % du capital par trade (2%)
PAPER_TRADING_MAX_POSITIONS = 3  # Nombre max de positions simultanées
PAPER_TRADING_TRACK_FILE = "data/paper_trading_history.json"  # Fichier d'historique

# Effet de levier (Futures)
PAPER_TRADING_LEVERAGE = 5  # Effet de levier (1 = pas de levier, 5 = 5x)
PAPER_TRADING_SIMULATE_LIQUIDATION = True  # Simuler les liquidations
PAPER_TRADING_LIQUIDATION_THRESHOLD = 0.8  # Seuil de liquidation (80% de perte sur la marge)

# Trailing Stop (Stop Loss suiveur)
PAPER_TRADING_TRAILING_STOP = True  # Activer le trailing stop
PAPER_TRADING_TRAILING_STOP_PERCENT = 1.5  # Distance du trailing stop en % du prix (1.5%)

# Take Profit fixe (remplace le trailing TP)
PAPER_TRADING_FIXED_TP = True  # Activer le take profit fixe
PAPER_TRADING_FIXED_TP_PERCENT = 2.0  # Take profit fixe en % du prix d'entrée (2%)

# Trailing Take Profit (TP suiveur) - Désactivé
PAPER_TRADING_TRAILING_TP = False  # Désactiver le trailing take profit
PAPER_TRADING_TRAILING_TP_PERCENT = 2.0  # Distance du trailing TP en % du prix (2%)
