"""
Modelo de Ponto de Entrega.

Define a estrutura de dados para representar um ponto de entrega
no sistema de otimização de rotas.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


class Priority(Enum):
    """Enum para prioridades de entrega."""
    CRITICO = "critico"
    ALTO = "alto"
    MEDIO = "medio"
    BAIXO = "baixo"
    
    def get_weight(self) -> int:
        """Retorna o peso da prioridade para cálculo de fitness."""
        weights = {
            Priority.CRITICO: 10,
            Priority.ALTO: 5,
            Priority.MEDIO: 2,
            Priority.BAIXO: 1
        }
        return weights[self]
    
    def get_max_delay_hours(self) -> int:
        """Retorna o atraso máximo permitido em horas."""
        delays = {
            Priority.CRITICO: 0,
            Priority.ALTO: 2,
            Priority.MEDIO: 6,
            Priority.BAIXO: 24
        }
        return delays[self]


@dataclass
class DeliveryPoint:
    """
    Representa um ponto de entrega no sistema.
    
    Atributos:
        id: Identificador único do ponto
        name: Nome do local/paciente
        latitude: Latitude do ponto
        longitude: Longitude do ponto
        address: Endereço completo
        priority: Prioridade da entrega
        weight_kg: Peso da carga em kg
        volume_m3: Volume da carga em m³
        time_window_start: Início da janela de tempo (opcional)
        time_window_end: Fim da janela de tempo (opcional)
        service_time_minutes: Tempo de serviço no local em minutos
        notes: Observações adicionais
        item_description: Descrição dos itens a entregar
    """
    
    id: int
    name: str
    latitude: float
    longitude: float
    address: str
    priority: Priority
    weight_kg: float
    volume_m3: float
    time_window_start: Optional[datetime] = None
    time_window_end: Optional[datetime] = None
    service_time_minutes: int = 10
    notes: str = ""
    item_description: str = ""
    
    def __post_init__(self):
        """Validação após inicialização."""
        if self.weight_kg < 0:
            raise ValueError("Peso não pode ser negativo")
        if self.volume_m3 < 0:
            raise ValueError("Volume não pode ser negativo")
        if self.service_time_minutes < 0:
            raise ValueError("Tempo de serviço não pode ser negativo")
    
    def get_coordinates(self) -> Tuple[float, float]:
        """Retorna as coordenadas como tupla (latitude, longitude)."""
        return (self.latitude, self.longitude)
    
    def get_priority_weight(self) -> int:
        """Retorna o peso da prioridade."""
        return self.priority.get_weight()
    
    def is_critical(self) -> bool:
        """Verifica se a entrega é crítica."""
        return self.priority == Priority.CRITICO
    
    def has_time_window(self) -> bool:
        """Verifica se há janela de tempo definida."""
        return self.time_window_start is not None and self.time_window_end is not None
    
    def __repr__(self) -> str:
        return f"DeliveryPoint(id={self.id}, name='{self.name}', priority={self.priority.value})"
    
    def to_dict(self) -> dict:
        """Converte o ponto de entrega para dicionário."""
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'priority': self.priority.value,
            'weight_kg': self.weight_kg,
            'volume_m3': self.volume_m3,
            'time_window_start': self.time_window_start.isoformat() if self.time_window_start else None,
            'time_window_end': self.time_window_end.isoformat() if self.time_window_end else None,
            'service_time_minutes': self.service_time_minutes,
            'notes': self.notes,
            'item_description': self.item_description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DeliveryPoint':
        """Cria um ponto de entrega a partir de um dicionário."""
        # Converter string de prioridade para enum
        if isinstance(data.get('priority'), str):
            data['priority'] = Priority(data['priority'])
        
        # Converter strings de datetime se existirem
        if data.get('time_window_start'):
            data['time_window_start'] = datetime.fromisoformat(data['time_window_start'])
        if data.get('time_window_end'):
            data['time_window_end'] = datetime.fromisoformat(data['time_window_end'])
        
        return cls(**data)

