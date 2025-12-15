# Guide de déploiement sur Raspberry Pi

Ce guide vous aide à déployer l'agent de trading sur votre Raspberry Pi avec Docker.

## Prérequis

### Matériel recommandé
- Raspberry Pi 3B+ ou supérieur (4 ou 5 recommandé)
- Carte SD 16 GB minimum (32 GB recommandé)
- Connexion internet stable

### Système d'exploitation
- Raspberry Pi OS (64-bit recommandé)
- OU Ubuntu Server pour Raspberry Pi

## Installation rapide

### 1. Installer Docker

Si Docker n'est pas déjà installé:

```bash
# Installation automatique
curl -fsSL https://get.docker.com | sh

# Ajouter votre utilisateur au groupe docker
sudo usermod -aG docker $USER

# Redémarrer la session (ou reboot)
newgrp docker
```

### 2. Installer Docker Compose

```bash
sudo pip3 install docker-compose
```

### 3. Transférer le projet sur le Raspberry Pi

#### Option A: Via Git (si le projet est sur GitHub)
```bash
git clone https://github.com/votre-repo/bot_trade.git
cd bot_trade
```

#### Option B: Via SCP depuis votre ordinateur
```bash
# Depuis votre ordinateur
scp -r bot_trade/ pi@raspberrypi.local:~/
```

#### Option C: Via rsync (recommandé)
```bash
# Depuis votre ordinateur
rsync -avz --exclude '.git' --exclude 'venv' bot_trade/ pi@raspberrypi.local:~/bot_trade/
```

### 4. Configurer les clés API

```bash
cd bot_trade

# Copier le fichier de config example
cp config.example.py config.py

# Éditer avec nano
nano config.py

# Remplir vos clés:
# - PUSHOVER_USER_KEY
# - PUSHOVER_APP_TOKEN
# - MISTRAL_API_KEY

# Sauvegarder: Ctrl+O puis Enter
# Quitter: Ctrl+X
```

### 5. Lancer l'agent

#### Méthode facile avec le script interactif:
```bash
./start-rpi.sh
```

Choisissez l'option 1 pour builder et démarrer.

#### Méthode manuelle:
```bash
# Builder l'image (5-10 min sur RPi)
docker-compose build

# Démarrer l'agent
docker-compose up -d

# Voir les logs
docker-compose logs -f
```

## Gestion de l'agent

### Commandes utiles

```bash
# Voir le statut
docker-compose ps

# Voir les logs en temps réel
docker-compose logs -f

# Voir les dernières 100 lignes de logs
docker-compose logs --tail=100

# Arrêter l'agent
docker-compose down

# Redémarrer l'agent
docker-compose restart

# Voir l'utilisation des ressources
docker stats trading-agent
```

### Mise à jour

```bash
cd bot_trade

# Récupérer les modifications
git pull  # ou transférer les nouveaux fichiers

# Rebuilder l'image
docker-compose build

# Redémarrer avec la nouvelle version
docker-compose up -d
```

## Optimisation pour Raspberry Pi

### Limiter l'utilisation de la mémoire

Le docker-compose.yml est déjà configuré avec:
- Limite mémoire: 512 MB
- Limite CPU: 1 cœur
- Logs limités: 30 MB max

### Vérifier la température

```bash
# Voir la température du CPU
vcgencmd measure_temp

# Monitoring continu
watch -n 2 vcgencmd measure_temp
```

Si la température dépasse 70°C régulièrement, ajoutez un ventilateur ou un dissipateur.

### Rotation des logs

Les logs Docker sont automatiquement limités, mais pour les logs applicatifs:

```bash
# Créer un dossier logs si nécessaire
mkdir -p logs

# Les logs seront automatiquement gérés par Docker
```

## Démarrage automatique au boot

L'agent redémarrera automatiquement grâce à `restart: unless-stopped` dans docker-compose.yml.

Pour vérifier:
```bash
# Redémarrer le Raspberry Pi
sudo reboot

# Après le redémarrage, vérifier que l'agent tourne
docker-compose ps
```

## Surveillance et monitoring

### Créer un script de surveillance

Créez `monitor.sh`:

```bash
#!/bin/bash
# Envoie une alerte si l'agent ne tourne pas

if ! docker ps | grep -q trading-agent; then
    echo "⚠️ Agent de trading arrêté ! Redémarrage..."
    cd ~/bot_trade
    docker-compose up -d
fi
```

Rendez-le exécutable:
```bash
chmod +x monitor.sh
```

Ajoutez-le à cron pour vérifier toutes les 10 minutes:
```bash
crontab -e

# Ajouter cette ligne:
*/10 * * * * /home/pi/bot_trade/monitor.sh
```

### Surveiller les ressources

```bash
# Installer htop si nécessaire
sudo apt install htop

# Lancer htop
htop
```

## Dépannage

### L'image ne se build pas

```bash
# Vérifier l'espace disque
df -h

# Nettoyer les images Docker inutiles
docker system prune -a
```

### L'agent crash au démarrage

```bash
# Voir les logs d'erreur
docker-compose logs --tail=50

# Vérifier que config.py est correct
cat config.py | grep -i key
```

### Problème de mémoire

```bash
# Voir l'utilisation mémoire
free -h

# Réduire la limite mémoire dans docker-compose.yml
# mem_limit: 256m  # au lieu de 512m
```

### L'agent ne reçoit pas les données de Binance

```bash
# Vérifier la connexion internet
ping -c 4 binance.com

# Tester dans le conteneur
docker exec trading-agent ping -c 4 binance.com
```

## Performance attendue sur Raspberry Pi

### Raspberry Pi 3B+
- Build: ~10-15 minutes
- Utilisation CPU: 5-15%
- Utilisation RAM: 150-250 MB

### Raspberry Pi 4 (4GB)
- Build: ~5-8 minutes
- Utilisation CPU: 3-10%
- Utilisation RAM: 150-250 MB

### Raspberry Pi 5
- Build: ~3-5 minutes
- Utilisation CPU: 2-8%
- Utilisation RAM: 150-250 MB

## Sécurité

### Protéger config.py

```bash
# Permissions strictes
chmod 600 config.py
```

### Firewall (optionnel)

```bash
# Installer UFW
sudo apt install ufw

# Autoriser SSH
sudo ufw allow ssh

# Activer le firewall
sudo ufw enable
```

### Mises à jour système

```bash
# Mettre à jour le système régulièrement
sudo apt update && sudo apt upgrade -y
```

## Support

Pour toute question ou problème, consultez le README.md principal ou créez une issue.

## Checklist de déploiement

- [ ] Docker et Docker Compose installés
- [ ] Projet transféré sur le Raspberry Pi
- [ ] config.py configuré avec les bonnes clés API
- [ ] Image Docker buildée avec succès
- [ ] Agent démarré avec `docker-compose up -d`
- [ ] Logs vérifiés avec `docker-compose logs -f`
- [ ] Notification de test reçue sur Pushover
- [ ] Température CPU vérifiée (<70°C)
- [ ] Redémarrage automatique testé

Une fois tous ces points validés, votre agent de trading est prêt !
