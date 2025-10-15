"""
Módulo de integração com LLMs (Large Language Models).

Suporta Ollama (local, grátis) e OpenAI (nuvem, pago).
"""

from .instruction_generator import InstructionGenerator
from .report_generator import ReportGenerator
from .qa_system import QASystem, interactive_qa_session

__all__ = ['InstructionGenerator', 'ReportGenerator', 'QASystem', 'interactive_qa_session']
