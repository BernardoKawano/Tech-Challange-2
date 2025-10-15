"""
Modelo de Rota.

Define a estrutura de dados para representar uma rota
no sistema de otimização.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from .delivery_point import DeliveryPoint
from .vehicle import Vehicle


@dataclass
class Route:
    """
    Representa uma rota de entrega.
    
    Atributos:
        vehicle: Veículo alocado para a rota
        delivery_points: Lista de pontos de entrega na ordem
        depot_location: Localização do depósito (ponto de partida/chegada)
        total_distance_km: Distância total da rota em km
        total_duration_hours: Duração total estimada em horas
        total_cost: Custo total da rota
        is_valid: Se a rota é válida (respeita todas as restrições)
        violations: Lista de violações de restrições
    """
    
    vehicle: Vehicle
    delivery_points: List[DeliveryPoint] = field(default_factory=list)
    depot_location: Optional[Tuple[float, float]] = None
    total_distance_km: float = 0.0
    total_duration_hours: float = 0.0
    total_cost: float = 0.0
    is_valid: bool = True
    violations: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validação após inicialização."""
        if self.depot_location is None:
            self.depot_location = (-23.5505, -46.6333)  # Default: São Paulo
    
    def add_delivery_point(self, point: DeliveryPoint):
        """Adiciona um ponto de entrega à rota."""
        self.delivery_points.append(point)
    
    def get_num_deliveries(self) -> int:
        """Retorna o número de entregas na rota."""
        return len(self.delivery_points)
    
    def get_total_weight_kg(self) -> float:
        """Calcula o peso total da carga."""
        return sum(point.weight_kg for point in self.delivery_points)
    
    def get_total_volume_m3(self) -> float:
        """Calcula o volume total da carga."""
        return sum(point.volume_m3 for point in self.delivery_points)
    
    def get_total_service_time_hours(self) -> float:
        """Calcula o tempo total de serviço em horas."""
        total_minutes = sum(point.service_time_minutes for point in self.delivery_points)
        return total_minutes / 60.0
    
    def get_priority_distribution(self) -> dict:
        """Retorna a distribuição de prioridades na rota."""
        distribution = {
            'critico': 0,
            'alto': 0,
            'medio': 0,
            'baixo': 0
        }
        for point in self.delivery_points:
            distribution[point.priority.value] += 1
        return distribution
    
    def get_critical_deliveries(self) -> List[DeliveryPoint]:
        """Retorna lista de entregas críticas."""
        return [p for p in self.delivery_points if p.is_critical()]
    
    def has_critical_deliveries(self) -> bool:
        """Verifica se a rota possui entregas críticas."""
        return any(p.is_critical() for p in self.delivery_points)
    
    def calculate_priority_score(self) -> float:
        """Calcula pontuação baseada nas prioridades."""
        return sum(p.get_priority_weight() for p in self.delivery_points)
    
    def validate_capacity_constraints(self) -> bool:
        """Valida se a rota respeita as restrições de capacidade."""
        total_weight = self.get_total_weight_kg()
        total_volume = self.get_total_volume_m3()
        
        weight_ok = total_weight <= self.vehicle.capacity_kg
        volume_ok = total_volume <= self.vehicle.capacity_volume_m3
        
        if not weight_ok:
            self.violations.append(
                f"Excesso de peso: {total_weight:.2f}kg > {self.vehicle.capacity_kg}kg"
            )
        
        if not volume_ok:
            self.violations.append(
                f"Excesso de volume: {total_volume:.2f}m³ > {self.vehicle.capacity_volume_m3}m³"
            )
        
        return weight_ok and volume_ok
    
    def validate_autonomy_constraint(self) -> bool:
        """Valida se a rota respeita a autonomia do veículo."""
        autonomy_ok = self.total_distance_km <= self.vehicle.autonomy_km
        
        if not autonomy_ok:
            self.violations.append(
                f"Excesso de distância: {self.total_distance_km:.2f}km > {self.vehicle.autonomy_km}km"
            )
        
        return autonomy_ok
    
    def validate(self) -> bool:
        """
        Valida todas as restrições da rota.
        
        Returns:
            True se a rota é válida, False caso contrário
        """
        self.violations.clear()
        
        capacity_valid = self.validate_capacity_constraints()
        autonomy_valid = self.validate_autonomy_constraint()
        
        self.is_valid = capacity_valid and autonomy_valid
        
        return self.is_valid
    
    def get_efficiency_metrics(self) -> dict:
        """Retorna métricas de eficiência da rota."""
        return {
            'num_deliveries': self.get_num_deliveries(),
            'total_distance_km': self.total_distance_km,
            'total_duration_hours': self.total_duration_hours,
            'total_cost': self.total_cost,
            'capacity_usage_percent': self.vehicle.get_capacity_usage_percentage(),
            'autonomy_usage_percent': (self.total_distance_km / self.vehicle.autonomy_km) * 100,
            'priority_score': self.calculate_priority_score(),
            'is_valid': self.is_valid,
            'num_violations': len(self.violations)
        }
    
    def __repr__(self) -> str:
        return (f"Route(vehicle={self.vehicle.name}, deliveries={len(self.delivery_points)}, "
                f"distance={self.total_distance_km:.2f}km, valid={self.is_valid})")
    
    def to_dict(self) -> dict:
        """Converte a rota para dicionário."""
        return {
            'vehicle': self.vehicle.to_dict(),
            'delivery_points': [p.to_dict() for p in self.delivery_points],
            'depot_location': self.depot_location,
            'total_distance_km': self.total_distance_km,
            'total_duration_hours': self.total_duration_hours,
            'total_cost': self.total_cost,
            'is_valid': self.is_valid,
            'violations': self.violations,
            'metrics': self.get_efficiency_metrics()
        }

