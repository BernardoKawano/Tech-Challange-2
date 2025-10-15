"""
Módulo de Algoritmo Genético para VRP (Vehicle Routing Problem).

Este módulo implementa um AG completo para otimização de rotas de múltiplos
veículos com restrições realistas.
"""

from .chromosome import Chromosome
from .operators import GeneticOperators
from .fitness import FitnessCalculator
from .ga_engine import GeneticAlgorithm
from .logger import GeneticLogger

__all__ = [
    'Chromosome',
    'GeneticOperators',
    'FitnessCalculator',
    'GeneticAlgorithm',
    'GeneticLogger'
]
