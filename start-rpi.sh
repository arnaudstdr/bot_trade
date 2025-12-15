#!/bin/bash
# Script de démarrage rapide pour Raspberry Pi

echo "=================================="
echo "Agent de Trading - Raspberry Pi"
echo "=================================="
echo ""

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé."
    echo "Installation: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Vérifier que docker-compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé."
    echo "Installation: sudo pip3 install docker-compose"
    exit 1
fi

# Vérifier que config.py existe
if [ ! -f "config.py" ]; then
    echo "❌ config.py n'existe pas."
    echo "Copiez config.example.py vers config.py et remplissez vos clés API."
    exit 1
fi

# Vérifier que les clés API sont configurées
if grep -q "votre_.*_ici" config.py; then
    echo "⚠️  ATTENTION: config.py contient encore des valeurs par défaut."
    echo "Assurez-vous d'avoir configuré vos clés API Pushover et Mistral."
    read -p "Continuer quand même ? (o/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Oo]$ ]]; then
        exit 1
    fi
fi

echo "✓ Vérifications OK"
echo ""

# Afficher le menu
echo "Que voulez-vous faire ?"
echo "1) Builder et démarrer l'agent"
echo "2) Démarrer l'agent (si déjà buildé)"
echo "3) Voir les logs"
echo "4) Arrêter l'agent"
echo "5) Redémarrer l'agent"
echo "6) Voir le statut"
echo "0) Quitter"
echo ""

read -p "Votre choix: " choice

case $choice in
    1)
        echo "🔨 Build de l'image..."
        docker-compose build
        echo "🚀 Démarrage de l'agent..."
        docker-compose up -d
        echo "✅ Agent démarré !"
        echo "Utilisez: docker-compose logs -f"
        ;;
    2)
        echo "🚀 Démarrage de l'agent..."
        docker-compose up -d
        echo "✅ Agent démarré !"
        ;;
    3)
        echo "📋 Logs (Ctrl+C pour quitter):"
        docker-compose logs -f --tail=50
        ;;
    4)
        echo "🛑 Arrêt de l'agent..."
        docker-compose down
        echo "✅ Agent arrêté"
        ;;
    5)
        echo "🔄 Redémarrage de l'agent..."
        docker-compose restart
        echo "✅ Agent redémarré"
        ;;
    6)
        echo "📊 Statut:"
        docker-compose ps
        ;;
    0)
        echo "Au revoir !"
        exit 0
        ;;
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac
