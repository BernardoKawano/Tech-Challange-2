"""
Chat em tempo real com LLM usando contexto da ultima simulacao.

Uso:
    python chat_realtime.py
"""

import json
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.llm_integration import QASystem, interactive_qa_session


def load_latest_context() -> dict:
    context_file = project_root / "outputs" / "session" / "latest_context.json"
    if not context_file.exists():
        raise FileNotFoundError(
            "Contexto nao encontrado. Execute primeiro: python main.py"
        )
    with open(context_file, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=" * 70)
    print("CHAT CONVERSACIONAL EM TEMPO REAL - ROTAS OTIMIZADAS")
    print("=" * 70)

    try:
        context = load_latest_context()
    except Exception as e:
        print(f"\nErro ao carregar contexto: {e}")
        return

    try:
        qa = QASystem(provider="ollama", model="llama2")
    except Exception as e:
        print(f"\nErro ao inicializar Q&A: {e}")
        print("\nVerifique:")
        print("  - Ollama instalado")
        print("  - Servidor ativo: ollama serve")
        print("  - Modelo baixado: ollama pull llama2")
        return

    qa.load_context(
        routes=context["routes"],
        vehicles=context["vehicles"],
        delivery_points=context["delivery_points"],
        metrics=context["metrics"],
        ga_stats=context.get("ga_stats", {}),
    )

    interactive_qa_session(qa, stream=True)


if __name__ == "__main__":
    main()
