"""
Módulo de integração com LLMs (Large Language Models).

Suporta Ollama (local, grátis) e OpenAI (nuvem, pago).
"""

from .instruction_generator import InstructionGenerator
from .report_generator import ReportGenerator

__all__ = ['InstructionGenerator', 'ReportGenerator']
