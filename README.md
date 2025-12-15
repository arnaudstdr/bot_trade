# Agent de Trading Autonome avec Alertes IA

Agent de trading automatique qui surveille 5 cryptomonnaies en temps réel, détecte les opportunités de trading et envoie des alertes via Pushover après validation par Mistral AI.

## Fonctionnalités

- **Analyse technique complète**: RSI, MACD, Bollinger Bands, moyennes mobiles, ATR, volume
- **Détection automatique de signaux**: LONG et SHORT avec TP/SL calculés dynamiquement
- **Validation IA**: Chaque signal est analysé par Mistral AI avant envoi
- **Alertes mobiles**: Notifications Pushover instantanées
- **Anti-spam**: Système de gestion d'état pour éviter les doublons
- **Timeframe 5 minutes**: Optimisé pour le day trading

## Prérequis

### 1. Compte Pushover

1. Créez un compte sur [pushover.net](https://pushover.net/)
2. Installez l'app Pushover sur votre téléphone (iOS/Android)
3. Notez votre **User Key** (sur le dashboard)
4. Créez une nouvelle application et notez l'**App Token**

### 2. API Mistral

1. Créez un compte sur [console.mistral.ai](https://console.mistral.ai/)
2. Créez une API key
3. Ajoutez des crédits (environ 5-10€ pour commencer)

## Installation

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Configurer les clés API

Éditez le fichier `config.py` et ajoutez vos clés:

```python
PUSHOVER_USER_KEY = "votre_user_key"
PUSHOVER_APP_TOKEN = "votre_app_token"
MISTRAL_API_KEY = "votre_api_key_mistral"
```

### 3. Configurer les paramètres (optionnel)

Dans `config.py`, vous pouvez ajuster:

```python
TIMEFRAME = "5m"  # Timeframe d'analyse
CHECK_INTERVAL = 300  # Intervalle entre analyses (secondes)
SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT']
MIN_CONFIDENCE_SCORE = 65  # Score minimum pour signal
MIN_RISK_REWARD = 1.5  # Ratio R/R minimum
NOTIFY_ON_HIGH_CONFIDENCE_ONLY = True  # Seulement signaux haute confiance (≥75)
```

## Utilisation

### Mode autonome (recommandé)

Lance l'agent qui tourne en continu:

```bash
python3 agent.py
```

L'agent va:
- Analyser les 5 cryptos toutes les 5 minutes
- Détecter les signaux de trading
- Les valider avec Mistral AI
- Envoyer une notification Pushover si le signal est validé

Pour arrêter: `Ctrl+C`

### Analyse ponctuelle

Pour une analyse unique sans monitoring continu:

```bash
python3 main.py
```

Cela affiche un rapport complet dans le terminal.

## Déploiement avec Docker (Recommandé pour Raspberry Pi)

### Avantages de Docker

- Environnement isolé et reproductible
- Pas de conflits de dépendances
- Redémarrage automatique en cas de crash
- Facile à déployer sur Raspberry Pi
- Gestion automatique des ressources

### Construction de l'image

```bash
docker build -t trading-agent .
```

### Lancement avec Docker Compose (Recommandé)

```bash
# Démarrer l'agent
docker-compose up -d

# Voir les logs en temps réel
docker-compose logs -f

# Arrêter l'agent
docker-compose down

# Redémarrer l'agent
docker-compose restart
```

### Lancement avec Docker directement

```bash
# Créer un volume pour les données persistantes
docker volume create trading-data

# Lancer l'agent
docker run -d \
  --name trading-agent \
  --restart unless-stopped \
  -v $(pwd)/config.py:/app/config.py:ro \
  -v trading-data:/app/data \
  -v $(pwd)/logs:/app/logs \
  trading-agent

# Voir les logs
docker logs -f trading-agent

# Arrêter l'agent
docker stop trading-agent

# Redémarrer l'agent
docker start trading-agent
```

### Sur Raspberry Pi

Le Dockerfile est optimisé pour ARM. Sur votre Raspberry Pi:

```bash
# Cloner ou copier le projet
cd bot_trade

# S'assurer que config.py est configuré avec vos clés API

# Builder l'image (peut prendre 5-10 min sur RPi)
docker-compose build

# Lancer l'agent
docker-compose up -d

# Vérifier que ça tourne
docker-compose ps

# Voir les logs
docker-compose logs -f
```

L'agent redémarrera automatiquement:
- Après un reboot du Raspberry Pi
- En cas de crash
- Si le conteneur s'arrête

### Gestion des logs Docker

Les logs sont automatiquement limités:
- Taille max par fichier: 10 MB
- Nombre de fichiers: 3
- Total max: 30 MB

Pour voir les logs:
```bash
docker-compose logs -f --tail=100
```

### Mise à jour de l'agent

```bash
# Arrêter l'agent
docker-compose down

# Récupérer les nouvelles modifications
git pull  # ou copier les nouveaux fichiers

# Rebuilder l'image
docker-compose build

# Redémarrer
docker-compose up -d
```

## Lancer l'agent en arrière-plan (sans Docker)

### Sur Linux/Mac

```bash
nohup python3 agent.py > agent.log 2>&1 &
```

Pour voir les logs en temps réel:
```bash
tail -f agent.log
```

Pour arrêter:
```bash
pkill -f agent.py
```

### Avec screen

```bash
screen -S trading_agent
python3 agent.py
# Détacher: Ctrl+A puis D
```

Pour revenir:
```bash
screen -r trading_agent
```

### Avec systemd (Linux)

Créez `/etc/systemd/system/trading-agent.service`:

```ini
[Unit]
Description=Trading Agent
After=network.target

[Service]
Type=simple
User=votre_user
WorkingDirectory=/home/arnaud.stadler/projets/divers/bot_trade
ExecStart=/usr/bin/python3 /home/arnaud.stadler/projets/divers/bot_trade/agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Puis:
```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-agent
sudo systemctl start trading-agent
sudo systemctl status trading-agent
```

## Structure du projet

```
bot_trade/
├── agent.py              # Agent autonome principal
├── main.py              # Script d'analyse ponctuelle
├── config.py            # Configuration et clés API
├── requirements.txt     # Dépendances Python
├── signals_state.json   # État des signaux (créé automatiquement)
└── README.md           # Ce fichier
```

## Notifications Pushover

Vous recevrez des notifications avec:
- Direction du signal (LONG/SHORT)
- Prix d'entrée, TP, SL avec pourcentages
- Ratio Risk/Reward
- Score de confiance
- Recommandation du LLM
- Analyse détaillée du LLM
- Indicateurs techniques (tendance, RSI)

## Personnalisation

### Ajouter d'autres cryptos

Dans `config.py`:
```python
SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'DOGE/USDT', 'MATIC/USDT']
```

### Changer le timeframe

```python
TIMEFRAME = "15m"  # 1m, 5m, 15m, 30m, 1h, 4h, 1d
```

### Ajuster les critères de signal

Dans `agent.py`, modifiez les conditions dans `generate_trading_signal()`:
- `long_conditions`: Critères pour signal LONG
- `short_conditions`: Critères pour signal SHORT

### Modifier les TP/SL

Dans `agent.py`, ligne ~247:
```python
atr_multiplier_tp = 2.5  # Multiplicateur pour Take Profit
atr_multiplier_sl = 1.5  # Multiplicateur pour Stop Loss
```

## Sécurité

- **Ne commitez JAMAIS config.py avec vos vraies clés API**
- Ajoutez `config.py` à `.gitignore`
- Gardez vos clés API secrètes
- Utilisez des clés API avec permissions limitées si possible

## Coûts

- **Pushover**: 5$ unique (achat de l'app)
- **Mistral API**: ~0.002$ par validation (environ 0.50€/jour si 250 analyses)
- **Binance API**: Gratuit

## Dépannage

### Erreur "MACD_12_26_9"
Vérifiez que `ta` est bien installé: `pip install --upgrade ta`

### Pas de notification Pushover
- Vérifiez vos clés dans `config.py`
- Testez manuellement: `python3 -c "import config; import requests; print(requests.post('https://api.pushover.net/1/messages.json', data={'token': config.PUSHOVER_APP_TOKEN, 'user': config.PUSHOVER_USER_KEY, 'message': 'Test'}).text)"`

### Erreur Mistral API
- Vérifiez votre clé API
- Vérifiez que vous avez des crédits
- Testez: `python3 -c "from mistralai import Mistral; import config; client = Mistral(api_key=config.MISTRAL_API_KEY); print('OK')"`

## Avertissement

Cet outil est fourni à des fins éducatives. Le trading de cryptomonnaies comporte des risques importants. Ne tradez jamais avec de l'argent que vous ne pouvez pas vous permettre de perdre. Les signaux générés ne constituent pas des conseils financiers.

## Support

Pour toute question ou bug, créez une issue sur le repo GitHub.

## Licence

MIT
