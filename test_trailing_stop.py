#!/usr/bin/env python3
"""
Script de test pour valider le trailing stop (Stop Loss suiveur)
"""

from paper_trading import PaperTradingManager
import config

def test_trailing_stop_long():
    """Test du trailing stop pour une position LONG"""

    print("="*80)
    print("TEST DU TRAILING STOP - POSITION LONG")
    print("="*80)

    pt = PaperTradingManager()

    print(f"\n💰 Balance initiale: ${pt.balance:.2f}")
    print(f"📊 Trailing stop: {getattr(config, 'PAPER_TRADING_TRAILING_STOP_PERCENT', 0.5)}%")

    # Ouvrir une position LONG sur BTC à $100,000
    signal = {
        'type': 'LONG',
        'entry': 100000,
        'tp': 105000,  # +5%
        'sl': 99000,   # -1% (SL initial)
        'confidence': 75,
        'risk_reward': 5.0
    }

    analysis = {'symbol': 'BTC/USDT'}

    print("\n" + "─"*80)
    print("📈 OUVERTURE POSITION LONG BTC/USDT à $100,000")
    print("─"*80)

    position, msg = pt.open_position(signal, analysis)

    if position:
        print(f"✅ Position ouverte")
        print(f"  - SL initial: ${position['sl']:,.2f}")
        print(f"  - TP: ${position['tp']:,.2f}")

        # Scénario 1: Prix monte à $101,000 (+1%)
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 1: Prix monte à $101,000 (+1%)")
        print("─"*80)

        pt.update_positions('BTC/USDT', 101000)
        pos = pt.open_positions[0]

        print(f"Prix actuel: $101,000")
        print(f"SL ajusté: ${pos['sl']:,.2f}")
        print(f"✅ SL devrait être environ $100,495 (101000 * 0.995)")
        print(f"P&L: ${pos['pnl_usdt']:+.2f} ({pos['pnl_percent_on_margin']:+.2f}% sur marge)")

        # Scénario 2: Prix continue à monter à $102,000 (+2%)
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 2: Prix continue à $102,000 (+2%)")
        print("─"*80)

        pt.update_positions('BTC/USDT', 102000)
        pos = pt.open_positions[0]

        print(f"Prix actuel: $102,000")
        print(f"SL ajusté: ${pos['sl']:,.2f}")
        print(f"✅ SL devrait être environ $101,490 (102000 * 0.995)")
        print(f"P&L: ${pos['pnl_usdt']:+.2f} ({pos['pnl_percent_on_margin']:+.2f}% sur marge)")

        # Scénario 3: Prix retrace à $101,500 (-0.5%)
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 3: Prix retrace à $101,500 (-0.5% depuis pic)")
        print("─"*80)

        pt.update_positions('BTC/USDT', 101500)
        pos = pt.open_positions[0]

        print(f"Prix actuel: $101,500")
        print(f"SL: ${pos['sl']:,.2f}")
        print(f"✅ SL NE DOIT PAS avoir bougé (reste à $101,490)")
        print(f"P&L: ${pos['pnl_usdt']:+.2f} ({pos['pnl_percent_on_margin']:+.2f}% sur marge)")

        # Scénario 4: Prix descend et touche le trailing SL
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 4: Prix descend à $101,400 et touche le SL")
        print("─"*80)

        pt.update_positions('BTC/USDT', 101400)

        if not pt.open_positions:
            closed_pos = pt.closed_positions[-1]
            print(f"✅ Position fermée: {closed_pos['close_reason']}")
            print(f"Prix de sortie: ${closed_pos['exit_price']:,.2f}")
            print(f"P&L final: ${closed_pos['pnl_usdt']:+.2f} ({closed_pos['pnl_percent_on_margin']:+.2f}% sur marge)")
            print(f"💰 Balance finale: ${pt.balance:.2f}")
            print(f"\n🎯 SUCCÈS: Le trailing stop a sécurisé ~$1.40 de gain au lieu de tout perdre!")
        else:
            print(f"⚠️  Position encore ouverte, P&L: ${pt.open_positions[0]['pnl_usdt']:+.2f}")

def test_trailing_stop_short():
    """Test du trailing stop pour une position SHORT"""

    print("\n\n" + "="*80)
    print("TEST DU TRAILING STOP - POSITION SHORT")
    print("="*80)

    pt = PaperTradingManager()

    # Ouvrir une position SHORT sur ETH à $4,000
    signal = {
        'type': 'SHORT',
        'entry': 4000,
        'tp': 3800,   # -5%
        'sl': 4040,   # +1% (SL initial)
        'confidence': 75,
        'risk_reward': 5.0
    }

    analysis = {'symbol': 'ETH/USDT'}

    print("\n" + "─"*80)
    print("📉 OUVERTURE POSITION SHORT ETH/USDT à $4,000")
    print("─"*80)

    position, msg = pt.open_position(signal, analysis)

    if position:
        print(f"✅ Position ouverte")
        print(f"  - SL initial: ${position['sl']:,.2f}")
        print(f"  - TP: ${position['tp']:,.2f}")

        # Scénario 1: Prix descend à $3,960 (-1%)
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 1: Prix descend à $3,960 (-1%)")
        print("─"*80)

        pt.update_positions('ETH/USDT', 3960)
        pos = pt.open_positions[0]

        print(f"Prix actuel: $3,960")
        print(f"SL ajusté: ${pos['sl']:,.2f}")
        print(f"✅ SL devrait être environ $3,979.80 (3960 * 1.005)")
        print(f"P&L: ${pos['pnl_usdt']:+.2f} ({pos['pnl_percent_on_margin']:+.2f}% sur marge)")

        # Scénario 2: Prix continue à descendre à $3,920 (-2%)
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 2: Prix continue à $3,920 (-2%)")
        print("─"*80)

        pt.update_positions('ETH/USDT', 3920)
        pos = pt.open_positions[0]

        print(f"Prix actuel: $3,920")
        print(f"SL ajusté: ${pos['sl']:,.2f}")
        print(f"✅ SL devrait être environ $3,939.60 (3920 * 1.005)")
        print(f"P&L: ${pos['pnl_usdt']:+.2f} ({pos['pnl_percent_on_margin']:+.2f}% sur marge)")

        # Scénario 3: Prix rebondit et touche le trailing SL
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 3: Prix rebondit à $3,940 et touche le SL")
        print("─"*80)

        pt.update_positions('ETH/USDT', 3940)

        if not pt.open_positions:
            closed_pos = pt.closed_positions[-1]
            print(f"✅ Position fermée: {closed_pos['close_reason']}")
            print(f"Prix de sortie: ${closed_pos['exit_price']:,.2f}")
            print(f"P&L final: ${closed_pos['pnl_usdt']:+.2f} ({closed_pos['pnl_percent_on_margin']:+.2f}% sur marge)")
            print(f"💰 Balance finale: ${pt.balance:.2f}")
            print(f"\n🎯 SUCCÈS: Le trailing stop a sécurisé le gain au lieu de tout perdre!")
        else:
            print(f"⚠️  Position encore ouverte, P&L: ${pt.open_positions[0]['pnl_usdt']:+.2f}")

    print("\n" + "="*80)
    print("FIN DES TESTS")
    print("="*80)

if __name__ == "__main__":
    test_trailing_stop_long()
    test_trailing_stop_short()
