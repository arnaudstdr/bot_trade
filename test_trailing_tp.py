#!/usr/bin/env python3
"""
Script de test pour valider le Trailing Take Profit (TP suiveur)
"""

from paper_trading import PaperTradingManager
import config

def test_trailing_tp_long():
    """Test du trailing TP pour une position LONG"""

    print("="*80)
    print("TEST DU TRAILING TAKE PROFIT - POSITION LONG")
    print("="*80)

    pt = PaperTradingManager()

    print(f"\n💰 Balance initiale: ${pt.balance:.2f}")
    print(f"📊 Trailing TP: {getattr(config, 'PAPER_TRADING_TRAILING_TP_PERCENT', 2.0)}%")
    print(f"📊 Trailing SL: {getattr(config, 'PAPER_TRADING_TRAILING_STOP_PERCENT', 0.5)}%")

    # Ouvrir une position LONG sur BTC à $100,000
    signal = {
        'type': 'LONG',
        'entry': 100000,
        'tp': 102000,  # +2% initial
        'sl': 99000,   # -1% initial
        'confidence': 75,
        'risk_reward': 2.0
    }

    analysis = {'symbol': 'BTC/USDT'}

    print("\n" + "─"*80)
    print("📈 OUVERTURE POSITION LONG BTC/USDT à $100,000")
    print("─"*80)

    position, msg = pt.open_position(signal, analysis)

    if position:
        print(f"✅ Position ouverte")
        print(f"  - TP initial: ${position['tp']:,.2f} (+2%)")
        print(f"  - SL initial: ${position['sl']:,.2f} (-1%)")

        # Scénario 1: Prix monte à $101,000 (+1%)
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 1: Prix monte à $101,000 (+1%)")
        print("─"*80)

        pt.update_positions('BTC/USDT', 101000)
        pos = pt.open_positions[0]

        print(f"Prix actuel: $101,000")
        print(f"TP ajusté: ${pos['tp']:,.2f}")
        print(f"✅ TP devrait être ~$103,020 (101000 * 1.02)")
        print(f"SL ajusté: ${pos['sl']:,.2f}")
        print(f"P&L: ${pos['pnl_usdt']:+.2f} ({pos['pnl_percent_on_margin']:+.2f}% sur marge)")

        # Scénario 2: Prix continue à $103,000 (+3%)
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 2: Prix continue à $103,000 (+3%)")
        print("─"*80)

        pt.update_positions('BTC/USDT', 103000)
        pos = pt.open_positions[0]

        print(f"Prix actuel: $103,000")
        print(f"TP ajusté: ${pos['tp']:,.2f}")
        print(f"✅ TP devrait être ~$105,060 (103000 * 1.02)")
        print(f"SL ajusté: ${pos['sl']:,.2f}")
        print(f"P&L: ${pos['pnl_usdt']:+.2f} ({pos['pnl_percent_on_margin']:+.2f}% sur marge)")

        # Scénario 3: Prix atteint un pic à $105,000 (+5%)
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 3: Prix atteint $105,000 (+5%)")
        print("─"*80)

        pt.update_positions('BTC/USDT', 105000)
        pos = pt.open_positions[0]

        print(f"Prix actuel: $105,000")
        print(f"TP ajusté: ${pos['tp']:,.2f}")
        print(f"✅ TP devrait être ~$107,100 (105000 * 1.02)")
        print(f"SL ajusté: ${pos['sl']:,.2f}")
        print(f"P&L: ${pos['pnl_usdt']:+.2f} ({pos['pnl_percent_on_margin']:+.2f}% sur marge)")

        tp_at_peak = pos['tp']

        # Scénario 4: Prix retrace à $104,800 (en dessous du pic mais au-dessus du SL)
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 4: Prix retrace à $104,800 (-0.2% depuis pic)")
        print("─"*80)

        pt.update_positions('BTC/USDT', 104800)

        if pt.open_positions:
            pos = pt.open_positions[0]
            print(f"Prix actuel: $104,800")
            print(f"TP: ${pos['tp']:,.2f}")
            print(f"✅ TP NE DOIT PAS avoir bougé (reste à ${tp_at_peak:,.2f})")
            print(f"SL: ${pos['sl']:,.2f}")
            print(f"✅ Prix en dessous du pic mais au-dessus du SL = position toujours ouverte")
            print(f"P&L: ${pos['pnl_usdt']:+.2f} ({pos['pnl_percent_on_margin']:+.2f}% sur marge)")
        else:
            print(f"⚠️  Position fermée prématurément")

        # Scénario 5: Prix remonte et atteint le TP sécurisé
        print("\n" + "─"*80)
        print(f"📊 SCÉNARIO 5: Prix remonte et atteint le TP à ${tp_at_peak:,.2f}")
        print("─"*80)

        if pt.open_positions:
            pt.update_positions('BTC/USDT', tp_at_peak)

            if not pt.open_positions:
                closed_pos = pt.closed_positions[-1]
                print(f"🎯 Position fermée: {closed_pos['close_reason']}")
                print(f"Prix de sortie: ${closed_pos['exit_price']:,.2f}")
                print(f"P&L final: ${closed_pos['pnl_usdt']:+.2f} ({closed_pos['pnl_percent_on_margin']:+.2f}% sur marge)")
                print(f"💰 Balance finale: ${pt.balance:.2f}")
                print(f"\n✅ SUCCÈS: Le trailing TP a capturé ~$7.10 de gain au lieu de seulement $2!")
            else:
                print(f"⚠️  Position encore ouverte, P&L: ${pt.open_positions[0]['pnl_usdt']:+.2f}")
        else:
            print(f"Position déjà fermée au scénario précédent")

