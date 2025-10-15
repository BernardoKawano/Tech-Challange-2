"""
Representação genética (Cromossomo) para VRP.

Um cromossomo representa uma solução completa do problema de roteamento,
contendo as rotas de todos os veículos.
"""

from typing import List, Tuple
import random
import copy


class Chromosome:
    """
    Cromossomo para VRP com múltiplos veículos.
    
    Representação: Lista de índices de pontos com separadores de veículos.
    Exemplo: [1, 3, 5, -1, 2, 4, -1, 6, 7, 8]
    Significa: Veículo 1 visita pontos 1,3,5 | Veículo 2 visita 2,4 | Veículo 3 visita 6,7,8
    (-1 é o separador de veículos)
    """
    
    def __init__(self, genes: List[int], num_vehicles: int):
        """
        Inicializa um cromossomo.
        
        Args:
            genes: Lista de genes (índices de pontos + separadores -1)
            num_vehicles: Número de veículos disponíveis
        """
        self.genes = genes
        self.num_vehicles = num_vehicles
        self.fitness = float('inf')  # Menor é melhor
        self.fitness_components = {}  # Detalhamento do fitness
        self.generation = 0
        self.parent1_id = None
        self.parent2_id = None
        self.mutation_applied = None
        self.id = None  # Será atribuído pelo logger
        
    def get_routes(self) -> List[List[int]]:
        """
        Extrai as rotas individuais de cada veículo.
        
        Returns:
            Lista de rotas, onde cada rota é uma lista de índices de pontos
        """
        routes = []
        current_route = []
        
        for gene in self.genes:
            if gene == -1:  # Separador
                if current_route:  # Só adiciona se não estiver vazia
                    routes.append(current_route)
                    current_route = []
            else:
                current_route.append(gene)
        
        # Adicionar última rota se não estiver vazia
        if current_route:
            routes.append(current_route)
        
        return routes
    
    def get_num_active_vehicles(self) -> int:
        """Retorna o número de veículos realmente usados."""
        routes = self.get_routes()
        return len([r for r in routes if r])  # Contar apenas rotas não vazias
    
    def get_points(self) -> List[int]:
        """Retorna apenas os pontos (sem separadores)."""
        return [g for g in self.genes if g != -1]
    
    def is_valid(self) -> bool:
        """
        Verifica se o cromossomo é válido.
        
        Um cromossomo é válido se:
        1. Todos os pontos aparecem exatamente uma vez
        2. Não há rotas vazias consecutivas
        """
        points = self.get_points()
        
        # Verificar se todos os pontos são únicos
        if len(points) != len(set(points)):
            return False
        
        # Verificar se não há separadores consecutivos
        for i in range(len(self.genes) - 1):
            if self.genes[i] == -1 and self.genes[i+1] == -1:
                return False
        
        return True
    
    def repair(self, num_points: int):
        """
        Repara um cromossomo inválido.
        
        Args:
            num_points: Número total de pontos (0 a num_points-1)
        """
        # Extrair pontos atuais (sem separadores)
        current_points = self.get_points()
        all_points = set(range(num_points))
        present_points = set(current_points)
        
        # Encontrar pontos duplicados e faltantes
        missing = list(all_points - present_points)
        
        # Remover duplicatas
        seen = set()
        new_genes = []
        for gene in self.genes:
            if gene == -1:
                new_genes.append(gene)
            elif gene not in seen:
                seen.add(gene)
                new_genes.append(gene)
        
        # Adicionar pontos faltantes aleatoriamente
        if missing:
            random.shuffle(missing)
            points_only = [g for g in new_genes if g != -1]
            points_only.extend(missing)
            
            # Reconstruir com separadores
            routes = self.get_routes()
            if not routes:
                routes = [[]]
            
            # Distribuir pontos faltantes
            for point in missing:
                route_idx = random.randint(0, len(routes)-1)
                routes[route_idx].append(point)
            
            # Reconstruir genes
            new_genes = []
            for i, route in enumerate(routes):
                new_genes.extend(route)
                if i < len(routes) - 1:
                    new_genes.append(-1)
        
        self.genes = new_genes
        
        # Remover separadores consecutivos
        cleaned = []
        prev_was_sep = False
        for gene in self.genes:
            if gene == -1:
                if not prev_was_sep and cleaned:  # Não adicionar separador no início ou consecutivo
                    cleaned.append(gene)
                    prev_was_sep = True
            else:
                cleaned.append(gene)
                prev_was_sep = False
        
        # Remover separador final se existir
        if cleaned and cleaned[-1] == -1:
            cleaned.pop()
        
        self.genes = cleaned
    
    def copy(self):
        """Cria uma cópia profunda do cromossomo."""
        new_chrom = Chromosome(copy.deepcopy(self.genes), self.num_vehicles)
        new_chrom.fitness = self.fitness
        new_chrom.fitness_components = copy.deepcopy(self.fitness_components)
        new_chrom.generation = self.generation
        new_chrom.parent1_id = self.parent1_id
        new_chrom.parent2_id = self.parent2_id
        new_chrom.mutation_applied = self.mutation_applied
        return new_chrom
    
    def to_string(self, point_labels: List[str] = None) -> str:
        """
        Converte o cromossomo em string legível.
        
        Args:
            point_labels: Lista de rótulos para os pontos (A, B, C...)
        
        Returns:
            String representando as rotas
        """
        routes = self.get_routes()
        route_strs = []
        
        for i, route in enumerate(routes):
            if point_labels:
                points_str = ','.join([point_labels[p] for p in route])
            else:
                points_str = ','.join([str(p) for p in route])
            route_strs.append(f"V{i+1}:[{points_str}]")
        
        return ' | '.join(route_strs)
    
    def __repr__(self):
        """Representação string do cromossomo."""
        return f"Chromosome(fitness={self.fitness:.2f}, routes={self.get_num_active_vehicles()}, genes={self.to_string()})"
    
    def __lt__(self, other):
        """Comparação para ordenação (menor fitness é melhor)."""
        return self.fitness < other.fitness
    
    @staticmethod
    def create_random(num_points: int, num_vehicles: int) -> 'Chromosome':
        """
        Cria um cromossomo aleatório válido.
        
        Args:
            num_points: Número total de pontos de entrega
            num_vehicles: Número de veículos disponíveis
        
        Returns:
            Cromossomo aleatório válido
        """
        # Embaralhar pontos
        points = list(range(num_points))
        random.shuffle(points)
        
        # Dividir aleatoriamente entre veículos
        # Garantir que cada veículo tenha pelo menos 1 ponto (se possível)
        if num_points >= num_vehicles:
            # Dividir em partes aproximadamente iguais
            points_per_vehicle = num_points // num_vehicles
            remainder = num_points % num_vehicles
            
            genes = []
            start_idx = 0
            for v in range(num_vehicles):
                # Alguns veículos pegam 1 ponto extra
                end_idx = start_idx + points_per_vehicle + (1 if v < remainder else 0)
                
                # Adicionar pontos deste veículo
                genes.extend(points[start_idx:end_idx])
                
                # Adicionar separador (exceto no último)
                if v < num_vehicles - 1:
                    genes.append(-1)
                
                start_idx = end_idx
        else:
            # Menos pontos que veículos: alguns veículos ficam vazios
            genes = points.copy()
            # Adicionar alguns separadores aleatoriamente
            num_separators = min(num_vehicles - 1, num_points - 1)
            if num_separators > 0:
                # Posições válidas para inserir separadores
                positions = random.sample(range(1, len(genes)), num_separators)
                positions.sort(reverse=True)
                for pos in positions:
                    genes.insert(pos, -1)
        
        chromosome = Chromosome(genes, num_vehicles)
        chromosome.repair(num_points)  # Garantir validade
        return chromosome

