"""
Operadores Genéticos: Crossover, Mutação e Seleção.

Implementa operadores especializados para VRP com múltiplos veículos.
"""

from typing import List, Tuple
import random
import copy
from .chromosome import Chromosome


def get_point_label(index: int) -> str:
    """
    Gera label para ponto de entrega baseado no índice.
    
    0-25: A-Z
    26-51: A1-Z1
    52-77: A2-Z2
    E assim por diante.
    
    Args:
        index: Índice do ponto (0-based)
        
    Returns:
        String com o label (ex: 'A', 'Z', 'A1', 'B2')
    """
    letter = chr(65 + (index % 26))  # A-Z
    cycle = index // 26  # Qual ciclo (0, 1, 2, ...)
    
    if cycle == 0:
        return letter
    else:
        return f"{letter}{cycle}"


class GeneticOperators:
    """Classe com operadores genéticos para VRP."""
    
    @staticmethod
    def order_crossover_vrp(parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Order Crossover (OX) adaptado para VRP.
        
        Preserva a ordem relativa dos pontos enquanto permite troca de segmentos.
        Os separadores de veículos são ajustados para manter validade.
        
        Args:
            parent1: Primeiro pai
            parent2: Segundo pai
        
        Returns:
            Tupla com dois filhos
        """
        # Trabalhar apenas com os pontos (sem separadores)
        points1 = parent1.get_points()
        points2 = parent2.get_points()
        
        size = len(points1)
        
        # Escolher dois pontos de corte
        cx_point1 = random.randint(0, size - 1)
        cx_point2 = random.randint(cx_point1 + 1, size)
        
        # Filho 1: pegar segmento do pai 1
        child1_middle = points1[cx_point1:cx_point2]
        child1_middle_set = set(child1_middle)
        
        # Completar com pontos do pai 2 na ordem
        child1_points = []
        for point in points2:
            if point not in child1_middle_set:
                child1_points.append(point)
        
        # Inserir o segmento do meio na posição correta
        child1_points = child1_points[:cx_point1] + child1_middle + child1_points[cx_point1:]
        
        # Filho 2: mesmo processo invertido
        child2_middle = points2[cx_point1:cx_point2]
        child2_middle_set = set(child2_middle)
        
        child2_points = []
        for point in points1:
            if point not in child2_middle_set:
                child2_points.append(point)
        
        child2_points = child2_points[:cx_point1] + child2_middle + child2_points[cx_point1:]
        
        # Redistribuir separadores baseado nos pais
        child1_genes = GeneticOperators._add_separators_from_parent(child1_points, parent1)
        child2_genes = GeneticOperators._add_separators_from_parent(child2_points, parent2)
        
        # Criar cromossomos filhos
        child1 = Chromosome(child1_genes, parent1.num_vehicles)
        child2 = Chromosome(child2_genes, parent2.num_vehicles)
        
        # Configurar informações de genealogia
        child1.parent1_id = parent1.id
        child1.parent2_id = parent2.id
        child2.parent1_id = parent1.id
        child2.parent2_id = parent2.id
        
        # Reparar se necessário
        child1.repair(len(points1))
        child2.repair(len(points2))
        
        return child1, child2
    
    @staticmethod
    def _add_separators_from_parent(points: List[int], parent: Chromosome) -> List[int]:
        """
        Adiciona separadores baseado na estrutura do pai.
        
        Args:
            points: Lista de pontos sem separadores
            parent: Cromossomo pai para copiar estrutura
        
        Returns:
            Lista de genes com separadores
        """
        parent_routes = parent.get_routes()
        if not parent_routes:
            return points
        
        # Calcular proporção de pontos por rota no pai
        total_points = sum(len(r) for r in parent_routes)
        proportions = [len(r) / total_points for r in parent_routes]
        
        # Distribuir pontos proporcionalmente
        genes = []
        start = 0
        for i, prop in enumerate(proportions[:-1]):  # Última rota pega o que sobrar
            count = max(1, int(len(points) * prop))
            genes.extend(points[start:start+count])
            genes.append(-1)  # Separador
            start += count
        
        # Última rota
        genes.extend(points[start:])
        
        return genes
    
    @staticmethod
    def partially_mapped_crossover_vrp(parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Partially Mapped Crossover (PMX) adaptado para VRP.
        
        Cria mapeamento parcial entre segmentos dos pais.
        
        Args:
            parent1: Primeiro pai
            parent2: Segundo pai
        
        Returns:
            Tupla com dois filhos
        """
        points1 = parent1.get_points()
        points2 = parent2.get_points()
        size = len(points1)
        
        # Pontos de corte
        cx_point1 = random.randint(0, size - 2)
        cx_point2 = random.randint(cx_point1 + 1, size)
        
        # Criar filhos
        child1_points = [-1] * size
        child2_points = [-1] * size
        
        # Copiar segmentos do meio
        child1_points[cx_point1:cx_point2] = points1[cx_point1:cx_point2]
        child2_points[cx_point1:cx_point2] = points2[cx_point1:cx_point2]
        
        # Criar mapeamento
        mapping1to2 = {}
        mapping2to1 = {}
        for i in range(cx_point1, cx_point2):
            mapping1to2[points1[i]] = points2[i]
            mapping2to1[points2[i]] = points1[i]
        
        # Preencher restante
        for i in list(range(0, cx_point1)) + list(range(cx_point2, size)):
            # Filho 1
            val = points2[i]
            while val in mapping2to1:
                val = mapping2to1[val]
            child1_points[i] = val
            
            # Filho 2
            val = points1[i]
            while val in mapping1to2:
                val = mapping1to2[val]
            child2_points[i] = val
        
        # Adicionar separadores
        child1_genes = GeneticOperators._add_separators_from_parent(child1_points, parent1)
        child2_genes = GeneticOperators._add_separators_from_parent(child2_points, parent2)
        
        child1 = Chromosome(child1_genes, parent1.num_vehicles)
        child2 = Chromosome(child2_genes, parent2.num_vehicles)
        
        child1.parent1_id = parent1.id
        child1.parent2_id = parent2.id
        child2.parent1_id = parent1.id
        child2.parent2_id = parent2.id
        
        child1.repair(len(points1))
        child2.repair(len(points2))
        
        return child1, child2
    
    @staticmethod
    def swap_mutation(chromosome: Chromosome, num_points: int) -> Chromosome:
        """
        Mutação por troca (swap) de dois pontos.
        
        Args:
            chromosome: Cromossomo a ser mutado
            num_points: Número total de pontos
        
        Returns:
            Cromossomo mutado
        """
        mutant = chromosome.copy()
        points = mutant.get_points()
        
        if len(points) < 2:
            return mutant
        
        # Escolher dois pontos aleatórios para trocar
        idx1, idx2 = random.sample(range(len(points)), 2)
        
        # Encontrar posições nos genes (considerando separadores)
        point_indices = [i for i, g in enumerate(mutant.genes) if g != -1]
        gene_idx1 = point_indices[idx1]
        gene_idx2 = point_indices[idx2]
        
        # Trocar
        mutant.genes[gene_idx1], mutant.genes[gene_idx2] = mutant.genes[gene_idx2], mutant.genes[gene_idx1]
        mutant.mutation_applied = f"SWAP({get_point_label(points[idx1])},{get_point_label(points[idx2])})"
        
        return mutant
    
    @staticmethod
    def inversion_mutation(chromosome: Chromosome, num_points: int) -> Chromosome:
        """
        Mutação por inversão de um segmento.
        
        Args:
            chromosome: Cromossomo a ser mutado
            num_points: Número total de pontos
        
        Returns:
            Cromossomo mutado
        """
        mutant = chromosome.copy()
        points = mutant.get_points()
        
        if len(points) < 2:
            return mutant
        
        # Escolher segmento aleatório
        idx1 = random.randint(0, len(points) - 2)
        idx2 = random.randint(idx1 + 1, len(points))
        
        # Encontrar posições nos genes
        point_indices = [i for i, g in enumerate(mutant.genes) if g != -1]
        gene_idx1 = point_indices[idx1]
        gene_idx2 = point_indices[idx2-1]
        
        # Extrair segmento (apenas pontos, sem separadores)
        segment = []
        separators_pos = []
        for i in range(gene_idx1, gene_idx2+1):
            if mutant.genes[i] == -1:
                separators_pos.append(len(segment))
            else:
                segment.append(mutant.genes[i])
        
        # Inverter segmento
        segment.reverse()
        
        # Reconstruir com separadores nas mesmas posições relativas
        new_segment = []
        seg_idx = 0
        for pos in range(len(segment) + len(separators_pos)):
            if pos in separators_pos:
                new_segment.append(-1)
            else:
                new_segment.append(segment[seg_idx])
                seg_idx += 1
        
        # Substituir no cromossomo
        mutant.genes[gene_idx1:gene_idx2+1] = new_segment[:gene_idx2-gene_idx1+1]
        mutant.mutation_applied = f"INVERSION({idx1}-{idx2})"
        
        return mutant
    
    @staticmethod
    def move_mutation(chromosome: Chromosome, num_points: int) -> Chromosome:
        """
        Mutação movendo um ponto para outra rota.
        
        Args:
            chromosome: Cromossomo a ser mutado
            num_points: Número total de pontos
        
        Returns:
            Cromossomo mutado
        """
        mutant = chromosome.copy()
        routes = mutant.get_routes()
        
        if len(routes) < 2:
            return GeneticOperators.swap_mutation(mutant, num_points)
        
        # Escolher rota de origem e destino
        source_route_idx = random.randint(0, len(routes) - 1)
        dest_route_idx = random.randint(0, len(routes) - 1)
        
        while dest_route_idx == source_route_idx and len(routes) > 1:
            dest_route_idx = random.randint(0, len(routes) - 1)
        
        if not routes[source_route_idx]:
            return mutant
        
        # Escolher ponto aleatório da rota de origem
        point_idx = random.randint(0, len(routes[source_route_idx]) - 1)
        point = routes[source_route_idx].pop(point_idx)
        
        # Inserir em posição aleatória na rota de destino
        if routes[dest_route_idx]:
            insert_pos = random.randint(0, len(routes[dest_route_idx]))
        else:
            insert_pos = 0
        routes[dest_route_idx].insert(insert_pos, point)
        
        # Reconstruir genes
        new_genes = []
        for i, route in enumerate(routes):
            new_genes.extend(route)
            if i < len(routes) - 1 and route:  # Separador apenas se a rota não estiver vazia
                new_genes.append(-1)
        
        mutant.genes = new_genes
        mutant.mutation_applied = f"MOVE({get_point_label(point)}: V{source_route_idx+1}→V{dest_route_idx+1})"
        mutant.repair(num_points)
        
        return mutant
    
    @staticmethod
    def tournament_selection(population: List[Chromosome], tournament_size: int = 3) -> Chromosome:
        """
        Seleção por torneio.
        
        Args:
            population: População de cromossomos
            tournament_size: Tamanho do torneio
        
        Returns:
            Cromossomo vencedor
        """
        tournament = random.sample(population, min(tournament_size, len(population)))
        return min(tournament, key=lambda x: x.fitness)
    
    @staticmethod
    def roulette_selection(population: List[Chromosome]) -> Chromosome:
        """
        Seleção por roleta (fitness proporcional).
        
        Menor fitness = melhor, então invertemos os valores.
        
        Args:
            population: População de cromossomos
        
        Returns:
            Cromossomo selecionado
        """
        # Inverter fitness (menor é melhor, mas roleta precisa de valores maiores = melhor)
        max_fitness = max(c.fitness for c in population)
        min_fitness = min(c.fitness for c in population)
        
        if max_fitness == min_fitness:
            return random.choice(population)
        
        # Fitness ajustado: maior fitness ajustado = melhor
        adjusted_fitness = [max_fitness - c.fitness + 1 for c in population]
        total_fitness = sum(adjusted_fitness)
        
        # Roleta
        pick = random.uniform(0, total_fitness)
        current = 0
        for i, fitness in enumerate(adjusted_fitness):
            current += fitness
            if current >= pick:
                return population[i]
        
        return population[-1]