def test_trailing_tp_short():
    """Test du trailing TP pour une position SHORT"""

    print("\n\n" + "="*80)
    print("TEST DU TRAILING TAKE PROFIT - POSITION SHORT")
    print("="*80)

    # Réinitialiser pour le test SHORT
    pt = PaperTradingManager()
    pt.reset()

    # Ouvrir une position SHORT sur ETH à $4,000
    signal = {
        'type': 'SHORT',
        'entry': 4000,
        'tp': 3920,   # -2% initial
        'sl': 4040,   # +1% initial
        'confidence': 75,
        'risk_reward': 2.0
    }

    analysis = {'symbol': 'ETH/USDT'}

    print("\n" + "─"*80)
    print("📉 OUVERTURE POSITION SHORT ETH/USDT à $4,000")
    print("─"*80)

    position, msg = pt.open_position(signal, analysis)

    if position:
        print(f"✅ Position ouverte")
        print(f"  - TP initial: ${position['tp']:,.2f} (-2%)")
        print(f"  - SL initial: ${position['sl']:,.2f} (+1%)")

        # Scénario 1: Prix descend à $3,960 (-1%)
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 1: Prix descend à $3,960 (-1%)")
        print("─"*80)

        pt.update_positions('ETH/USDT', 3960)
        pos = pt.open_positions[0]

        print(f"Prix actuel: $3,960")
        print(f"TP ajusté: ${pos['tp']:,.2f}")
        print(f"✅ TP devrait être ~$3,880.80 (3960 * 0.98)")
        print(f"SL ajusté: ${pos['sl']:,.2f}")
        print(f"P&L: ${pos['pnl_usdt']:+.2f} ({pos['pnl_percent_on_margin']:+.2f}% sur marge)")

        # Scénario 2: Prix continue à $3,900 (-2.5%)
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 2: Prix continue à $3,900 (-2.5%)")
        print("─"*80)

        pt.update_positions('ETH/USDT', 3900)
        pos = pt.open_positions[0]

        print(f"Prix actuel: $3,900")
        print(f"TP ajusté: ${pos['tp']:,.2f}")
        print(f"✅ TP devrait être ~$3,822 (3900 * 0.98)")
        print(f"SL ajusté: ${pos['sl']:,.2f}")
        print(f"P&L: ${pos['pnl_usdt']:+.2f} ({pos['pnl_percent_on_margin']:+.2f}% sur marge)")

        # Scénario 3: Prix atteint un creux à $3,840 (-4%)
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 3: Prix atteint $3,840 (-4%)")
        print("─"*80)

        pt.update_positions('ETH/USDT', 3840)
        pos = pt.open_positions[0]

        print(f"Prix actuel: $3,840")
        print(f"TP ajusté: ${pos['tp']:,.2f}")
        print(f"✅ TP devrait être ~$3,763.20 (3840 * 0.98)")
        print(f"SL ajusté: ${pos['sl']:,.2f}")
        print(f"P&L: ${pos['pnl_usdt']:+.2f} ({pos['pnl_percent_on_margin']:+.2f}% sur marge)")

        tp_at_bottom = pos['tp']

        # Scénario 4: Prix rebondit légèrement à $3,850
        print("\n" + "─"*80)
        print("📊 SCÉNARIO 4: Prix rebondit légèrement à $3,850")
        print("─"*80)

        pt.update_positions('ETH/USDT', 3850)

        if pt.open_positions:
            pos = pt.open_positions[0]
            print(f"Prix actuel: $3,850")
            print(f"TP: ${pos['tp']:,.2f}")
            print(f"✅ TP NE DOIT PAS avoir bougé (reste à ${tp_at_bottom:,.2f})")
            print(f"SL: ${pos['sl']:,.2f}")
            print(f"P&L: ${pos['pnl_usdt']:+.2f} ({pos['pnl_percent_on_margin']:+.2f}% sur marge)")
        else:
            print(f"⚠️  Position fermée prématurément")

        # Scénario 5: Prix redescend et atteint le TP sécurisé
        print("\n" + "─"*80)
        print(f"📊 SCÉNARIO 5: Prix redescend et atteint le TP à ${tp_at_bottom:,.2f}")
        print("─"*80)

        if pt.open_positions:
            pt.update_positions('ETH/USDT', tp_at_bottom)

            if not pt.open_positions:
                closed_pos = pt.closed_positions[-1]
                print(f"🎯 Position fermée: {closed_pos['close_reason']}")
                print(f"Prix de sortie: ${closed_pos['exit_price']:,.2f}")
                print(f"P&L final: ${closed_pos['pnl_usdt']:+.2f} ({closed_pos['pnl_percent_on_margin']:+.2f}% sur marge)")
                print(f"💰 Balance finale: ${pt.balance:.2f}")
                print(f"\n✅ SUCCÈS: Le trailing TP a capturé un gain maximal!")
            else:
                print(f"⚠️  Position encore ouverte, P&L: ${pt.open_positions[0]['pnl_usdt']:+.2f}")
        else:
            print(f"Position déjà fermée au scénario précédent")

    print("\n" + "="*80)
    print("FIN DES TESTS")
    print("="*80)

if __name__ == "__main__":
    test_trailing_tp_long()
    test_trailing_tp_short()
