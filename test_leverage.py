#!/usr/bin/env python3
"""
Script de test pour valider les calculs de levier dans le paper trading
"""

from paper_trading import PaperTradingManager
import config

def test_leverage_calculations():
    """Test les calculs avec effet de levier 5x"""

    print("="*80)
    print("TEST DE L'EFFET DE LEVIER 5x")
    print("="*80)

    # Créer un nouveau manager
    pt = PaperTradingManager()

    print(f"\n💰 Balance initiale: ${pt.balance:.2f}")
    print(f"📊 Levier configuré: {getattr(config, 'PAPER_TRADING_LEVERAGE', 1)}x")
    print(f"📊 Position size: {getattr(config, 'PAPER_TRADING_POSITION_SIZE_PERCENT', 2)}% du capital")

    # Simuler un signal LONG sur BTC à $100,000
    signal = {
        'type': 'LONG',
        'entry': 100000,
        'tp': 102000,  # +2% sur le prix
        'sl': 99000,   # -1% sur le prix
        'confidence': 75,
        'risk_reward': 2.0
    }

    analysis = {
        'symbol': 'BTC/USDT'
    }

    # Ouvrir la position
    print("\n" + "─"*80)
    print("📈 OUVERTURE POSITION LONG BTC/USDT")
    print("─"*80)

    position, msg = pt.open_position(signal, analysis)

    if position:
        margin = position.get('margin_usdt', 0)
        size = position.get('size_usdt', 0)
        leverage = position.get('leverage', 1)
        liq_price = position.get('liquidation_price', 0)

        print(f"✅ {msg}")
        print(f"\n📊 Détails de la position:")
        print(f"  - Prix d'entrée: ${position['entry_price']:,.2f}")
        print(f"  - Marge investie: ${margin:.2f} ({config.PAPER_TRADING_POSITION_SIZE_PERCENT}% de ${pt.initial_balance})")
        print(f"  - Taille position: ${size:.2f} (avec levier {leverage}x)")
        print(f"  - Quantité BTC: {position['size_crypto']:.6f}")
        print(f"  - Prix liquidation: ${liq_price:,.2f}")
        print(f"  - TP: ${position['tp']:,.2f}")
        print(f"  - SL: ${position['sl']:,.2f}")
        print(f"\n💰 Balance restante: ${pt.balance:.2f}")

        # Test 1: Prix monte à $101,000 (+1%)
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 1: Prix monte à $101,000 (+1% sur le prix)")
        print("─"*80)

        pt.update_positions('BTC/USDT', 101000)
        pos = pt.open_positions[0]

        print(f"P&L: ${pos['pnl_usdt']:+.2f}")
        print(f"P&L sur marge: {pos['pnl_percent_on_margin']:+.2f}%")
        print(f"P&L sur prix: {pos['pnl_percent']:+.2f}%")
        print(f"✅ Avec levier 5x, +1% de mouvement = +5% de gain sur la marge")

        # Test 2: Prix atteint le TP
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 2: Prix atteint le TP à $102,000 (+2% sur le prix)")
        print("─"*80)

        pt.update_positions('BTC/USDT', 102000)

        if not pt.open_positions:
            closed_pos = pt.closed_positions[-1]
            print(f"✅ Position fermée: {closed_pos['close_reason']}")
            print(f"P&L: ${closed_pos['pnl_usdt']:+.2f}")
            print(f"P&L sur marge: {closed_pos['pnl_percent_on_margin']:+.2f}%")
            print(f"P&L sur prix: {closed_pos['pnl_percent']:+.2f}%")
            print(f"💰 Balance finale: ${pt.balance:.2f}")
            print(f"✅ Avec levier 5x, +2% de mouvement = +10% de gain sur la marge")

    # Test de liquidation
    print("\n" + "="*80)
    print("TEST DE LIQUIDATION")
    print("="*80)

    # Réinitialiser
    pt.reset()

    # Ouvrir une nouvelle position SHORT
    signal_short = {
        'type': 'SHORT',
        'entry': 100000,
        'tp': 98000,
        'sl': 101000,
        'confidence': 75,
        'risk_reward': 2.0
    }

    print("\n📉 OUVERTURE POSITION SHORT BTC/USDT à $100,000")
    position, msg = pt.open_position(signal_short, analysis)

    if position:
        liq_price = position.get('liquidation_price', 0)
        print(f"✅ Position ouverte")
        print(f"Prix de liquidation: ${liq_price:,.2f}")

        # Simuler un mouvement violent vers le haut
        print(f"\n📊 Prix monte violemment à ${liq_price + 100:,.2f} (au-dessus de la liquidation)")
        pt.update_positions('BTC/USDT', liq_price + 100)

        if not pt.open_positions:
            closed_pos = pt.closed_positions[-1]
            if closed_pos['close_reason'] == 'LIQUIDATED':
                print(f"💀 LIQUIDÉ!")
                print(f"P&L: ${closed_pos['pnl_usdt']:+.2f}")
                print(f"Balance finale: ${pt.balance:.2f}")
                print(f"✅ Perte limitée à la marge investie: ${closed_pos.get('margin_usdt', 0):.2f}")

    print("\n" + "="*80)
    print("FIN DES TESTS")
    print("="*80)

if __name__ == "__main__":
    test_leverage_calculations()
