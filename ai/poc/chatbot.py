"""
Sprint 3 — RAG + hafıza destekli chatbot.

    python poc/chatbot.py
    python poc/chatbot.py --groq
    python poc/chatbot.py --question "Zencefil mide bulantısına iyi gelir mi?"
    python poc/chatbot.py --json --question "Uyku için ne var?"
"""

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from memory import memory_store
from orchestrator import orchestrate

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def interactive(use_groq: bool, as_json: bool):
    mode = "Groq + RAG" if use_groq else "Sablon + RAG"
    session_id = memory_store.create_session()

    print(f"=== PhyraMed Chatbot ({mode}) ===")
    print(f"Oturum: {session_id}")
    print("Cikmak icin 'quit' yazin.\n")

    while True:
        try:
            question = input("Soru> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGorusmek uzere.")
            break

        if not question:
            continue

        if question.lower() in {"quit", "exit", "q"}:
            print("Gorusmek uzere.")
            break

        result = orchestrate(
            question,
            session_id=session_id,
            use_groq=use_groq,
        )

        print()
        if as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["answer"])
            if result["sources"]:
                names = ", ".join(s["name"] for s in result["sources"])
                print(f"\n[Kaynaklar: {names}]")
        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--groq", action="store_true", help="Groq ile dogal dil cevabi")
    parser.add_argument("--question", "-q", type=str, help="Tek soru sor")
    parser.add_argument("--json", action="store_true", help="Yapilandirilmis JSON cikti")
    parser.add_argument("--session", type=str, help="Mevcut oturum ID'si")
    args = parser.parse_args()

    if args.question:
        result = orchestrate(
            args.question,
            session_id=args.session,
            use_groq=args.groq,
        )
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["answer"])
    else:
        interactive(args.groq, args.json)


if __name__ == "__main__":
    main()
