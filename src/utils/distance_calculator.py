"""
Módulo para cálculo de distâncias entre coordenadas geográficas.

Fornece funções para calcular distâncias Euclidianas e Haversine,
além de criar matrizes de distância com cache.
"""

import math
from typing import List, Tuple, Dict
import numpy as np


def euclidean_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calcula distância Euclidiana entre duas coordenadas.
    
    Args:
        coord1: Tupla (lat, lon) do primeiro ponto
        coord2: Tupla (lat, lon) do segundo ponto
    
    Returns:
        Distância Euclidiana
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)


def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calcula distância Haversine entre duas coordenadas geográficas.
    
    Esta é a distância real na superfície da Terra considerando sua curvatura.
    
    Args:
        coord1: Tupla (lat, lon) do primeiro ponto
        coord2: Tupla (lat, lon) do segundo ponto
    
    Returns:
        Distância em quilômetros
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Raio da Terra em km
    R = 6371.0
    
    # Converter para radianos
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Fórmula de Haversine
    a = math.sin(delta_lat / 2)**2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def create_distance_matrix(coordinates: List[Tuple[float, float]], 
                          depot_coord: Tuple[float, float],
                          use_haversine: bool = True) -> np.ndarray:
    """
    Cria matriz de distâncias entre todos os pontos (incluindo depósito).
    
    Args:
        coordinates: Lista de coordenadas dos pontos de entrega
        depot_coord: Coordenada do depósito
        use_haversine: Se True, usa distância Haversine. Se False, usa Euclidiana.
    
    Returns:
        Matriz NumPy onde matrix[i][j] é a distância do ponto i ao ponto j
        Índice 0 é sempre o depósito
    """
    # Adicionar depósito no início
    all_coords = [depot_coord] + list(coordinates)
    n = len(all_coords)
    
    # Escolher função de distância
    dist_func = haversine_distance if use_haversine else euclidean_distance
    
    # Criar matriz
    matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = dist_func(all_coords[i], all_coords[j])
    
    return matrix


class DistanceCache:
    """
    Cache para armazenar distâncias calculadas e evitar recalcular.
    
    Útil quando a mesma distância é consultada múltiplas vezes durante
    a execução do algoritmo genético.
    """
    
    def __init__(self, use_haversine: bool = True):
        """
        Inicializa o cache.
        
        Args:
            use_haversine: Se True, usa Haversine. Se False, usa Euclidiana.
        """
        self.cache: Dict[Tuple[Tuple[float, float], Tuple[float, float]], float] = {}
        self.use_haversine = use_haversine
        self.dist_func = haversine_distance if use_haversine else euclidean_distance
    
    def get_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """
        Obtém distância entre duas coordenadas (usa cache se disponível).
        
        Args:
            coord1: Primeira coordenada
            coord2: Segunda coordenada
        
        Returns:
            Distância entre os pontos
        """
        # Criar chave ordenada (para que (A,B) e (B,A) sejam iguais)
        key = tuple(sorted([coord1, coord2]))
        
        if key not in self.cache:
            self.cache[key] = self.dist_func(coord1, coord2)
        
        return self.cache[key]
    
    def clear_cache(self):
        """Limpa o cache."""
        self.cache.clear()
    
    def cache_size(self) -> int:
        """Retorna número de distâncias em cache."""
        return len(self.cache)


def calculate_route_distance(route_coords: List[Tuple[float, float]], 
                            depot_coord: Tuple[float, float],
                            use_haversine: bool = True,
                            return_to_depot: bool = True) -> float:
    """
    Calcula distância total de uma rota.
    
    Args:
        route_coords: Lista ordenada de coordenadas da rota
        depot_coord: Coordenada do depósito
        use_haversine: Se True, usa Haversine. Se False, usa Euclidiana.
        return_to_depot: Se True, inclui distância de volta ao depósito
    
    Returns:
        Distância total da rota em km
    """
    if not route_coords:
        return 0.0
    
    dist_func = haversine_distance if use_haversine else euclidean_distance
    total_distance = 0.0
    
    # Distância do depósito ao primeiro ponto
    total_distance += dist_func(depot_coord, route_coords[0])
    
    # Distância entre pontos consecutivos
    for i in range(len(route_coords) - 1):
        total_distance += dist_func(route_coords[i], route_coords[i + 1])
    
    # Distância do último ponto de volta ao depósito
    if return_to_depot:
        total_distance += dist_func(route_coords[-1], depot_coord)
    
    return total_distance


# Exemplo de uso
if __name__ == '__main__':
    # Coordenadas de exemplo (São Paulo)
    depot = (-23.5505, -46.6333)  # Av. Paulista
    point1 = (-23.5880, -46.6400)  # Zona Sul
    point2 = (-23.5650, -46.6520)  # Zona Oeste
    
    print("Exemplos de Cálculo de Distância:")
    print("-" * 50)
    
    # Euclidiana
    dist_eucl = euclidean_distance(depot, point1)
    print(f"Euclidiana (depot → point1): {dist_eucl:.4f}")
    
    # Haversine
    dist_hav = haversine_distance(depot, point1)
    print(f"Haversine (depot → point1): {dist_hav:.2f} km")
    
    # Matriz de distâncias
    coords = [point1, point2]
    matrix = create_distance_matrix(coords, depot, use_haversine=True)
    print(f"\nMatriz de Distâncias (3x3):")
    print(matrix)
    
    # Distância de rota
    route_dist = calculate_route_distance([point1, point2], depot, use_haversine=True)
    print(f"\nDistância da rota (depot → p1 → p2 → depot): {route_dist:.2f} km")
    
    # Cache
    print("\n" + "-" * 50)
    print("Teste de Cache:")
    cache = DistanceCache(use_haversine=True)
    
    # Primeira chamada (calcula)
    d1 = cache.get_distance(depot, point1)
    print(f"Distância (depot → point1): {d1:.2f} km")
    print(f"Tamanho do cache: {cache.cache_size()}")
    
    # Segunda chamada (usa cache)
    d2 = cache.get_distance(point1, depot)  # Ordem invertida
    print(f"Distância (point1 → depot): {d2:.2f} km (do cache)")
    print(f"Tamanho do cache: {cache.cache_size()}")  # Ainda é 1

