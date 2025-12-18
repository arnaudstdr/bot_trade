#!/usr/bin/env python3
"""
Interface Web pour le bot de trading
Accessible depuis n'importe quel navigateur sur le réseau
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
from paper_trading import PaperTradingManager
import config
import subprocess
import signal

app = Flask(__name__)

# Fichier pour stocker le PID du bot
BOT_PID_FILE = "data/bot.pid"
DATA_DIR = "data"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_paper_trading_data():
    """Récupère les données du paper trading"""
    try:
        pt = PaperTradingManager()
        stats = pt.get_statistics()

        return {
            'stats': stats,
            'open_positions': pt.open_positions,
            'closed_positions': pt.closed_positions[-20:]  # 20 derniers trades
        }
    except Exception as e:
        print(f"Erreur lors de la récupération des données: {e}")
        return {
            'stats': {},
            'open_positions': [],
            'closed_positions': []
        }

def is_bot_running():
    """Vérifie si le bot est en cours d'exécution"""
    if not os.path.exists(BOT_PID_FILE):
        return False

    try:
        with open(BOT_PID_FILE, 'r') as f:
            pid = int(f.read().strip())

        # Vérifier si le processus existe
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        # Le processus n'existe pas ou erreur de lecture
        if os.path.exists(BOT_PID_FILE):
            os.remove(BOT_PID_FILE)
        return False

def get_bot_status():
    """Récupère le statut du bot"""
    return {
        'running': is_bot_running(),
        'paper_trading_enabled': getattr(config, 'PAPER_TRADING_ENABLED', False),
        'symbols': config.SYMBOLS,
        'timeframe': config.TIMEFRAME,
        'check_interval': config.CHECK_INTERVAL // 60  # en minutes
    }

@app.route('/')
def index():
    """Page principale"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def api_stats():
    """API: Statistiques du paper trading"""
    data = get_paper_trading_data()
    return jsonify(data['stats'])

@app.route('/api/positions')
def api_positions():
    """API: Positions ouvertes et fermées"""
    data = get_paper_trading_data()
    return jsonify({
        'open': data['open_positions'],
        'closed': data['closed_positions']
    })

@app.route('/api/bot/status')
def api_bot_status():
    """API: Statut du bot"""
    return jsonify(get_bot_status())

@app.route('/api/bot/start', methods=['POST'])
def api_bot_start():
    """API: Démarrer le bot"""
    if is_bot_running():
        return jsonify({'success': False, 'message': 'Le bot est déjà en cours d\'exécution'})

    try:
        # Démarrer le bot en arrière-plan
        process = subprocess.Popen(
            ['python3', 'agent.py'],
            stdout=open('data/bot.log', 'a'),
            stderr=subprocess.STDOUT,
            preexec_fn=os.setpgrp
        )

        # Sauvegarder le PID
        with open(BOT_PID_FILE, 'w') as f:
            f.write(str(process.pid))

        return jsonify({'success': True, 'message': 'Bot démarré avec succès'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/api/bot/stop', methods=['POST'])
def api_bot_stop():
    """API: Arrêter le bot"""
    if not is_bot_running():
        return jsonify({'success': False, 'message': 'Le bot n\'est pas en cours d\'exécution'})

    try:
        with open(BOT_PID_FILE, 'r') as f:
            pid = int(f.read().strip())

        # Envoyer SIGTERM pour un arrêt propre
        os.killpg(os.getpgid(pid), signal.SIGTERM)

        # Supprimer le fichier PID
        if os.path.exists(BOT_PID_FILE):
            os.remove(BOT_PID_FILE)

        return jsonify({'success': True, 'message': 'Bot arrêté avec succès'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/api/config')
def api_config():
    """API: Configuration actuelle"""
    return jsonify({
        'symbols': config.SYMBOLS,
        'timeframe': config.TIMEFRAME,
        'check_interval': config.CHECK_INTERVAL // 60,
        'min_confidence_score': config.MIN_CONFIDENCE_SCORE,
        'min_risk_reward': config.MIN_RISK_REWARD,
        'paper_trading': {
            'enabled': getattr(config, 'PAPER_TRADING_ENABLED', False),
            'initial_balance': getattr(config, 'PAPER_TRADING_INITIAL_BALANCE', 1000),
            'position_size_percent': getattr(config, 'PAPER_TRADING_POSITION_SIZE_PERCENT', 2),
            'max_positions': getattr(config, 'PAPER_TRADING_MAX_POSITIONS', 3),
            'leverage': getattr(config, 'PAPER_TRADING_LEVERAGE', 1),
            'trailing_stop': getattr(config, 'PAPER_TRADING_TRAILING_STOP', False),
            'trailing_tp': getattr(config, 'PAPER_TRADING_TRAILING_TP', False)
        },
        'trading_hours': {
            'enabled': config.TRADING_HOURS_ENABLED,
            'start': config.TRADING_HOURS_START,
            'end': config.TRADING_HOURS_END,
            'days': config.TRADING_ENABLED_DAYS
        }
    })

@app.route('/api/logs')
def api_logs():
    """API: Dernières lignes du log"""
    try:
        if os.path.exists('data/bot.log'):
            with open('data/bot.log', 'r') as f:
                lines = f.readlines()
                return jsonify({'logs': lines[-100:]})  # 100 dernières lignes
        else:
            return jsonify({'logs': []})
    except Exception as e:
        return jsonify({'logs': [f'Erreur de lecture du log: {str(e)}']})

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🌐 INTERFACE WEB DU BOT DE TRADING")
    print("="*70)
    print("Accès local: http://localhost:5005")
    print("Accès réseau: http://[IP_RASPBERRY]:5005")
    print("\nPour trouver l'IP du Raspberry: hostname -I")
    print("="*70 + "\n")

    # Démarrer le serveur accessible depuis le réseau
    app.run(host='0.0.0.0', port=5005, debug=False)
