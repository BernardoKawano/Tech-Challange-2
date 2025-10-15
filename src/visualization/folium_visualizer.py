"""
Visualizador de Rotas usando Folium (Mapas HTML Interativos).

Este módulo cria mapas interativos em HTML mostrando as rotas otimizadas
pelo Algoritmo Genético em um mapa real de São Paulo.
"""
import folium
from folium import plugins
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from datetime import datetime


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


class FoliumVisualizer:
    """Cria mapas interativos HTML das rotas otimizadas."""
    
    # Cores por prioridade
    PRIORITY_COLORS = {
        'CRITICO': 'red',
        'ALTO': 'orange',
        'MEDIO': 'lightblue',
        'BAIXO': 'green'
    }
    
    # Ícones por prioridade
    PRIORITY_ICONS = {
        'CRITICO': 'exclamation-sign',
        'ALTO': 'warning-sign',
        'MEDIO': 'info-sign',
        'BAIXO': 'ok-sign'
    }
    
    # Cores por veículo (mesmas do Pygame)
    VEHICLE_COLORS = [
        '#FF6464',  # Vermelho
        '#6496FF',  # Azul
        '#64C864',  # Verde
        '#FFC864',  # Laranja
        '#C864FF'   # Roxo
    ]
    
    def __init__(self, center: Tuple[float, float] = (-23.550520, -46.633308)):
        """
        Inicializa visualizador.
        
        Args:
            center: Coordenadas do centro do mapa (lat, lon)
                   Padrão: Centro de São Paulo
        """
        self.center = center
        self.depot_location = center
    
    def create_map(
        self,
        delivery_points: List[Dict],
        routes: List[List[int]],
        vehicles: List[Dict],
        zoom_start: int = 12,
        show_route_arrows: bool = True
    ) -> folium.Map:
        """
        Cria mapa interativo com rotas otimizadas.
        
        Args:
            delivery_points: Lista de pontos de entrega com coordenadas
            routes: Lista de rotas (cada rota é lista de índices de pontos)
            vehicles: Lista de dados dos veículos
            zoom_start: Nível de zoom inicial (padrão: 12)
            show_route_arrows: Mostrar setas animadas nas rotas (padrão: True)
            
        Returns:
            Objeto folium.Map pronto para ser salvo
        """
        
        # Criar mapa base
        mapa = folium.Map(
            location=self.center,
            zoom_start=zoom_start,
            tiles='OpenStreetMap'
        )
        
        # Adicionar controle de tela cheia
        plugins.Fullscreen().add_to(mapa)
        
        # Adicionar mini mapa
        minimap = plugins.MiniMap()
        mapa.add_child(minimap)
        
        # Adicionar depósito
        self._add_depot(mapa)
        
        # Adicionar rotas (antes dos pontos para ficarem embaixo)
        self._add_routes(mapa, routes, delivery_points, vehicles, show_route_arrows)
        
        # Adicionar pontos de entrega (por cima das rotas)
        self._add_delivery_points(mapa, delivery_points)
        
        # Adicionar legenda
        self._add_legend(mapa, len(routes), len(delivery_points))
        
        return mapa
    
    def _add_depot(self, mapa: folium.Map):
        """Adiciona marcador do depósito central."""
        folium.Marker(
            location=self.depot_location,
            popup=folium.Popup(
                '<div style="font-family: Arial; width: 220px;">'
                '<h3 style="margin: 0; color: #333;">🏠 DEPÓSITO CENTRAL</h3>'
                '<hr style="margin: 5px 0; border: 1px solid #ddd;">'
                '<p style="margin: 5px 0;"><b>Hospital Central</b></p>'
                '<p style="margin: 5px 0; font-size: 12px; color: #666;">'
                'Ponto de partida e retorno de todos os veículos'
                '</p>'
                '<p style="margin: 5px 0; font-size: 11px; color: #999;">'
                f'Coordenadas: {self.depot_location[0]:.4f}, {self.depot_location[1]:.4f}'
                '</p>'
                '</div>',
                max_width=250
            ),
            tooltip='🏠 Depósito Central - Clique para detalhes',
            icon=folium.Icon(
                color='black',
                icon='home',
                prefix='glyphicon'
            )
        ).add_to(mapa)
        
        # Adicionar círculo ao redor do depósito
        folium.Circle(
            location=self.depot_location,
            radius=500,  # 500 metros
            color='black',
            fill=True,
            fillColor='gray',
            fillOpacity=0.1,
            popup='Área do depósito (500m)'
        ).add_to(mapa)
    
    def _add_delivery_points(self, mapa: folium.Map, points: List[Dict]):
        """Adiciona marcadores dos pontos de entrega."""
        for i, point in enumerate(points):
            # Determinar cor e ícone por prioridade
            priority = point.get('priority', 'MEDIO')
            color = self.PRIORITY_COLORS.get(priority, 'blue')
            icon_type = self.PRIORITY_ICONS.get(priority, 'info-sign')
            
            # Emojis de prioridade
            priority_emoji = {
                'CRITICO': '🔴',
                'ALTO': '🟠',
                'MEDIO': '🟡',
                'BAIXO': '🟢'
            }.get(priority, '⚪')
            
            # Criar popup com informações detalhadas
            popup_html = f"""
            <div style="font-family: Arial; width: 260px;">
                <h3 style="margin: 0; color: #333; font-size: 16px;">
                    {priority_emoji} {point.get('name', f'Ponto {i+1}')}
                </h3>
                <hr style="margin: 5px 0; border: 1px solid #ddd;">
                
                <table style="width: 100%; font-size: 13px; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 3px 5px; font-weight: bold; width: 40%;">Prioridade:</td>
                        <td style="padding: 3px 5px;">{priority}</td>
                    </tr>
                    <tr style="background-color: #f5f5f5;">
                        <td style="padding: 3px 5px; font-weight: bold;">Carga:</td>
                        <td style="padding: 3px 5px;">{point.get('weight', 'N/A')} kg</td>
                    </tr>
                    <tr>
                        <td style="padding: 3px 5px; font-weight: bold;">Volume:</td>
                        <td style="padding: 3px 5px;">{point.get('volume', 'N/A')} m³</td>
                    </tr>
                    <tr style="background-color: #f5f5f5;">
                        <td style="padding: 3px 5px; font-weight: bold;">Tempo Serviço:</td>
                        <td style="padding: 3px 5px;">{point.get('service_time_min', 'N/A')} min</td>
                    </tr>
                </table>
                
                <p style="margin: 8px 0 5px 0; font-size: 12px; color: #666; line-height: 1.4;">
                    {point.get('description', 'Sem descrição disponível')}
                </p>
                
                <p style="margin: 5px 0 0 0; font-size: 10px; color: #999;">
                    Coordenadas: {point['latitude']:.4f}, {point['longitude']:.4f}
                </p>
            </div>
            """
            
            # Criar tooltip (aparece ao passar o mouse)
            label = get_point_label(i)
            tooltip_text = f"{label} - {point.get('name', f'Ponto {i+1}')} ({priority})"
            
            # Adicionar marcador
            folium.Marker(
                location=[point['latitude'], point['longitude']],
                popup=folium.Popup(popup_html, max_width=280),
                tooltip=tooltip_text,
                icon=folium.Icon(
                    color=color,
                    icon=icon_type,
                    prefix='glyphicon'
                )
            ).add_to(mapa)
            
            # Adicionar label com letra (A, B, C... A1, B1, ...)
            folium.Marker(
                location=[point['latitude'], point['longitude']],
                icon=folium.DivIcon(
                    html=f'''
                    <div style="
                        font-size: 14px;
                        font-weight: bold;
                        color: white;
                        text-align: center;
                        text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
                        margin-top: -40px;
                        margin-left: 5px;
                    ">
                        {label}
                    </div>
                    '''
                )
            ).add_to(mapa)
    
    def _add_routes(
        self,
        mapa: folium.Map,
        routes: List[List[int]],
        points: List[Dict],
        vehicles: List[Dict],
        show_arrows: bool
    ):
        """Adiciona linhas das rotas no mapa."""
        for vehicle_idx, route in enumerate(routes):
            if not route:
                continue
            
            # Coordenadas da rota (depósito → pontos → depósito)
            coords = [self.depot_location]
            
            for point_idx in route:
                if point_idx < len(points):
                    point = points[point_idx]
                    coords.append([point['latitude'], point['longitude']])
            
            coords.append(self.depot_location)  # Retorna ao depósito
            
            # Cor do veículo
            color = self.VEHICLE_COLORS[vehicle_idx % len(self.VEHICLE_COLORS)]
            
            # Nome do veículo
            vehicle_name = vehicles[vehicle_idx].get('name', f'Veículo {vehicle_idx + 1}') if vehicle_idx < len(vehicles) else f'Veículo {vehicle_idx + 1}'
            
            # Informações da rota para popup
            num_deliveries = len(route)
            route_letters = ' → '.join([get_point_label(idx) for idx in route])
            
            popup_text = f'''
            <div style="font-family: Arial; width: 200px;">
                <h4 style="margin: 0; color: {color};">{vehicle_name}</h4>
                <hr style="margin: 5px 0;">
                <p style="margin: 3px 0;"><b>Entregas:</b> {num_deliveries}</p>
                <p style="margin: 3px 0; font-size: 11px;"><b>Sequência:</b><br>Depósito → {route_letters} → Depósito</p>
            </div>
            '''
            
            # Criar linha da rota
            folium.PolyLine(
                coords,
                color=color,
                weight=5,
                opacity=0.8,
                popup=folium.Popup(popup_text, max_width=220),
                tooltip=f'{vehicle_name} - {num_deliveries} entregas'
            ).add_to(mapa)
            
            # Adicionar setas de direção animadas
            if show_arrows:
                plugins.AntPath(
                    coords,
                    color=color,
                    weight=3,
                    opacity=0.6,
                    delay=1200,
                    dashArray=[10, 20],
                    pulseColor='white'
                ).add_to(mapa)
    
    def _add_legend(self, mapa: folium.Map, num_vehicles: int, num_points: int):
        """Adiciona legenda interativa ao mapa."""
        
        # Construir HTML da legenda
        legend_html = f'''
        <div style="
            position: fixed; 
            bottom: 50px; 
            right: 50px; 
            width: 320px; 
            background-color: white; 
            border: 3px solid #666; 
            border-radius: 8px; 
            padding: 15px; 
            font-family: Arial, sans-serif;
            font-size: 13px; 
            z-index: 9999;
            box-shadow: 3px 3px 10px rgba(0,0,0,0.4);
        ">
            <h3 style="margin-top: 0; margin-bottom: 10px; color: #333; border-bottom: 2px solid #ddd; padding-bottom: 5px;">
                📊 LEGENDA DO MAPA
            </h3>
            
            <div style="margin-bottom: 12px;">
                <h4 style="margin: 5px 0; font-size: 13px; color: #555;">🎯 Prioridades ({num_points} pontos):</h4>
                <p style="margin: 3px 0; line-height: 1.6;">
                    <span style="color: red; font-weight: bold;">🔴 Crítico</span> | 
                    <span style="color: orange; font-weight: bold;">🟠 Alto</span><br>
                    <span style="color: #6495ED; font-weight: bold;">🟡 Médio</span> | 
                    <span style="color: green; font-weight: bold;">🟢 Baixo</span>
                </p>
            </div>
            
            <hr style="margin: 10px 0; border: 1px solid #ddd;">
            
            <div style="margin-bottom: 12px;">
                <h4 style="margin: 5px 0; font-size: 13px; color: #555;">🚐 Veículos ({num_vehicles} rotas):</h4>
        '''
        
        # Adicionar cores dos veículos
        for i in range(num_vehicles):
            color = self.VEHICLE_COLORS[i % len(self.VEHICLE_COLORS)]
            legend_html += f'''
                <p style="margin: 3px 0; line-height: 1.5;">
                    <span style="display: inline-block; width: 30px; height: 3px; background-color: {color}; vertical-align: middle;"></span>
                    <span style="font-weight: bold; color: {color};"> Veículo {i+1}</span>
                </p>
            '''
        
        legend_html += '''
            </div>
            
            <hr style="margin: 10px 0; border: 1px solid #ddd;">
            
            <div style="margin-bottom: 5px;">
                <h4 style="margin: 5px 0; font-size: 13px; color: #555;">📍 Símbolos:</h4>
                <p style="margin: 3px 0; font-size: 12px; line-height: 1.6;">
                    🏠 = Depósito Central<br>
                    📍 = Ponto de Entrega<br>
                    A,B,C... = Identificação dos pontos<br>
                    → = Direção da rota (animada)
                </p>
            </div>
            
            <hr style="margin: 10px 0; border: 1px solid #ddd;">
            
            <p style="margin: 5px 0; font-size: 11px; color: #999; text-align: center;">
                💡 Clique nos marcadores para ver detalhes<br>
                Use os botões + e - para zoom
            </p>
        </div>
        '''
        
        mapa.get_root().html.add_child(folium.Element(legend_html))
    
    def save_map(self, mapa: folium.Map, filename: str = None) -> Path:
        """
        Salva mapa em arquivo HTML.
        
        Args:
            mapa: Objeto folium.Map
            filename: Nome do arquivo (opcional, gera automaticamente se None)
            
        Returns:
            Path do arquivo salvo
        """
        # Criar diretório de saída se não existir
        output_dir = Path("outputs/maps")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Gerar nome do arquivo se não fornecido
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mapa_rotas_{timestamp}.html"
        
        # Garantir extensão .html
        if not filename.endswith('.html'):
            filename += '.html'
        
        # Caminho completo
        filepath = output_dir / filename
        
        # Salvar mapa
        mapa.save(str(filepath))
        
        print(f"\n{'='*70}")
        print(f"✅ MAPA HTML GERADO COM SUCESSO!")
        print(f"{'='*70}")
        print(f"📁 Local: {filepath.absolute()}")
        print(f"🌐 Abra no navegador para visualizar o mapa interativo!")
        print(f"{'='*70}\n")
        
        return filepath
    
    def create_and_save_map(
        self,
        delivery_points: List[Dict],
        routes: List[List[int]],
        vehicles: List[Dict],
        filename: str = None,
        zoom_start: int = 12
    ) -> Path:
        """
        Método auxiliar que cria e salva o mapa em uma única chamada.
        
        Args:
            delivery_points: Lista de pontos de entrega
            routes: Lista de rotas
            vehicles: Lista de veículos
            filename: Nome do arquivo (opcional)
            zoom_start: Nível de zoom inicial
            
        Returns:
            Path do arquivo salvo
        """
        mapa = self.create_map(delivery_points, routes, vehicles, zoom_start)
        return self.save_map(mapa, filename)


# Função auxiliar para uso rápido
def generate_route_map(
    delivery_points: List[Dict],
    routes: List[List[int]],
    vehicles: List[Dict],
    output_filename: str = None,
    center: Tuple[float, float] = (-23.550520, -46.633308)
) -> Path:
    """
    Função auxiliar para gerar mapa de rotas rapidamente.
    
    Args:
        delivery_points: Lista de pontos de entrega
        routes: Lista de rotas (índices dos pontos)
        vehicles: Lista de dados dos veículos
        output_filename: Nome do arquivo de saída (opcional)
        center: Centro do mapa (lat, lon)
        
    Returns:
        Path do arquivo HTML gerado
    """
    viz = FoliumVisualizer(center=center)
    return viz.create_and_save_map(delivery_points, routes, vehicles, output_filename)

