#!/usr/bin/env python3
"""
Script de test pour un cycle unique d'analyse
"""

from agent import TradingAgent

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TEST DE L'AGENT - 1 CYCLE D'ANALYSE")
    print("="*70 + "\n")

    agent = TradingAgent()

    print("Configuration:")
    print(f"  - Timeframe: {agent.exchange.__class__.__name__}")
    print(f"  - LLM: Mistral AI")
    print(f"  - Notifications: Pushover")
    print()

    # Lancer un seul cycle d'analyse
    agent.analyze_and_alert()

    print("\n" + "="*70)
    print("✅ Test terminé")
    print("="*70 + "\n")
