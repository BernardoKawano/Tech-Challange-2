"""
Sistema de Logging Genético.

Rastreia evolução, genealogia, mutações e mudanças significativas.
"""

from typing import List, Dict, Optional
import json
from datetime import datetime
from pathlib import Path
from .chromosome import Chromosome


class GeneticLogger:
    """Logger para rastrear evolução genética."""
    
    def __init__(self, output_dir: str = "logs/genetic"):
        """
        Inicializa o logger.
        
        Args:
            output_dir: Diretório para salvar logs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.chromosome_counter = 0
        self.generation_history = []
        self.significant_events = []
        self.genealogy = {}  # Mapa de ID -> informações do cromossomo
        
        # Threshold para eventos significativos
        self.improvement_threshold = 0.05  # 5% de melhoria
        
        # Estatísticas do AG
        self.total_crossovers = 0
        self.total_mutations = 0
        self.mutation_types_count = {}  # Contador por tipo de mutação
        self.crossover_types_count = {}  # Contador por tipo de crossover
        
        # Arquivos de log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.evolution_file = self.output_dir / f"evolution_{timestamp}.jsonl"
        self.events_file = self.output_dir / f"significant_events_{timestamp}.jsonl"
        self.summary_file = self.output_dir / f"summary_{timestamp}.txt"
        self.genealogy_file = self.output_dir / f"genealogy_{timestamp}.json"
    
    def assign_id(self, chromosome: Chromosome) -> int:
        """
        Atribui ID único a um cromossomo.
        
        Args:
            chromosome: Cromossomo a receber ID
        
        Returns:
            ID atribuído
        """
        self.chromosome_counter += 1
        chromosome.id = self.chromosome_counter
        return self.chromosome_counter
    
    def log_generation(self, 
                      generation: int, 
                      population: List[Chromosome],
                      best_chromosome: Chromosome,
                      avg_fitness: float,
                      diversity: float):
        """
        Registra informações de uma geração.
        
        Args:
            generation: Número da geração
            population: População atual
            best_chromosome: Melhor cromossomo
            avg_fitness: Fitness médio
            diversity: Diversidade genética
        """
        gen_info = {
            'generation': generation,
            'timestamp': datetime.now().isoformat(),
            'best_fitness': best_chromosome.fitness,
            'avg_fitness': avg_fitness,
            'worst_fitness': max(c.fitness for c in population),
            'diversity': diversity,
            'best_chromosome_id': best_chromosome.id,
            'best_genes': best_chromosome.to_string(),
            'num_active_vehicles': best_chromosome.get_num_active_vehicles(),
            'fitness_components': best_chromosome.fitness_components
        }
        
        self.generation_history.append(gen_info)
        
        # Salvar em arquivo JSONL (uma linha por geração)
        with open(self.evolution_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(gen_info) + '\n')
        
        # Verificar se houve melhoria significativa
        if len(self.generation_history) > 1:
            prev_best = self.generation_history[-2]['best_fitness']
            improvement = (prev_best - best_chromosome.fitness) / prev_best
            
            if improvement >= self.improvement_threshold:
                self.log_significant_event(
                    generation=generation,
                    event_type='SIGNIFICANT_IMPROVEMENT',
                    chromosome=best_chromosome,
                    details={
                        'previous_fitness': prev_best,
                        'new_fitness': best_chromosome.fitness,
                        'improvement_percent': improvement * 100,
                        'mutation': best_chromosome.mutation_applied
                    }
                )
    
    def log_crossover(self, 
                     generation: int,
                     parent1: Chromosome,
                     parent2: Chromosome,
                     child1: Chromosome,
                     child2: Chromosome,
                     crossover_type: str = "order"):
        """
        Registra operação de crossover.
        
        Args:
            generation: Número da geração
            parent1: Primeiro pai
            parent2: Segundo pai
            child1: Primeiro filho
            child2: Segundo filho
            crossover_type: Tipo de crossover usado
        """
        # Incrementar contadores
        self.total_crossovers += 1
        self.crossover_types_count[crossover_type] = self.crossover_types_count.get(crossover_type, 0) + 1
        
        # Atribuir IDs se não tiverem
        if child1.id is None:
            self.assign_id(child1)
        if child2.id is None:
            self.assign_id(child2)
        
        child1.generation = generation
        child2.generation = generation
        
        # Registrar genealogia
        self.genealogy[child1.id] = {
            'id': child1.id,
            'generation': generation,
            'type': 'crossover',
            'parent1_id': parent1.id,
            'parent2_id': parent2.id,
            'genes': child1.to_string(),
            'fitness': child1.fitness
        }
        
        self.genealogy[child2.id] = {
            'id': child2.id,
            'generation': generation,
            'type': 'crossover',
            'parent1_id': parent1.id,
            'parent2_id': parent2.id,
            'genes': child2.to_string(),
            'fitness': child2.fitness
        }
    
    def log_mutation(self, 
                    generation: int,
                    original: Chromosome,
                    mutated: Chromosome):
        """
        Registra operação de mutação.
        
        Args:
            generation: Número da geração
            original: Cromossomo original
            mutated: Cromossomo mutado
        """
        # Incrementar contadores
        self.total_mutations += 1
        mutation_type = mutated.mutation_applied or "UNKNOWN"
        self.mutation_types_count[mutation_type] = self.mutation_types_count.get(mutation_type, 0) + 1
        
        if mutated.id is None:
            self.assign_id(mutated)
        
        mutated.generation = generation
        
        # Calcular diferença
        orig_points = set(original.get_points())
        mut_points = set(mutated.get_points())
        
        # Registrar genealogia
        self.genealogy[mutated.id] = {
            'id': mutated.id,
            'generation': generation,
            'type': 'mutation',
            'parent_id': original.id,
            'mutation_type': mutated.mutation_applied or 'UNKNOWN',
            'genes_before': original.to_string(),
            'genes_after': mutated.to_string(),
            'fitness_before': original.fitness,
            'fitness_after': mutated.fitness,
            'fitness_change': mutated.fitness - original.fitness
        }
        
        # Se mutação causou melhoria significativa
        if original.fitness > 0:
            improvement = (original.fitness - mutated.fitness) / original.fitness
            if improvement >= self.improvement_threshold:
                self.log_significant_event(
                    generation=generation,
                    event_type='BENEFICIAL_MUTATION',
                    chromosome=mutated,
                    details={
                        'parent_id': original.id,
                        'mutation_type': mutated.mutation_applied,
                        'fitness_before': original.fitness,
                        'fitness_after': mutated.fitness,
                        'improvement_percent': improvement * 100
                    }
                )
    
    def log_significant_event(self,
                             generation: int,
                             event_type: str,
                             chromosome: Chromosome,
                             details: Dict):
        """
        Registra evento significativo.
        
        Args:
            generation: Número da geração
            event_type: Tipo de evento
            chromosome: Cromossomo relacionado
            details: Detalhes adicionais
        """
        event = {
            'generation': generation,
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'chromosome_id': chromosome.id,
            'genes': chromosome.to_string(),
            'fitness': chromosome.fitness,
            'details': details
        }
        
        self.significant_events.append(event)
        
        # Salvar em arquivo
        with open(self.events_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, indent=2) + '\n' + '='*80 + '\n')
    
    def save_summary(self, 
                    final_best: Chromosome,
                    total_generations: int,
                    execution_time: float):
        """
        Salva resumo final da execução.
        
        Args:
            final_best: Melhor cromossomo final
            total_generations: Total de gerações executadas
            execution_time: Tempo de execução em segundos
        """
        summary = []
        summary.append("="*80)
        summary.append("RESUMO DA EVOLUÇÃO GENÉTICA - VRP")
        summary.append("="*80)
        summary.append(f"\nData/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"Tempo de Execução: {execution_time:.2f} segundos")
        summary.append(f"Total de Gerações: {total_generations}")
        summary.append(f"Total de Cromossomos Criados: {self.chromosome_counter}")
        
        summary.append("\n" + "="*80)
        summary.append("MELHOR SOLUÇÃO ENCONTRADA")
        summary.append("="*80)
        summary.append(f"Fitness: {final_best.fitness:.2f}")
        summary.append(f"ID: {final_best.id}")
        summary.append(f"Geração: {final_best.generation}")
        summary.append(f"\nRotas: {final_best.to_string()}")
        
        if final_best.fitness_components:
            summary.append("\n" + "-"*80)
            summary.append("Componentes do Fitness:")
            summary.append("-"*80)
            for key, value in final_best.fitness_components.items():
                if isinstance(value, (int, float)):
                    summary.append(f"  {key}: {value:.2f}")
                elif isinstance(value, list):
                    summary.append(f"  {key}: {value}")
        
        summary.append("\n" + "="*80)
        summary.append("EVOLUÇÃO AO LONGO DAS GERAÇÕES")
        summary.append("="*80)
        
        if self.generation_history:
            initial_fitness = self.generation_history[0]['best_fitness']
            final_fitness = self.generation_history[-1]['best_fitness']
            improvement = (initial_fitness - final_fitness) / initial_fitness * 100
            
            summary.append(f"Fitness Inicial: {initial_fitness:.2f}")
            summary.append(f"Fitness Final: {final_fitness:.2f}")
            summary.append(f"Melhoria Total: {improvement:.2f}%")
            
            # Marcos importantes
            summary.append("\nMarcos de Melhoria:")
            milestones = [0, len(self.generation_history)//4, len(self.generation_history)//2, 
                         3*len(self.generation_history)//4, len(self.generation_history)-1]
            
            for idx in milestones:
                if idx < len(self.generation_history):
                    gen = self.generation_history[idx]
                    summary.append(f"  Gen {gen['generation']:4d}: Fitness = {gen['best_fitness']:.2f}, "
                                 f"Veículos = {gen['num_active_vehicles']}")
        
        summary.append("\n" + "="*80)
        summary.append(f"EVENTOS SIGNIFICATIVOS: {len(self.significant_events)}")
        summary.append("="*80)
        
        for i, event in enumerate(self.significant_events[:10], 1):  # Mostrar até 10
            summary.append(f"\n{i}. Gen {event['generation']}: {event['event_type']}")
            summary.append(f"   Cromossomo ID: {event['chromosome_id']}")
            summary.append(f"   Fitness: {event['fitness']:.2f}")
            if 'improvement_percent' in event['details']:
                summary.append(f"   Melhoria: {event['details']['improvement_percent']:.2f}%")
        
        if len(self.significant_events) > 10:
            summary.append(f"\n... e mais {len(self.significant_events) - 10} eventos.")
        
        summary.append("\n" + "="*80)
        summary.append("ARQUIVOS GERADOS")
        summary.append("="*80)
        summary.append(f"- Evolução completa: {self.evolution_file}")
        summary.append(f"- Eventos significativos: {self.events_file}")
        summary.append(f"- Genealogia: {self.genealogy_file}")
        summary.append(f"- Este resumo: {self.summary_file}")
        summary.append("="*80)
        
        # Salvar em arquivo
        with open(self.summary_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary))
        
        # Salvar genealogia
        with open(self.genealogy_file, 'w', encoding='utf-8') as f:
            json.dump(self.genealogy, f, indent=2, ensure_ascii=False)
        
        # Retornar resumo também
        return '\n'.join(summary)
    
    def get_chromosome_lineage(self, chromosome_id: int) -> List[Dict]:
        """
        Rastreia linhagem de um cromossomo até seus ancestrais.
        
        Args:
            chromosome_id: ID do cromossomo
        
        Returns:
            Lista de ancestrais em ordem (mais antigo primeiro)
        """
        lineage = []
        current_id = chromosome_id
        
        while current_id in self.genealogy:
            info = self.genealogy[current_id]
            lineage.insert(0, info)
            
            # Ir para o pai (usar parent1 se for crossover)
            if 'parent1_id' in info:
                current_id = info['parent1_id']
            elif 'parent_id' in info:
                current_id = info['parent_id']
            else:
                break  # Chegou na raiz (população inicial)
        
        return lineage
    
    def calculate_diversity(self, population: List[Chromosome]) -> float:
        """
        Calcula diversidade genética da população.
        
        Args:
            population: População de cromossomos
        
        Returns:
            Índice de diversidade (0-1)
        """
        if len(population) < 2:
            return 0.0
        
        # Usar distância de Hamming entre cromossomos
        distances = []
        for i in range(len(population)):
            for j in range(i+1, len(population)):
                points_i = set(population[i].get_points())
                points_j = set(population[j].get_points())
                
                # Distância baseada em diferença de posições
                distance = 0
                for pi, pj in zip(population[i].get_points(), population[j].get_points()):
                    if pi != pj:
                        distance += 1
                
                distances.append(distance)
        
        if not distances:
            return 0.0
        
        # Normalizar pela máxima distância possível
        max_possible = len(population[0].get_points())
        avg_distance = sum(distances) / len(distances)
        diversity = avg_distance / max_possible if max_possible > 0 else 0
        
        return min(diversity, 1.0)

