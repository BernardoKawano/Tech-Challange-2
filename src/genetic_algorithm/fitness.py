"""
Função Fitness Multi-Critério para VRP.

Calcula o fitness considerando múltiplos objetivos e restrições.
"""

from typing import List, Dict, Tuple
import math
from ..models.delivery_point import DeliveryPoint
from ..models.vehicle import Vehicle
from ..utils.distance_calculator import haversine_distance
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


class FitnessCalculator:
    """Calculadora de fitness multi-critério."""
    
    def __init__(self, 
                 delivery_points: List[DeliveryPoint],
                 vehicles: List[Vehicle],
                 depot_coord: Tuple[float, float],
                 weights: Dict[str, float] = None):
        """
        Inicializa o calculador de fitness.
        
        Args:
            delivery_points: Lista de pontos de entrega
            vehicles: Lista de veículos disponíveis
            depot_coord: Coordenadas do depósito (lat, lon)
            weights: Pesos para cada componente do fitness
        """
        self.delivery_points = delivery_points
        self.vehicles = vehicles
        self.depot_coord = depot_coord
        
        # Pesos padrão
        self.weights = weights or {
            'distance': 1.0,          # Minimizar distância total
            'capacity': 10.0,         # Penalidade por violar capacidade
            'autonomy': 10.0,         # Penalidade por violar autonomia
            'priority': 5.0,          # Bonificação por atender prioridades
            'balance': 2.0,           # Penalidade por desbalanceamento
            'num_vehicles': 3.0       # Penalidade por usar mais veículos
        }
        
        # Cache de distâncias
        self._distance_cache = {}
        self._precompute_distances()
    
    def _precompute_distances(self):
        """Pré-calcula matriz de distâncias."""
        n = len(self.delivery_points)
        
        # Distância do depósito para cada ponto
        for i in range(n):
            point_coord = self.delivery_points[i].get_coordinates()
            key = ('depot', i)
            self._distance_cache[key] = haversine_distance(self.depot_coord, point_coord)
        
        # Distância entre todos os pares de pontos
        for i in range(n):
            for j in range(i+1, n):
                coord_i = self.delivery_points[i].get_coordinates()
                coord_j = self.delivery_points[j].get_coordinates()
                dist = haversine_distance(coord_i, coord_j)
                self._distance_cache[(i, j)] = dist
                self._distance_cache[(j, i)] = dist
    
    def get_distance(self, from_idx: int, to_idx: int) -> float:
        """
        Obtém distância entre dois pontos (ou depósito).
        
        Args:
            from_idx: Índice do ponto de origem (-1 para depósito)
            to_idx: Índice do ponto de destino (-1 para depósito)
        
        Returns:
            Distância em km
        """
        if from_idx == -1:
            key = ('depot', to_idx)
        elif to_idx == -1:
            key = ('depot', from_idx)
        else:
            key = (from_idx, to_idx) if from_idx < to_idx else (to_idx, from_idx)
        
        return self._distance_cache.get(key, 0)
    
    def calculate_fitness(self, chromosome: Chromosome) -> float:
        """
        Calcula fitness multi-critério do cromossomo.
        
        Args:
            chromosome: Cromossomo a ser avaliado
        
        Returns:
            Fitness total (menor é melhor)
        """
        routes = chromosome.get_routes()
        
        # Componentes do fitness
        total_distance = 0
        capacity_penalty = 0
        autonomy_penalty = 0
        priority_penalty = 0
        balance_penalty = 0
        num_vehicles_penalty = 0
        
        route_distances = []
        route_loads = []
        
        # Avaliar cada rota
        for route_idx, route in enumerate(routes):
            if not route:  # Rota vazia
                continue
            
            # Selecionar veículo (rotativo ou pelo índice)
            vehicle_idx = route_idx % len(self.vehicles)
            vehicle = self.vehicles[vehicle_idx]
            
            # Calcular distância da rota
            route_distance = self.get_distance(-1, route[0])  # Depósito -> primeiro ponto
            for i in range(len(route) - 1):
                route_distance += self.get_distance(route[i], route[i+1])
            route_distance += self.get_distance(route[-1], -1)  # Último ponto -> depósito
            
            route_distances.append(route_distance)
            total_distance += route_distance
            
            # Verificar autonomia
            if route_distance > vehicle.autonomy_km:
                autonomy_penalty += (route_distance - vehicle.autonomy_km) ** 2
            
            # Calcular carga
            total_weight = sum(self.delivery_points[p].weight_kg for p in route)
            total_volume = sum(self.delivery_points[p].volume_m3 for p in route)
            
            route_loads.append(total_weight)
            
            # Verificar capacidade
            if total_weight > vehicle.capacity_kg:
                capacity_penalty += (total_weight - vehicle.capacity_kg) ** 2
            
            if total_volume > vehicle.capacity_volume_m3:
                capacity_penalty += (total_volume - vehicle.capacity_volume_m3) ** 2 * 10  # Volume é mais crítico
            
            # Avaliar prioridades
            for position, point_idx in enumerate(route):
                point = self.delivery_points[point_idx]
                priority_val = point.priority.value
                
                # Pontos críticos devem ser visitados primeiro
                if priority_val == 'critico':
                    if position > len(route) // 3:  # Se não estiver no primeiro terço
                        priority_penalty += 100 * (position / len(route))
                elif priority_val == 'alto':
                    if position > 2 * len(route) // 3:  # Se não estiver nos primeiros 2/3
                        priority_penalty += 50 * (position / len(route))
        
        # Penalidade por desbalanceamento
        if route_loads:
            avg_load = sum(route_loads) / len(route_loads)
            balance_penalty = sum((load - avg_load) ** 2 for load in route_loads) / len(route_loads)
        
        # Penalidade por número de veículos
        num_active_vehicles = len([r for r in routes if r])
        num_vehicles_penalty = num_active_vehicles
        
        # Fitness total (combinação ponderada)
        fitness = (
            self.weights['distance'] * total_distance +
            self.weights['capacity'] * capacity_penalty +
            self.weights['autonomy'] * autonomy_penalty +
            self.weights['priority'] * priority_penalty +
            self.weights['balance'] * balance_penalty +
            self.weights['num_vehicles'] * num_vehicles_penalty
        )
        
        # Armazenar componentes para análise
        chromosome.fitness_components = {
            'total_distance': total_distance,
            'capacity_penalty': capacity_penalty,
            'autonomy_penalty': autonomy_penalty,
            'priority_penalty': priority_penalty,
            'balance_penalty': balance_penalty,
            'num_vehicles': num_active_vehicles,
            'route_distances': route_distances,
            'route_loads': route_loads
        }
        
        chromosome.fitness = fitness
        return fitness
    
    def get_detailed_metrics(self, chromosome: Chromosome) -> Dict:
        """
        Obtém métricas detalhadas do cromossomo.
        
        Args:
            chromosome: Cromossomo a ser analisado
        
        Returns:
            Dicionário com métricas detalhadas
        """
        if not chromosome.fitness_components:
            self.calculate_fitness(chromosome)
        
        comp = chromosome.fitness_components
        routes = chromosome.get_routes()
        
        metrics = {
            'fitness': chromosome.fitness,
            'total_distance_km': comp['total_distance'],
            'num_vehicles_used': comp['num_vehicles'],
            'capacity_violations': comp['capacity_penalty'] > 0,
            'autonomy_violations': comp['autonomy_penalty'] > 0,
            'priority_violations': comp['priority_penalty'] > 0,
            'avg_route_distance': sum(comp['route_distances']) / len(comp['route_distances']) if comp['route_distances'] else 0,
            'max_route_distance': max(comp['route_distances']) if comp['route_distances'] else 0,
            'min_route_distance': min(comp['route_distances']) if comp['route_distances'] else 0,
            'avg_vehicle_load': sum(comp['route_loads']) / len(comp['route_loads']) if comp['route_loads'] else 0,
            'total_deliveries': sum(len(r) for r in routes),
            'routes': []
        }
        
        # Detalhes de cada rota
        for i, route in enumerate(routes):
            if not route:
                continue
            
            vehicle_idx = i % len(self.vehicles)
            vehicle = self.vehicles[vehicle_idx]
            
            route_info = {
                'vehicle_id': vehicle_idx + 1,
                'vehicle_name': vehicle.name if hasattr(vehicle, 'name') else f"Veículo {vehicle_idx+1}",
                'num_deliveries': len(route),
                'distance_km': comp['route_distances'][i] if i < len(comp['route_distances']) else 0,
                'autonomy_km': vehicle.autonomy_km,  # ADICIONADO: autonomia do veículo
                'load_kg': comp['route_loads'][i] if i < len(comp['route_loads']) else 0,
                'capacity_kg': vehicle.capacity_kg,
                'capacity_usage_%': (comp['route_loads'][i] / vehicle.capacity_kg * 100) if i < len(comp['route_loads']) else 0,
                'points': [get_point_label(p) for p in route]
            }
            metrics['routes'].append(route_info)
        
        return metrics

