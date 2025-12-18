# 🐳 Déploiement Docker avec Interface Web

Guide pour déployer le bot de trading et son interface web avec Docker.

## 📋 Prérequis

- Docker et Docker Compose installés
- Fichier `config.py` configuré avec vos clés API

## 🚀 Démarrage Rapide

### Lancer les deux services (agent + interface web)

```bash
docker-compose up -d
```

Cette commande démarre :
- **trading-agent** : Le bot de trading qui analyse et trade
- **web-interface** : L'interface web accessible sur http://localhost:5005

### Vérifier que tout fonctionne

```bash
docker-compose ps
```

Vous devriez voir :
```
NAME            STATUS          PORTS
trading-agent   Up
trading-web     Up              0.0.0.0:5005->5005/tcp
```

## 🌐 Accès à l'Interface Web

- **Local** : http://localhost:5005
- **Réseau** : http://[IP_SERVEUR]:5005

## 📊 Commandes Utiles

### Voir les logs

```bash
# Logs de l'agent de trading
docker-compose logs -f trading-agent

# Logs de l'interface web
docker-compose logs -f web-interface

# Tous les logs
docker-compose logs -f
```

### Redémarrer un service

```bash
# Redémarrer l'agent
docker-compose restart trading-agent

# Redémarrer l'interface web
docker-compose restart web-interface
```

### Arrêter les services

```bash
# Arrêter sans supprimer
docker-compose stop

# Arrêter et supprimer les conteneurs
docker-compose down
```

### Reconstruire après modification

```bash
# Reconstruire les images
docker-compose build

# Reconstruire et redémarrer
docker-compose up -d --build
```

## 🎛️ Lancer uniquement certains services

### Uniquement l'agent (sans interface web)

```bash
docker-compose up -d trading-agent
```

### Uniquement l'interface web

```bash
docker-compose up -d web-interface
```

## 📁 Volumes et Données

Les données sont partagées entre l'agent et l'interface web via des volumes :

```
./data        -> /app/data    (données du paper trading, logs)
./config.py   -> /app/config.py  (configuration)
./templates   -> /app/templates  (interface web)
./static      -> /app/static     (interface web)
```

Les modifications dans `./data` sont visibles par les deux conteneurs en temps réel.

## 🔧 Configuration des Ressources

### Limites actuelles (optimisé Raspberry Pi)

**Agent de trading :**
- Mémoire : 512 MB
- CPU : 1.0 core

**Interface web :**
- Mémoire : 256 MB
- CPU : 0.5 core

### Modifier les limites

Éditez `docker-compose.yml` :

```yaml
services:
  trading-agent:
    mem_limit: 1g      # Augmenter à 1 GB
    cpus: 2.0          # Utiliser 2 cores
```

## 🐛 Dépannage

### L'interface web ne démarre pas

```bash
# Vérifier les logs
docker-compose logs web-interface

# Vérifier que le port 5005 n'est pas utilisé
sudo lsof -i :5005

# Redémarrer
docker-compose restart web-interface
```

### Les données ne s'affichent pas

```bash
# Vérifier que le répertoire data existe
ls -la ./data

# Vérifier les permissions
sudo chown -R 1000:1000 ./data

# Redémarrer les services
docker-compose restart
```

### L'agent ne se connecte pas aux APIs

```bash
# Vérifier la configuration
cat config.py

# Vérifier les logs de l'agent
docker-compose logs trading-agent | grep -i error

# Tester la connectivité
docker-compose exec trading-agent ping api.binance.com
```

### Erreur "Cannot connect to Docker daemon"

```bash
# Démarrer Docker
sudo systemctl start docker

# Vérifier le statut
sudo systemctl status docker
```

## 🔄 Mise à jour

Pour mettre à jour le bot après avoir récupéré de nouvelles modifications :

```bash
# Arrêter les services
docker-compose down

# Reconstruire les images
docker-compose build --no-cache

# Redémarrer
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

## 🔐 Sécurité

### Exposition sur Internet

⚠️ **Par défaut, l'interface web écoute sur `0.0.0.0:5005`**, ce qui la rend accessible depuis le réseau local.

**Pour exposer sur Internet de manière sécurisée :**

1. **Utiliser un reverse proxy (recommandé)**

Exemple avec Nginx + Let's Encrypt :

```nginx
server {
    listen 443 ssl;
    server_name trading.mondomaine.com;

    ssl_certificate /etc/letsencrypt/live/mondomaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mondomaine.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

2. **Utiliser un VPN (Tailscale, WireGuard)**

Plus simple et plus sécurisé pour un accès personnel.

3. **Ajouter une authentification**

L'interface n'a pas d'authentification par défaut. Ajoutez-en une avant l'exposition publique.

## 📈 Monitoring

### Surveiller l'utilisation des ressources

```bash
# Stats en temps réel
docker stats

# Utilisation disque
docker system df

# Informations détaillées
docker-compose ps
docker inspect trading-agent
docker inspect trading-web
```

### Logs persistants

Les logs sont automatiquement rotatés :
- Taille max : 10 MB par fichier
- Nombre de fichiers : 3
- Total par conteneur : ~30 MB

## 🎯 Bonnes Pratiques

1. **Sauvegardez régulièrement `./data`**
   ```bash
   tar -czf backup-$(date +%Y%m%d).tar.gz data/
   ```

2. **Surveillez les logs**
   ```bash
   docker-compose logs -f --tail=100
   ```

3. **Mettez à jour régulièrement**
   ```bash
   git pull
   docker-compose up -d --build
   ```

4. **Testez en local avant de déployer**
   ```bash
   docker-compose -f docker-compose.yml up
   ```

## 🚀 Déploiement Raspberry Pi

Le docker-compose est optimisé pour Raspberry Pi avec des limites de ressources adaptées.

### Vérifier la compatibilité

```bash
# Architecture
uname -m  # devrait afficher: aarch64 ou armv7l

# Version Docker
docker --version

# Mémoire disponible
free -h
```

### Optimisations Raspberry Pi

1. **Utilisez un SSD externe** plutôt qu'une carte SD pour les données
2. **Montez le répertoire data sur le SSD**
3. **Augmentez le swap** si vous avez moins de 2 GB de RAM

```bash
# Vérifier le swap
free -h

# Augmenter le swap (temporaire)
sudo swapoff -a
sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📞 Support

En cas de problème :

1. Consultez les logs : `docker-compose logs`
2. Vérifiez la configuration : `cat config.py`
3. Redémarrez les services : `docker-compose restart`
4. Reconstruisez si nécessaire : `docker-compose up -d --build`

Bon trading ! 🚀📈
