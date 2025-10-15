"""
Modelo de Veículo.

Define a estrutura de dados para representar um veículo
no sistema de otimização de rotas.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Vehicle:
    """
    Representa um veículo no sistema de distribuição.
    
    Atributos:
        id: Identificador único do veículo
        name: Nome/identificação do veículo (ex: "Van 01")
        capacity_kg: Capacidade máxima de carga em kg
        capacity_volume_m3: Capacidade máxima de volume em m³
        autonomy_km: Autonomia máxima do veículo em km
        cost_per_km: Custo por quilômetro rodado
        average_speed_kmh: Velocidade média em km/h
        driver_name: Nome do motorista
        vehicle_type: Tipo do veículo
        is_refrigerated: Se o veículo possui refrigeração
        notes: Observações adicionais
    """
    
    id: int
    name: str
    capacity_kg: float
    capacity_volume_m3: float
    autonomy_km: float
    cost_per_km: float = 2.5
    average_speed_kmh: float = 40.0
    driver_name: str = ""
    vehicle_type: str = "Van"
    is_refrigerated: bool = False
    notes: str = ""
    
    # Atributos de estado durante a otimização (não serializados)
    current_load_kg: float = field(default=0.0, init=False, repr=False)
    current_volume_m3: float = field(default=0.0, init=False, repr=False)
    current_distance_km: float = field(default=0.0, init=False, repr=False)
    
    def __post_init__(self):
        """Validação após inicialização."""
        if self.capacity_kg <= 0:
            raise ValueError("Capacidade de peso deve ser positiva")
        if self.capacity_volume_m3 <= 0:
            raise ValueError("Capacidade de volume deve ser positiva")
        if self.autonomy_km <= 0:
            raise ValueError("Autonomia deve ser positiva")
        if self.average_speed_kmh <= 0:
            raise ValueError("Velocidade média deve ser positiva")
    
    def reset_state(self):
        """Reseta o estado atual do veículo."""
        self.current_load_kg = 0.0
        self.current_volume_m3 = 0.0
        self.current_distance_km = 0.0
    
    def can_add_load(self, weight_kg: float, volume_m3: float) -> bool:
        """
        Verifica se é possível adicionar uma carga ao veículo.
        
        Args:
            weight_kg: Peso a adicionar em kg
            volume_m3: Volume a adicionar em m³
            
        Returns:
            True se a carga cabe, False caso contrário
        """
        return (self.current_load_kg + weight_kg <= self.capacity_kg and
                self.current_volume_m3 + volume_m3 <= self.capacity_volume_m3)
    
    def add_load(self, weight_kg: float, volume_m3: float):
        """
        Adiciona carga ao veículo.
        
        Args:
            weight_kg: Peso a adicionar em kg
            volume_m3: Volume a adicionar em m³
            
        Raises:
            ValueError: Se a carga exceder a capacidade
        """
        if not self.can_add_load(weight_kg, volume_m3):
            raise ValueError(f"Carga excede capacidade do veículo {self.name}")
        
        self.current_load_kg += weight_kg
        self.current_volume_m3 += volume_m3
    
    def can_travel_distance(self, distance_km: float) -> bool:
        """
        Verifica se o veículo pode viajar uma determinada distância.
        
        Args:
            distance_km: Distância em km
            
        Returns:
            True se pode viajar, False caso contrário
        """
        return self.current_distance_km + distance_km <= self.autonomy_km
    
    def add_distance(self, distance_km: float):
        """
        Adiciona distância percorrida ao veículo.
        
        Args:
            distance_km: Distância em km
            
        Raises:
            ValueError: Se a distância exceder a autonomia
        """
        if not self.can_travel_distance(distance_km):
            raise ValueError(f"Distância excede autonomia do veículo {self.name}")
        
        self.current_distance_km += distance_km
    
    def get_remaining_capacity_kg(self) -> float:
        """Retorna a capacidade restante de peso."""
        return self.capacity_kg - self.current_load_kg
    
    def get_remaining_capacity_m3(self) -> float:
        """Retorna a capacidade restante de volume."""
        return self.capacity_volume_m3 - self.current_volume_m3
    
    def get_remaining_autonomy(self) -> float:
        """Retorna a autonomia restante."""
        return self.autonomy_km - self.current_distance_km
    
    def get_capacity_usage_percentage(self) -> float:
        """Retorna a porcentagem de uso da capacidade (baseado no maior limitante)."""
        weight_usage = (self.current_load_kg / self.capacity_kg) * 100
        volume_usage = (self.current_volume_m3 / self.capacity_volume_m3) * 100
        return max(weight_usage, volume_usage)
    
    def get_autonomy_usage_percentage(self) -> float:
        """Retorna a porcentagem de uso da autonomia."""
        return (self.current_distance_km / self.autonomy_km) * 100
    
    def calculate_route_cost(self) -> float:
        """Calcula o custo da rota percorrida."""
        return self.current_distance_km * self.cost_per_km
    
    def calculate_route_duration_hours(self) -> float:
        """Calcula a duração estimada da rota em horas."""
        return self.current_distance_km / self.average_speed_kmh
    
    def __repr__(self) -> str:
        return f"Vehicle(id={self.id}, name='{self.name}', capacity={self.capacity_kg}kg)"
    
    def to_dict(self) -> dict:
        """Converte o veículo para dicionário."""
        return {
            'id': self.id,
            'name': self.name,
            'capacity_kg': self.capacity_kg,
            'capacity_volume_m3': self.capacity_volume_m3,
            'autonomy_km': self.autonomy_km,
            'cost_per_km': self.cost_per_km,
            'average_speed_kmh': self.average_speed_kmh,
            'driver_name': self.driver_name,
            'vehicle_type': self.vehicle_type,
            'is_refrigerated': self.is_refrigerated,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Vehicle':
        """Cria um veículo a partir de um dicionário."""
        # Remover campos de estado se existirem
        state_fields = ['current_load_kg', 'current_volume_m3', 'current_distance_km']
        clean_data = {k: v for k, v in data.items() if k not in state_fields}
        return cls(**clean_data)

