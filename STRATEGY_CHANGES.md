## Résumé des changements de stratégie

Cette mise à jour rend la logique de signal 100% tendance.
Les conditions de rebond "support/résistance" ont été supprimées afin que
les entrées exigent la direction EMA 12/50 et les conditions de momentum.

## Ce qui a changé

- Suppression des entrées alternatives sur rebond BB.
- Les entrées LONG exigent EMA12 > EMA50 et au moins 3/4 conditions principales.
- Les entrées SHORT exigent EMA12 < EMA50 et au moins 3/4 conditions principales.

## Pourquoi

Cela maintient le système aligné avec une stratégie de tendance en 15m et évite
les entrées contre-tendance qui peuvent dégrader le win rate en marché haché.

## Comment suivre les changements à l'avenir

- Ajouter une chaîne "version de stratégie" dans `config.py` et l'afficher au démarrage.
- Sauvegarder un snapshot de la config avec chaque rapport de paper trading.
- Tenir un changelog simple avec date, version et justification.
- Lancer un paper trading de comparaison sur une période fixe après chaque changement.
