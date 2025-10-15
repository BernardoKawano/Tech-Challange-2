"""
Motor Principal do Algoritmo Genético.

Coordena toda a execução do AG: inicialização, seleção, crossover,
mutação, avaliação e logging.
"""

from typing import List, Dict, Callable, Optional, Tuple
import random
import time
from ..models.delivery_point import DeliveryPoint
from ..models.vehicle import Vehicle
from .chromosome import Chromosome
from .operators import GeneticOperators
from .fitness import FitnessCalculator
from .logger import GeneticLogger


class GeneticAlgorithm:
    """Motor do Algoritmo Genético para VRP."""
    
    def __init__(self,
                 delivery_points: List[DeliveryPoint],
                 vehicles: List[Vehicle],
                 depot_coord: Tuple[float, float],
                 config: Dict = None):
        """
        Inicializa o Algoritmo Genético.
        
        Args:
            delivery_points: Lista de pontos de entrega
            vehicles: Lista de veículos disponíveis
            depot_coord: Coordenadas do depósito (lat, lon)
            config: Configurações do AG
        """
        self.delivery_points = delivery_points
        self.vehicles = vehicles
        self.depot_coord = depot_coord
        self.num_points = len(delivery_points)
        self.num_vehicles = len(vehicles)
        
        # Configuração padrão
        default_config = {
            'population_size': 100,
            'num_generations': 500,
            'crossover_rate': 0.8,
            'mutation_rate': 0.3,
            'elitism_rate': 0.1,
            'tournament_size': 3,
            'convergence_threshold': 0.001,
            'max_gens_without_improvement': 50,
            'fitness_weights': {
                'distance': 1.0,
                'capacity': 10.0,
                'autonomy': 10.0,
                'priority': 5.0,
                'balance': 2.0,
                'num_vehicles': 3.0
            },
            'mutation_types': ['swap', 'inversion', 'move'],
            'mutation_weights': [0.4, 0.3, 0.3],  # Probabilidades relativas
            'crossover_type': 'order',  # 'order' ou 'pmx'
            'selection_type': 'tournament',  # 'tournament' ou 'roulette'
            'enable_logging': True,
            'log_dir': 'logs/genetic'
        }
        
        self.config = {**default_config, **(config or {})}
        
        # Inicializar componentes
        self.fitness_calculator = FitnessCalculator(
            delivery_points=delivery_points,
            vehicles=vehicles,
            depot_coord=depot_coord,
            weights=self.config['fitness_weights']
        )
        
        self.logger = None
        if self.config['enable_logging']:
            self.logger = GeneticLogger(output_dir=self.config['log_dir'])
        
        # Estado da evolução
        self.population = []
        self.best_chromosome = None
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.diversity_history = []
        self.current_generation = 0
        self.generations_without_improvement = 0
        
        # Callbacks
        self.generation_callback = None
    
    def initialize_population(self):
        """Cria população inicial aleatória."""
        print(f"Inicializando população de {self.config['population_size']} indivíduos...")
        
        self.population = []
        for i in range(self.config['population_size']):
            chromosome = Chromosome.create_random(self.num_points, self.num_vehicles)
            
            # Avaliar fitness
            self.fitness_calculator.calculate_fitness(chromosome)
            
            # Atribuir ID e registrar
            if self.logger:
                self.logger.assign_id(chromosome)
                chromosome.generation = 0
            
            self.population.append(chromosome)
        
        # Ordenar por fitness
        self.population.sort()
        self.best_chromosome = self.population[0].copy()
        
        print(f"População inicial criada. Melhor fitness: {self.best_chromosome.fitness:.2f}")
    
    def select_parents(self) -> Tuple[Chromosome, Chromosome]:
        """
        Seleciona dois pais para reprodução.
        
        Returns:
            Tupla com dois cromossomos pais
        """
        if self.config['selection_type'] == 'tournament':
            parent1 = GeneticOperators.tournament_selection(
                self.population, 
                self.config['tournament_size']
            )
            parent2 = GeneticOperators.tournament_selection(
                self.population, 
                self.config['tournament_size']
            )
        else:  # roulette
            parent1 = GeneticOperators.roulette_selection(self.population)
            parent2 = GeneticOperators.roulette_selection(self.population)
        
        # Garantir que os pais são diferentes
        attempts = 0
        while parent2.id == parent1.id and attempts < 10:
            parent2 = GeneticOperators.tournament_selection(
                self.population, 
                self.config['tournament_size']
            )
            attempts += 1
        
        return parent1, parent2
    
    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Aplica operador de crossover.
        
        Args:
            parent1: Primeiro pai
            parent2: Segundo pai
        
        Returns:
            Tupla com dois filhos
        """
        if self.config['crossover_type'] == 'pmx':
            child1, child2 = GeneticOperators.partially_mapped_crossover_vrp(parent1, parent2)
        else:  # order
            child1, child2 = GeneticOperators.order_crossover_vrp(parent1, parent2)
        
        # Avaliar fitness dos filhos
        self.fitness_calculator.calculate_fitness(child1)
        self.fitness_calculator.calculate_fitness(child2)
        
        # Registrar crossover
        if self.logger:
            self.logger.log_crossover(self.current_generation, parent1, parent2, child1, child2, 
                                     self.config['crossover_type'])
        
        return child1, child2
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """
        Aplica operador de mutação.
        
        Args:
            chromosome: Cromossomo a ser mutado
        
        Returns:
            Cromossomo mutado
        """
        # Escolher tipo de mutação aleatoriamente baseado nos pesos
        mutation_type = random.choices(
            self.config['mutation_types'],
            weights=self.config['mutation_weights']
        )[0]
        
        original = chromosome.copy()
        
        if mutation_type == 'swap':
            mutated = GeneticOperators.swap_mutation(chromosome, self.num_points)
        elif mutation_type == 'inversion':
            mutated = GeneticOperators.inversion_mutation(chromosome, self.num_points)
        else:  # move
            mutated = GeneticOperators.move_mutation(chromosome, self.num_points)
        
        # Avaliar fitness
        self.fitness_calculator.calculate_fitness(mutated)
        
        # Registrar mutação
        if self.logger:
            self.logger.log_mutation(self.current_generation, original, mutated)
        
        return mutated
    
    def evolve_generation(self):
        """Evolui uma geração completa."""
        new_population = []
        
        # Elitismo: manter os melhores indivíduos
        elite_size = int(self.config['population_size'] * self.config['elitism_rate'])
        elite = self.population[:elite_size]
        new_population.extend([c.copy() for c in elite])
        
        # Gerar restante da população
        while len(new_population) < self.config['population_size']:
            # Seleção
            parent1, parent2 = self.select_parents()
            
            # Crossover
            if random.random() < self.config['crossover_rate']:
                child1, child2 = self.crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
                self.fitness_calculator.calculate_fitness(child1)
                self.fitness_calculator.calculate_fitness(child2)
            
            # Mutação
            if random.random() < self.config['mutation_rate']:
                child1 = self.mutate(child1)
            
            if random.random() < self.config['mutation_rate']:
                child2 = self.mutate(child2)
            
            new_population.append(child1)
            if len(new_population) < self.config['population_size']:
                new_population.append(child2)
        
        # Atualizar população
        self.population = new_population[:self.config['population_size']]
        self.population.sort()
        
        # Atualizar melhor solução
        current_best = self.population[0]
        if current_best.fitness < self.best_chromosome.fitness:
            improvement = (self.best_chromosome.fitness - current_best.fitness) / self.best_chromosome.fitness
            self.best_chromosome = current_best.copy()
            self.generations_without_improvement = 0
            
            print(f"Gen {self.current_generation}: Nova melhor solução! "
                  f"Fitness: {self.best_chromosome.fitness:.2f} "
                  f"(↓{improvement*100:.2f}%)")
        else:
            self.generations_without_improvement += 1
    
    def run(self, generation_callback: Optional[Callable] = None):
        """
        Executa o algoritmo genético.
        
        Args:
            generation_callback: Função callback chamada a cada geração
                                Assinatura: callback(ga, generation, best, avg_fitness)
        
        Returns:
            Melhor cromossomo encontrado
        """
        print("\n" + "="*80)
        print("INICIANDO ALGORITMO GENÉTICO - VRP")
        print("="*80)
        print(f"Pontos de entrega: {self.num_points}")
        print(f"Veículos disponíveis: {self.num_vehicles}")
        print(f"Tamanho da população: {self.config['population_size']}")
        print(f"Gerações máximas: {self.config['num_generations']}")
        print(f"Taxa de crossover: {self.config['crossover_rate']}")
        print(f"Taxa de mutação: {self.config['mutation_rate']}")
        print(f"Elitismo: {self.config['elitism_rate']*100:.0f}%")
        print("="*80 + "\n")
        
        start_time = time.time()
        self.generation_callback = generation_callback
        
        # Inicializar população
        self.initialize_population()
        
        # Log inicial
        if self.logger:
            diversity = self.logger.calculate_diversity(self.population)
            avg_fitness = sum(c.fitness for c in self.population) / len(self.population)
            self.logger.log_generation(0, self.population, self.best_chromosome, avg_fitness, diversity)
            self.diversity_history.append(diversity)
        
        self.best_fitness_history.append(self.best_chromosome.fitness)
        avg_fitness = sum(c.fitness for c in self.population) / len(self.population)
        self.avg_fitness_history.append(avg_fitness)
        
        # Callback inicial
        if generation_callback:
            generation_callback(self, 0, self.best_chromosome, avg_fitness)
        
        # Loop principal
        for gen in range(1, self.config['num_generations'] + 1):
            self.current_generation = gen
            
            # Evoluir
            self.evolve_generation()
            
            # Calcular métricas
            avg_fitness = sum(c.fitness for c in self.population) / len(self.population)
            self.best_fitness_history.append(self.best_chromosome.fitness)
            self.avg_fitness_history.append(avg_fitness)
            
            # Diversidade
            diversity = 0
            if self.logger:
                diversity = self.logger.calculate_diversity(self.population)
                self.diversity_history.append(diversity)
                
                # Log da geração
                self.logger.log_generation(gen, self.population, self.best_chromosome, avg_fitness, diversity)
            
            # Callback
            if generation_callback:
                generation_callback(self, gen, self.best_chromosome, avg_fitness)
            
            # Mostrar progresso a cada 10 gerações
            if gen % 10 == 0 or gen == 1:
                print(f"Gen {gen:4d}: Best={self.best_chromosome.fitness:7.2f}, "
                      f"Avg={avg_fitness:7.2f}, "
                      f"Diversity={diversity:.3f}, "
                      f"No Improve={self.generations_without_improvement}")
            
            # Verificar convergência - DESABILITADO PARA RODAR TODAS AS GERAÇÕES
            # if self.generations_without_improvement >= self.config['max_gens_without_improvement']:
            #     print(f"\nConvergiu na geração {gen} (sem melhoria por {self.generations_without_improvement} gerações)")
            #     break
            
            # Verificar convergência por threshold - DESABILITADO PARA RODAR TODAS AS GERAÇÕES
            # if len(self.best_fitness_history) >= 10:
            #     recent_improvement = (self.best_fitness_history[-10] - self.best_chromosome.fitness) / self.best_fitness_history[-10]
            #     if recent_improvement < self.config['convergence_threshold']:
            #         print(f"\nConvergiu na geração {gen} (melhoria < {self.config['convergence_threshold']*100:.2f}%)")
            #         break
        
        execution_time = time.time() - start_time
        
        print("\n" + "="*80)
        print("EVOLUÇÃO COMPLETA!")
        print("="*80)
        print(f"Gerações executadas: {self.current_generation}")
        print(f"Tempo de execução: {execution_time:.2f} segundos")
        print(f"Melhor fitness: {self.best_chromosome.fitness:.2f}")
        print(f"Melhoria total: {(self.best_fitness_history[0] - self.best_chromosome.fitness) / self.best_fitness_history[0] * 100:.2f}%")
        print("="*80 + "\n")
        
        # Salvar resumo
        if self.logger:
            summary = self.logger.save_summary(
                self.best_chromosome,
                self.current_generation,
                execution_time
            )
            print(summary)
        
        return self.best_chromosome
    
    def get_best_solution_details(self) -> Dict:
        """
        Obtém detalhes completos da melhor solução.
        
        Returns:
            Dicionário com informações detalhadas
        """
        return self.fitness_calculator.get_detailed_metrics(self.best_chromosome)
    
    def get_statistics(self) -> Dict:
        """
        Obtém estatísticas do algoritmo genético.
        
        Returns:
            Dicionário com estatísticas
        """
        stats = {
            'current_generation': self.current_generation,
            'total_crossovers': 0,
            'total_mutations': 0,
            'mutation_types': {},
            'crossover_types': {},
            'selection_type': self.config['selection_type'],
            'crossover_type': self.config['crossover_type'],
            'mutation_rate': self.config['mutation_rate'],
            'crossover_rate': self.config['crossover_rate'],
            'population_size': self.config['population_size']
        }
        
        if self.logger:
            stats['total_crossovers'] = self.logger.total_crossovers
            stats['total_mutations'] = self.logger.total_mutations
            stats['mutation_types'] = self.logger.mutation_types_count.copy()
            stats['crossover_types'] = self.logger.crossover_types_count.copy()
        
        return stats

