#!/usr/bin/env python3
"""
Génère un rapport de performance du Paper Trading
"""

from paper_trading import PaperTradingManager
from datetime import datetime

def print_report():
    """Affiche un rapport complet du paper trading"""
    pt = PaperTradingManager()

    print("\n" + "="*80)
    print("📊 RAPPORT DE PERFORMANCE - PAPER TRADING")
    print("="*80)

    stats = pt.get_statistics()

    # Statistiques générales
    print("\n┌─ RÉSUMÉ GÉNÉRAL " + "─"*62)
    print(f"│ Balance initiale:      ${stats['initial_balance']:.2f}")
    print(f"│ Balance libre:         ${stats['current_balance']:.2f}")
    print(f"│ Capital en positions:  ${stats.get('open_positions_value', 0):.2f}")
    print(f"│ P&L non réalisé:       ${stats.get('unrealized_pnl', 0):+.2f}")
    print(f"│ Valeur portefeuille:   ${stats.get('total_portfolio_value', stats['current_balance']):.2f}")
    print(f"│ ROI:                  {stats['roi']:+.2f}%")
    print(f"│")
    print(f"│ P&L réalisé (fermé):  ${stats['total_pnl']:+.2f} ({stats['total_pnl_percent']:+.2f}%)")
    print(f"│ Positions ouvertes:    {stats['open_positions']}")
    print("└" + "─"*79)

    # Statistiques de trading
    if stats['total_trades'] > 0:
        print("\n┌─ STATISTIQUES DE TRADING " + "─"*52)
        print(f"│ Total trades:      {stats['total_trades']}")
        print(f"│ Gagnants:         {stats['wins']} ({stats['win_rate']:.1f}%)")
        print(f"│ Perdants:         {stats['losses']} ({100-stats['win_rate']:.1f}%)")
        print(f"│ Gain moyen:       ${stats['avg_win']:.2f}")
        print(f"│ Perte moyenne:    ${stats['avg_loss']:.2f}")
        print(f"│ Meilleur trade:   ${stats['best_trade']:.2f}")
        print(f"│ Pire trade:       ${stats['worst_trade']:.2f}")
        print(f"│ Durée moyenne:    {stats['avg_trade_duration']:.1f}h")
        print("└" + "─"*79)

        # Positions ouvertes
        if pt.open_positions:
            print("\n┌─ POSITIONS OUVERTES " + "─"*57)
            for pos in pt.open_positions:
                emoji = "🟢" if pos['pnl_usdt'] > 0 else "🔴"
                print(f"│ {emoji} {pos['type']:<5} {pos['symbol']:<12} Entrée: ${pos['entry_price']:.4f} | P&L: ${pos['pnl_usdt']:+.2f} ({pos['pnl_percent']:+.2f}%)")
            print("└" + "─"*79)

        # Derniers trades fermés
        if pt.closed_positions:
            print("\n┌─ DERNIERS TRADES FERMÉS " + "─"*53)
            last_trades = pt.closed_positions[-10:]  # 10 derniers
            for pos in reversed(last_trades):
                emoji = "🟢" if pos['pnl_usdt'] > 0 else "🔴"
                reason = pos['close_reason'].replace('_', ' ')
                print(f"│ {emoji} {pos['type']:<5} {pos['symbol']:<12} {reason:<12} P&L: ${pos['pnl_usdt']:+.2f} ({pos['pnl_percent']:+.2f}%)")
            print("└" + "─"*79)

        # Analyse par symbole
        print("\n┌─ ANALYSE PAR SYMBOLE " + "─"*56)
        symbols_stats = {}
        for pos in pt.closed_positions:
            symbol = pos['symbol']
            if symbol not in symbols_stats:
                symbols_stats[symbol] = {'trades': 0, 'wins': 0, 'pnl': 0}
            symbols_stats[symbol]['trades'] += 1
            if pos['pnl_usdt'] > 0:
                symbols_stats[symbol]['wins'] += 1
            symbols_stats[symbol]['pnl'] += pos['pnl_usdt']

        for symbol, data in sorted(symbols_stats.items(), key=lambda x: x[1]['pnl'], reverse=True):
            win_rate = (data['wins'] / data['trades'] * 100) if data['trades'] > 0 else 0
            emoji = "🟢" if data['pnl'] > 0 else "🔴"
            print(f"│ {emoji} {symbol:<12} Trades: {data['trades']:>2} | Win Rate: {win_rate:>5.1f}% | P&L: ${data['pnl']:+.2f}")
        print("└" + "─"*79)

    else:
        print("\n⏸️  Aucun trade fermé pour le moment")

    print("\n" + "="*80)
    print()

def reset_paper_trading():
    """Réinitialise le paper trading"""
    pt = PaperTradingManager()

    print("\n⚠️  ATTENTION: Vous êtes sur le point de réinitialiser le paper trading.")
    print("   Toutes les positions et l'historique seront perdus.")

    confirmation = input("\nTapez 'RESET' pour confirmer: ")

    if confirmation == "RESET":
        pt.reset()
        print("✅ Paper trading réinitialisé")
    else:
        print("❌ Réinitialisation annulée")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_paper_trading()
    else:
        print_report()
