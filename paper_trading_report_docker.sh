#!/bin/bash
# Script pour voir le rapport de paper trading depuis Docker

# Copier le fichier depuis le conteneur
echo "📊 Récupération des données depuis Docker..."
docker cp trading-agent:/app/data/paper_trading_history.json /tmp/paper_trading_history.json 2>/dev/null

# Si le fichier existe, créer un lien temporaire
if [ -f /tmp/paper_trading_history.json ]; then
    # Copier temporairement dans le répertoire courant
    cp /tmp/paper_trading_history.json ./paper_trading_history.json

    # Lancer le rapport
    python3 paper_trading_report.py "$@"

    # Nettoyer
    rm -f ./paper_trading_history.json /tmp/paper_trading_history.json
else
    echo "❌ Aucune donnée de paper trading trouvée dans Docker"
    echo "L'agent est-il en cours d'exécution ?"
fi
