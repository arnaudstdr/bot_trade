#!/usr/bin/env python3
"""
Script de test pour vérifier le système d'horaires
"""

from datetime import datetime
import config

def test_trading_hours():
    """Teste la logique des horaires de trading"""

    now = datetime.now()
    current_hour = now.hour
    current_day = now.weekday()

    print("\n" + "="*70)
    print("🧪 TEST DES HORAIRES DE TRADING")
    print("="*70)

    print(f"\n📅 Date et heure actuelle: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Jour de la semaine: {['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][current_day]}")
    print(f"🕐 Heure: {current_hour}h")

    print("\n" + "-"*70)
    print("CONFIGURATION:")
    print("-"*70)
    print(f"Horaires activés: {config.TRADING_HOURS_ENABLED}")
    print(f"Heure de début: {config.TRADING_HOURS_START}h")
    print(f"Heure de fin: {config.TRADING_HOURS_END}h")
    print(f"Jours autorisés: {[['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'][d] for d in config.TRADING_ENABLED_DAYS]}")

    print("\n" + "-"*70)
    print("RÉSULTAT:")
    print("-"*70)

    # Vérifier si on est dans les horaires
    if not config.TRADING_HOURS_ENABLED:
        print("✅ Restrictions d'horaires DÉSACTIVÉES")
        print("   → Les notifications seront envoyées 24/7")
        return

    in_trading_hours = True
    reasons = []

    # Vérifier le jour
    if current_day not in config.TRADING_ENABLED_DAYS:
        in_trading_hours = False
        reasons.append(f"Jour non autorisé ({['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'][current_day]})")

    # Vérifier l'heure
    if current_hour < config.TRADING_HOURS_START:
        in_trading_hours = False
        reasons.append(f"Trop tôt (avant {config.TRADING_HOURS_START}h)")
    elif current_hour >= config.TRADING_HOURS_END:
        in_trading_hours = False
        reasons.append(f"Trop tard (après {config.TRADING_HOURS_END}h)")

    if in_trading_hours:
        print("✅ DANS LES HORAIRES DE TRADING")
        print("   → Les notifications SERONT envoyées")
    else:
        print("❌ HORS HORAIRES DE TRADING")
        print("   → Les notifications NE SERONT PAS envoyées")
        print("\nRaisons:")
        for reason in reasons:
            print(f"   • {reason}")

    print("\n" + "="*70)

    # Afficher les prochaines fenêtres de trading
    print("\nPROCHAINES FENÊTRES DE TRADING:")
    print("-"*70)

    days_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    for day_num in config.TRADING_ENABLED_DAYS:
        print(f"{days_names[day_num]}: {config.TRADING_HOURS_START}h00 - {config.TRADING_HOURS_END}h00")

    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    test_trading_hours()
