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
TIMEFRAME = "5m"  # Timeframe pour le day trading (1m, 5m, 15m, 30m, 1h, 4h, 1d)
CHECK_INTERVAL = 300  # Intervalle entre chaque analyse en secondes (300s = 5 min)

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
