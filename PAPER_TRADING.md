# Paper Trading - Mode Simulation

Le mode Paper Trading vous permet de tester votre stratégie de trading **sans risque financier**.

## Fonctionnalités

- **Simulation réaliste** : Positions ouvertes/fermées avec TP/SL automatiques
- **Gestion du capital** : Balance virtuelle, taille de position configurable
- **Statistiques complètes** : Win rate, P&L, analyse par symbole
- **Notifications Pushover** : Reçois des alertes comme en trading réel
- **Historique persistant** : Toutes les positions sont sauvegardées

## Configuration

Dans `config.py`:

```python
# Paper Trading (Mode simulation)
PAPER_TRADING_ENABLED = True  # Activer le trading simulé
PAPER_TRADING_INITIAL_BALANCE = 1000  # Capital de départ en USDT
PAPER_TRADING_POSITION_SIZE_PERCENT = 2  # % du capital par trade (2%)
PAPER_TRADING_MAX_POSITIONS = 3  # Nombre max de positions simultanées
PAPER_TRADING_TRACK_FILE = "paper_trading_history.json"  # Fichier d'historique
```

## Utilisation

### Lancer l'agent avec Paper Trading

```bash
python3 agent.py
```

L'agent va :
1. Analyser les marchés toutes les 5 minutes
2. Détecter les signaux validés par l'IA
3. **Ouvrir automatiquement des positions virtuelles**
4. Surveiller les positions et fermer au TP/SL
5. Vous envoyer des notifications pour chaque trade

### Voir le rapport de performance

```bash
python3 paper_trading_report.py
```

Affiche :
- Balance actuelle et ROI
- Win rate et statistiques
- Positions ouvertes
- Historique des derniers trades
- Analyse par symbole

### Réinitialiser le Paper Trading

```bash
python3 paper_trading_report.py --reset
```

Remet tout à zéro (balance initiale, historique effacé).

## Comment ça marche

### 1. Ouverture de position

Quand un signal est validé :
- Calcul de la taille de position (ex: 2% de 1000$ = 20$)
- Ouverture d'une position virtuelle
- Notification Pushover envoyée

**Exemple de notification:**
```
📊 PAPER TRADING - Position ouverte

LONG sur BTC/USDT

Entrée: $89,303.72
TP: $89,912.59
SL: $88,938.68
Taille: $20.00 (0.000224 BTC)
R/R: 1:1.67

Balance: $980.00
Positions ouvertes: 1/3
```

### 2. Surveillance des positions

À chaque scan (toutes les 5 minutes) :
- Le prix actuel est récupéré
- Les positions sont mises à jour
- Si TP ou SL touché → position fermée automatiquement

### 3. Fermeture de position

Quand TP ou SL est touché :
- P&L calculé
- Balance mise à jour
- Notification envoyée

**Exemple de notification:**
```
🟢 PAPER TRADING - Position fermée

LONG sur BTC/USDT
Raison: TP_HIT

Entrée: $89,303.72
Sortie: $89,912.59
Durée: 2.5h

P&L: $0.68 (+3.41%)
Balance: $1,000.68 (ROI: +0.07%)

Total trades: 1
Win rate: 100.0%
```

## Exemple de rapport

```
================================================================================
📊 RAPPORT DE PERFORMANCE - PAPER TRADING
================================================================================

┌─ RÉSUMÉ GÉNÉRAL ──────────────────────────────────────────────────────────
│ Balance initiale:  $1000.00
│ Balance actuelle:  $1,045.30
│ ROI:              +4.53%
│ P&L Total:        $+45.30 (+4.53%)
│ Positions ouvertes: 1
└───────────────────────────────────────────────────────────────────────────

┌─ STATISTIQUES DE TRADING ─────────────────────────────────────────────────
│ Total trades:      15
│ Gagnants:         10 (66.7%)
│ Perdants:         5 (33.3%)
│ Gain moyen:       $8.20
│ Perte moyenne:    $-3.50
│ Meilleur trade:   $15.40
│ Pire trade:       $-7.20
│ Durée moyenne:    4.2h
└───────────────────────────────────────────────────────────────────────────

┌─ ANALYSE PAR SYMBOLE ─────────────────────────────────────────────────────
│ 🟢 BTC/USDT      Trades:  6 | Win Rate:  66.7% | P&L: $+25.30
│ 🟢 ETH/USDT      Trades:  5 | Win Rate:  60.0% | P&L: $+15.80
│ 🟢 SOL/USDT      Trades:  2 | Win Rate: 100.0% | P&L: $+8.50
│ 🔴 XRP/USDT      Trades:  2 | Win Rate:   0.0% | P&L: $-4.30
└───────────────────────────────────────────────────────────────────────────
```

## Avantages du Paper Trading

**Avant de trader en réel :**
1. **Tester la stratégie** : Voir si elle est profitable
2. **Affiner les paramètres** : Ajuster les seuils, TP/SL
3. **Comprendre le comportement** : Fréquence des trades, durée moyenne
4. **Sans risque** : Aucune perte réelle d'argent

**Durée recommandée :**
- Minimum **2 semaines** de paper trading
- Idéalement **1 mois**
- Objectif : **30+ trades** pour avoir des statistiques fiables

## Limites du Paper Trading

Le paper trading simule parfaitement les mécaniques mais :
- **Pas d'émotions** : En réel, la peur et l'avidité influencent
- **Exécution parfaite** : Pas de slippage, pas de frais
- **Pas de latence** : Les ordres sont instantanés

Même avec un bon paper trading, commencez en réel avec de **très petites sommes**.

## Passer au trading réel

Quand vous êtes satisfait des performances en paper trading :

1. **Vérifiez les stats** :
   - Win rate > 55%
   - ROI positif sur 30+ trades
   - Drawdown max acceptable

2. **Désactiver le paper trading** dans `config.py` :
   ```python
   PAPER_TRADING_ENABLED = False
   ```

3. **Commencer petit** :
   - 50-100€ maximum pour débuter
   - 0.5-1% par trade
   - Sur Binance Testnet d'abord si possible

## Conseils

- **Patience** : Laissez tourner plusieurs semaines
- **Ne pas tricher** : Ne modifiez pas les paramètres en cours de route
- **Analyser** : Regardez les trades perdants, apprenez
- **Itérer** : Si mauvais résultats, ajustez la stratégie et recommencez

## Support

Pour toute question sur le paper trading, consultez le README.md principal.
