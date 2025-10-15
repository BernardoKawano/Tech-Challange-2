"""
Visualizador em tempo real usando Pygame (adaptado do código base TSP).

Este módulo permite visualizar a evolução do algoritmo genético em tempo real,
mostrando as rotas sendo otimizadas e gráficos de convergência.
"""

import pygame
from pygame.locals import *
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from typing import List, Tuple, Optional, Dict
import sys

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)

# Cores por prioridade
PRIORITY_COLORS = {
    'critico': (255, 0, 0),      # Vermelho
    'alto': (255, 165, 0),        # Laranja
    'medio': (255, 255, 0),       # Amarelo
    'baixo': (0, 255, 0)          # Verde
}

# Cores por veículo (para diferentes rotas)
VEHICLE_COLORS = [
    (0, 0, 255),      # Azul
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Ciano
    (255, 128, 0),    # Laranja escuro
    (128, 0, 255),    # Roxo
]


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


class PygameVisualizer:
    """
    Visualizador em tempo real usando Pygame.
    
    Permite acompanhar a evolução do algoritmo genético enquanto ele executa,
    mostrando as rotas atuais e gráficos de convergência.
    """
    
    def __init__(self, width: int = 1200, height: int = 600, fps: int = 30):
        """
        Inicializa o visualizador Pygame.
        
        Args:
            width: Largura da janela
            height: Altura da janela
            fps: Frames por segundo
        """
        pygame.init()
        self.width = width
        self.height = height
        self.fps = fps
        self.plot_x_offset = width // 2  # Metade para mapa, metade para gráfico
        
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Otimização de Rotas Médicas - Evolução em Tempo Real")
        self.clock = pygame.time.Clock()
        
        self.running = True
        self.paused = False
        
        # Histórico
        self.generation_history = []
        self.fitness_history = []
        
        # Filtro de veículos (para visualização seletiva)
        self.selected_vehicle = -1  # -1 = todos, 0+ = veículo específico
        self.vehicle_buttons = []  # Lista de retângulos dos botões
        self.num_vehicles = 0  # Será atualizado dinamicamente
    
    def handle_events(self):
        """Processa eventos do Pygame, incluindo cliques nos botões."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_s:
                    # Salvar screenshot
                    pygame.image.save(self.screen, f"screenshot_gen_{len(self.generation_history)}.png")
                    print("Screenshot salvo!")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Detectar clique nos botões de veículos
                mouse_pos = event.pos
                for i, button_rect in enumerate(self.vehicle_buttons):
                    if button_rect.collidepoint(mouse_pos):
                        # i = 0 é "Todos", i >= 1 são veículos específicos
                        if i == 0:
                            self.selected_vehicle = -1  # Mostrar todos
                            print("Mostrando TODOS os veiculos")
                        else:
                            self.selected_vehicle = i - 1  # Índice do veículo
                            print(f"Mostrando apenas Veiculo {i}")
                        break
    
    def normalize_coordinates(self, 
                             coords: List[Tuple[float, float]], 
                             margin: int = 50) -> List[Tuple[int, int]]:
        """
        Normaliza coordenadas geográficas para pixels na tela.
        
        Args:
            coords: Lista de (latitude, longitude)
            margin: Margem em pixels
            
        Returns:
            Lista de (x, y) em pixels
        """
        if not coords:
            return []
        
        # Encontrar limites
        lats = [c[0] for c in coords]
        lons = [c[1] for c in coords]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Calcular escala
        available_width = self.plot_x_offset - 2 * margin
        available_height = self.height - 2 * margin
        
        lat_range = max_lat - min_lat if max_lat != min_lat else 1
        lon_range = max_lon - min_lon if max_lon != min_lon else 1
        
        scale_x = available_width / lon_range
        scale_y = available_height / lat_range
        scale = min(scale_x, scale_y)
        
        # Normalizar
        normalized = []
        for lat, lon in coords:
            x = int((lon - min_lon) * scale + margin)
            y = int((max_lat - lat) * scale + margin)  # Inverter Y
            normalized.append((x, y))
        
        return normalized
    
    def draw_delivery_points(self, 
                            points: List[Tuple[int, int]], 
                            priorities: List[str],
                            radius: int = 12):
        """
        Desenha pontos de entrega com letras (A, B, C...) e cores baseadas na prioridade.
        
        Args:
            points: Lista de coordenadas (x, y) em pixels
            priorities: Lista de prioridades correspondentes
            radius: Raio dos círculos
        """
        font = pygame.font.Font(None, 20)
        
        for i, (point, priority) in enumerate(zip(points, priorities)):
            color = PRIORITY_COLORS.get(priority, GRAY)
            pygame.draw.circle(self.screen, color, point, radius)
            # Borda preta
            pygame.draw.circle(self.screen, BLACK, point, radius, 2)
            
            # Desenhar letra (A, B, C, ... A1, B1, ...)
            label = get_point_label(i)
            text = font.render(label, True, BLACK)
            text_rect = text.get_rect(center=point)
            self.screen.blit(text, text_rect)
    
    def draw_route(self, 
                   route: List[Tuple[int, int]], 
                   vehicle_index: int = 0,
                   width: int = 3,
                   draw_arrows: bool = False):
        """
        Desenha uma rota conectando os pontos.
        
        Args:
            route: Lista de coordenadas (x, y) em pixels
            vehicle_index: Índice do veículo (para cor)
            width: Espessura da linha
            draw_arrows: Se True, desenha setas indicando direção
        """
        if len(route) < 2:
            return
        
        color = VEHICLE_COLORS[vehicle_index % len(VEHICLE_COLORS)]
        
        # Desenhar linha fechada (volta ao depósito)
        pygame.draw.lines(self.screen, color, True, route, width)
        
        if draw_arrows:
            # Desenhar setas pequenas indicando direção
            for i in range(len(route)):
                p1 = route[i]
                p2 = route[(i + 1) % len(route)]
                # Calcular ponto médio
                mid_x = (p1[0] + p2[0]) // 2
                mid_y = (p1[1] + p2[1]) // 2
                # Desenhar pequeno círculo
                pygame.draw.circle(self.screen, color, (mid_x, mid_y), 3)
    
    def draw_depot(self, depot: Tuple[int, int], size: int = 12):
        """
        Desenha o depósito (hospital central).
        
        Args:
            depot: Coordenadas (x, y) em pixels
            size: Tamanho do marcador
        """
        # Desenhar quadrado para depósito
        rect = pygame.Rect(depot[0] - size//2, depot[1] - size//2, size, size)
        pygame.draw.rect(self.screen, BLACK, rect)
        pygame.draw.rect(self.screen, RED, rect, 3)
    
    def draw_rounded_rect(self, surface, color, rect, radius=15, border_color=None, border_width=0):
        """
        Desenha um retângulo com cantos arredondados.
        
        Args:
            surface: Superfície pygame
            color: Cor do retângulo
            rect: pygame.Rect
            radius: Raio dos cantos
            border_color: Cor da borda (opcional)
            border_width: Espessura da borda
        """
        # Desenhar retângulo com cantos arredondados
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        if border_color and border_width > 0:
            pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)
    
    def draw_vehicle_filter_buttons(self, num_vehicles: int, y_offset: int = 10):
        """
        Desenha botões interativos ARREDONDADOS para filtrar visualização por veículo.
        Inclui legendas de prioridades ao lado.
        
        Args:
            num_vehicles: Número total de veículos
            y_offset: Deslocamento vertical inicial
        """
        self.num_vehicles = num_vehicles
        self.vehicle_buttons = []
        
        font_title = pygame.font.Font(None, 26)
        font_button = pygame.font.Font(None, 22)
        font_legend = pygame.font.Font(None, 18)
        
        x = self.plot_x_offset + 20
        y = y_offset
        
        # ==========================================
        # SEÇÃO 1: BOTÕES DE FILTRO (ESQUERDA)
        # ==========================================
        
        # Título da seção
        title = font_title.render("FILTRAR ROTAS:", True, BLACK)
        self.screen.blit(title, (x, y))
        y += 40
        
        # Botão "TODOS" - COMPACTO
        button_width = 150  # Reduzido de 160
        button_height = 38  # Reduzido de 42
        button_radius = 15  # Reduzido de 20
        
        # Botão "Todos os Veículos"
        button_rect = pygame.Rect(x, y, button_width, button_height)
        self.vehicle_buttons.append(button_rect)
        
        # Cor do botão (destacar se selecionado)
        if self.selected_vehicle == -1:
            button_color = (80, 180, 80)  # Verde mais vibrante
            text_color = WHITE
            icon = "[X]"
        else:
            button_color = (230, 230, 230)  # Cinza claro
            text_color = (80, 80, 80)
            icon = "[ ]"
        
        # Desenhar botão arredondado
        self.draw_rounded_rect(self.screen, button_color, button_rect, button_radius, BLACK, 3)
        
        # Texto do botão com ícone
        text = font_button.render(f"{icon} TODOS", True, text_color)
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)
        
        y += button_height + 8  # Reduzido de 12 para 8
        
        # Botões individuais para cada veículo - Arredondados
        
        for i in range(num_vehicles):
            button_rect = pygame.Rect(x, y, button_width, button_height)
            self.vehicle_buttons.append(button_rect)
            
            # Cor do botão
            if self.selected_vehicle == i:
                # Usar a cor do veículo se selecionado
                button_color = VEHICLE_COLORS[i % len(VEHICLE_COLORS)]
                text_color = WHITE
                icon = "[X]"
            else:
                button_color = (240, 240, 240)  # Cinza muito claro
                text_color = (60, 60, 60)
                icon = "[ ]"
            
            # Desenhar botão arredondado
            self.draw_rounded_rect(self.screen, button_color, button_rect, button_radius, BLACK, 2)
            
            # Desenhar preview da linha colorida (se não selecionado)
            if self.selected_vehicle != i:
                line_color = VEHICLE_COLORS[i % len(VEHICLE_COLORS)]
                line_start = (x + 12, y + button_height // 2)
                line_end = (x + 42, y + button_height // 2)
                pygame.draw.line(self.screen, line_color, line_start, line_end, 5)
                pygame.draw.circle(self.screen, line_color, line_start, 3)
                pygame.draw.circle(self.screen, line_color, line_end, 3)
            
            # Texto do botão
            text = font_button.render(f"{icon} Veiculo {i + 1}", True, text_color)
            text_rect = text.get_rect(center=(button_rect.centerx + 15, button_rect.centery))
            self.screen.blit(text, text_rect)
            
            y += button_height + 6  # Reduzido de 10 para 6
        
        # ==========================================
        # SEÇÃO 2: LEGENDA DE PRIORIDADES (DIREITA AO LADO DOS BOTÕES)
        # ==========================================
        
        legend_x = x + button_width + 30  # Ao lado dos botões
        legend_y = y_offset + 40
        
        # Título da legenda
        legend_title = font_title.render("PRIORIDADES:", True, BLACK)
        self.screen.blit(legend_title, (legend_x, legend_y))
        legend_y += 40
        
        priority_descriptions = {
            'critico': 'URGENTE',
            'alto': 'IMPORTANTE',
            'medio': 'REGULAR',
            'baixo': 'FLEXÍVEL'
        }
        
        item_height = 36  # Reduzido de 42 para 36
        icon_size = 14  # Reduzido de 18 para 14
        
        for priority, color in PRIORITY_COLORS.items():
            # Desenhar círculo da cor (mais destaque)
            circle_center = (legend_x + 15, legend_y + item_height // 2)
            pygame.draw.circle(self.screen, color, circle_center, icon_size)
            pygame.draw.circle(self.screen, BLACK, circle_center, icon_size, 3)
            
            # Nome da prioridade
            priority_name = priority_descriptions[priority]
            text = font_legend.render(priority_name, True, BLACK)
            self.screen.blit(text, (legend_x + 40, legend_y + 5))
            
            # Descrição menor
            if priority == 'critico':
                desc = "Não atrasa"
            elif priority == 'alto':
                desc = "Max 2h"
            elif priority == 'medio':
                desc = "Max 6h"
            else:
                desc = "Max 24h"
            
            desc_text = font_legend.render(desc, True, GRAY)
            self.screen.blit(desc_text, (legend_x + 40, legend_y + 23))
            
            legend_y += item_height + 2
        
        return max(y, legend_y) + 20  # Retornar posição Y final
    
    def draw_legend(self, y_offset: int = 10):
        """
        Desenha legenda simplificada (prioridades agora estão ao lado dos botões).
        
        Args:
            y_offset: Deslocamento vertical
        """
        font_title = pygame.font.Font(None, 24)
        font_text = pygame.font.Font(None, 20)
        font_small = pygame.font.Font(None, 16)
        
        x = self.plot_x_offset + 15
        y = y_offset
        
        # ==========================================
        # SEÇÃO 2: DEPÓSITO (HOSPITAL CENTRAL)
        # ==========================================
        title = font_title.render("DEPÓSITO:", True, BLACK)
        self.screen.blit(title, (x, y))
        y += 30
        
        # Desenhar símbolo do depósito
        rect = pygame.Rect(x + 4, y + 4, 16, 16)
        pygame.draw.rect(self.screen, BLACK, rect)
        pygame.draw.rect(self.screen, RED, rect, 3)
        
        text = font_text.render("HOSPITAL CENTRAL", True, BLACK)
        self.screen.blit(text, (x + 30, y))
        desc = font_small.render("Ponto de partida e chegada", True, GRAY)
        self.screen.blit(desc, (x + 30, y + 15))
        
        y += 50
        
        # ==========================================
        # SEÇÃO 3: ROTAS DOS VEÍCULOS (LINHAS)
        # ==========================================
        title = font_title.render("ROTAS (LINHAS):", True, BLACK)
        self.screen.blit(title, (x, y))
        y += 30
        
        # Legendas das rotas - usar apenas os veículos que existem realmente
        route_names = ["Veículo 1", "Veículo 2", "Veículo 3", "Veículo 4", "Veículo 5"]
        
        # Usar self.num_vehicles se disponível, senão mostrar apenas 3 (padrão da simulação)
        num_to_show = getattr(self, 'num_vehicles', 3)
        
        for i in range(min(num_to_show, len(VEHICLE_COLORS))):
            color = VEHICLE_COLORS[i]
            
            # Desenhar linha exemplo
            pygame.draw.line(self.screen, color, (x + 5, y + 10), (x + 40, y + 10), 4)
            
            # Nome do veículo
            text = font_text.render(route_names[i], True, BLACK)
            self.screen.blit(text, (x + 50, y + 2))
            
            y += 28
        
        y += 15
        
        # ==========================================
        # SEÇÃO 4: INFORMAÇÕES ADICIONAIS
        # ==========================================
        title = font_title.render("COMO LER O MAPA:", True, BLACK)
        self.screen.blit(title, (x, y))
        y += 30
        
        # Dicas de leitura
        tips = [
            "• Círculos = Locais de entrega",
            "• Linhas = Rota do veículo",
            "• Quadrado = Depósito central",
            "• Cores quentes = Mais urgente",
            "• Rotas fechadas = Volta ao depósito"
        ]
        
        for tip in tips:
            text = font_small.render(tip, True, BLACK)
            self.screen.blit(text, (x + 5, y))
            y += 22
    
    def draw_metrics(self, 
                    generation: int, 
                    best_fitness: float,
                    num_routes: int,
                    y_offset: int = 700):  # Ajustado para Full HD
        """
        Desenha métricas da evolução atual com formatação melhorada.
        
        Args:
            generation: Número da geração atual
            best_fitness: Melhor fitness da geração
            num_routes: Número de rotas/veículos
            y_offset: Deslocamento vertical
        """
        font_title = pygame.font.Font(None, 20)  # Reduzido de 24
        font_text = pygame.font.Font(None, 16)  # Reduzido de 20
        x = self.plot_x_offset + 15
        y = y_offset
        
        # Título da seção
        title = font_title.render("METRICAS:", True, BLACK)
        self.screen.blit(title, (x, y))
        y += 22  # Reduzido de 35
        
        # Métricas
        metrics = [
            f"Geracao: {generation}",
            f"Fitness: {best_fitness:.2f} km",
            f"Veiculos: {num_routes}",
        ]
        
        for metric in metrics:
            text = font_text.render(metric, True, BLACK)
            self.screen.blit(text, (x, y))
            y += 18  # Reduzido de 30
        
        y += 8  # Reduzido de 15
        
        # Controles - REMOVIDOS para economizar espaço
        # (usuário já sabe os controles do menu)
    
    def draw_ag_statistics(self, ag_stats: Dict, y_offset: int = 625):
        """
        Desenha estatísticas do algoritmo genético (COMPACTO).
        
        Args:
            ag_stats: Dicionário com estatísticas do AG
            y_offset: Posição Y inicial (padrão 625 para evitar sobreposição)
        """
        if not ag_stats:
            return
        
        font_title = pygame.font.Font(None, 20)  # Reduzido de 22
        font_text = pygame.font.Font(None, 16)  # Reduzido de 18
        x = self.plot_x_offset + 15
        y = y_offset
        
        # Título
        title = font_title.render("ESTATISTICAS DO AG:", True, BLACK)
        self.screen.blit(title, (x, y))
        y += 22  # Reduzido de 25
        
        # Estatísticas - COMPACTO
        stats_text = [
            f"Crossovers: {ag_stats.get('total_crossovers', 0)}",
            f"Mutacoes: {ag_stats.get('total_mutations', 0)}",
            f"Selecao: {ag_stats.get('selection_type', 'N/A')}",
            f"Crossover: {ag_stats.get('crossover_type', 'N/A')}"
        ]
        
        for stat in stats_text:
            text = font_text.render(stat, True, BLACK)
            self.screen.blit(text, (x, y))
            y += 17  # Reduzido de 20
        
        # Tipos de mutação - COMPACTO (mostrar apenas se houver)
        if ag_stats.get('mutation_types') and len(ag_stats['mutation_types']) > 0:
            y += 3  # Reduzido de 5
            text = font_text.render("Mutacoes:", True, BLACK)
            self.screen.blit(text, (x, y))
            y += 15  # Reduzido de 18
            
            # Mostrar apenas os 3 tipos mais comuns
            sorted_muts = sorted(ag_stats['mutation_types'].items(), key=lambda x: x[1], reverse=True)[:3]
            for mut_type, count in sorted_muts:
                text = font_text.render(f"  {mut_type}: {count}", True, GRAY)
                self.screen.blit(text, (x + 10, y))
                y += 14  # Reduzido de 16
    
    def draw_route_details(self, route_details: Dict, y_offset: int = 10):
        """
        Desenha detalhes das rotas abaixo do mapa (COMPACTO).
        
        Args:
            route_details: Dicionário com detalhes das rotas
            y_offset: Posição Y inicial
        """
        if not route_details or 'routes' not in route_details:
            return
        
        font_title = pygame.font.Font(None, 18)
        font_text = pygame.font.Font(None, 14)
        
        # Área para detalhes (parte inferior da tela) - COMPACTA
        detail_area_y = self.height - 150  # Reduzido de 200 para 150
        x = 20
        y = detail_area_y + 8
        
        # Fundo semi-transparente - MENOR
        detail_bg = pygame.Surface((self.width - 40, 135))  # Reduzido de 180 para 135
        detail_bg.fill((240, 240, 240))
        detail_bg.set_alpha(230)
        self.screen.blit(detail_bg, (20, detail_area_y))
        
        # Título
        title = font_title.render(f"DETALHES DAS ROTAS - Fitness: {route_details.get('fitness', 0):.2f} | "
                                 f"Distancia: {route_details.get('total_distance_km', 0):.2f} km | "
                                 f"Veiculos: {route_details.get('num_vehicles', 0)}", True, BLACK)
        self.screen.blit(title, (x + 10, y))
        y += 25
        
        # Desenhar cada rota em colunas - COMPACTO
        routes = route_details['routes']
        num_routes = len(routes)
        col_width = (self.width - 60) // min(num_routes, 4)  # Máximo 4 colunas
        
        for i, route_info in enumerate(routes):
            col_x = x + 10 + (i % 4) * col_width
            col_y = y + (i // 4) * 60  # Reduzido de 75 para 60
            
            # Nome do veículo
            vehicle_name = route_info.get('vehicle_name', f"Veiculo {i+1}")
            color = VEHICLE_COLORS[i % len(VEHICLE_COLORS)]
            
            # Linha colorida do veículo - COMPACTA
            pygame.draw.line(self.screen, color, (col_x, col_y + 4), (col_x + 25, col_y + 4), 3)
            
            text = font_title.render(vehicle_name, True, BLACK)
            self.screen.blit(text, (col_x + 30, col_y))
            col_y += 16
            
            # Detalhes - COMPACTOS
            details = [
                f"Entregas: {route_info.get('num_deliveries', 0)}",
                f"Dist: {route_info.get('distance_km', 0):.1f} km",
                f"Carga: {route_info.get('load_kg', 0):.0f}/{route_info.get('capacity_kg', 0):.0f} kg",
                f"Rota: {' -> '.join(route_info.get('points', []))[:30]}..."  # Limitar tamanho
            ]
            
            for detail in details:
                text = font_text.render(detail, True, GRAY)
                self.screen.blit(text, (col_x, col_y))
                col_y += 12  # Reduzido de 14 para 12
    
    def draw_convergence_plot(self, y_offset: int = 340):
        """Desenha gráfico de convergência COMPACTO."""
        if not self.fitness_history:
            return
        
        try:
            # Criar figura matplotlib MENOR
            fig, ax = plt.subplots(figsize=(4.2, 3.2), dpi=85)  # Reduzido de (5,5)
            ax.plot(self.generation_history, self.fitness_history, 'b-', linewidth=1.5)
            ax.set_xlabel('Geracao', fontsize=9)
            ax.set_ylabel('Fitness', fontsize=9)
            ax.set_title('Convergencia do AG', fontsize=10)
            ax.tick_params(axis='both', labelsize=8)
            ax.grid(True, alpha=0.3, linewidth=0.5)
            plt.tight_layout(pad=0.5)
            
            # Converter para surface Pygame
            canvas = FigureCanvasAgg(fig)
            canvas.draw()
            
            buf = canvas.buffer_rgba()
            size = canvas.get_width_height()
            
            # Criar surface do pygame - POSIÇÃO FIXA NO LADO DIREITO
            surf = pygame.image.frombuffer(buf, size, "RGBA")
            self.screen.blit(surf, (self.plot_x_offset + 10, y_offset))  # Posição controlada
            
            plt.close(fig)
        except Exception as e:
            # Se falhar, apenas não desenhar o gráfico
            pass
    
    def update(self, 
               delivery_points_coords: List[Tuple[float, float]],
               delivery_points_priorities: List[str],
               routes: List[List[int]],  # Lista de rotas (cada rota é lista de índices)
               depot_coord: Tuple[float, float],
               generation: int,
               best_fitness: float,
               ag_stats: Dict = None,
               route_details: Dict = None):
        """
        Atualiza a visualização com novos dados.
        
        Args:
            delivery_points_coords: Coordenadas dos pontos de entrega (lat, lon)
            delivery_points_priorities: Prioridades dos pontos
            routes: Lista de rotas (cada rota é lista de índices de pontos)
            depot_coord: Coordenada do depósito (lat, lon)
            generation: Número da geração atual
            best_fitness: Melhor fitness
        """
        # Processar eventos
        self.handle_events()
        
        if not self.running:
            return False
        
        if self.paused:
            self.clock.tick(self.fps)
            return True
        
        # Limpar tela
        self.screen.fill(WHITE)
        
        # Normalizar coordenadas
        all_coords = delivery_points_coords + [depot_coord]
        normalized = self.normalize_coordinates(all_coords)
        
        depot_pixel = normalized[-1]
        points_pixels = normalized[:-1]
        
        # Desenhar depósito
        self.draw_depot(depot_pixel)
        
        # Desenhar rotas (com filtro)
        for vehicle_idx, route_indices in enumerate(routes):
            # Aplicar filtro: só desenhar se for o veículo selecionado ou se "todos" estiver selecionado
            if self.selected_vehicle == -1 or self.selected_vehicle == vehicle_idx:
                # Construir rota em pixels
                route_pixels = [depot_pixel]  # Começa no depósito
                for idx in route_indices:
                    if 0 <= idx < len(points_pixels):
                        route_pixels.append(points_pixels[idx])
                
                # Espessura da linha: mais grossa se for o veículo selecionado
                line_width = 4 if self.selected_vehicle == vehicle_idx else 2
                
                if len(route_pixels) > 1:
                    self.draw_route(route_pixels, vehicle_idx, width=line_width)
        
        # Desenhar pontos de entrega (por cima das rotas)
        self.draw_delivery_points(points_pixels, delivery_points_priorities)
        
        # Atualizar histórico
        self.generation_history.append(generation)
        self.fitness_history.append(best_fitness)
        
        # ========== LAYOUT ORGANIZADO - SEM SOBREPOSIÇÕES ==========
        
        # TOPO DO PAINEL DIREITO (y=10): Filtros de veículos + Prioridades
        next_y = self.draw_vehicle_filter_buttons(len(routes), y_offset=10)
        
        # GRÁFICO DE CONVERGÊNCIA (y=340): Posição fixa, não sobrepõe
        self.draw_convergence_plot(y_offset=340)
        
        # ESTATÍSTICAS DO AG (y=625): Logo abaixo do gráfico
        if ag_stats:
            self.draw_ag_statistics(ag_stats, y_offset=625)
        
        # MÉTRICAS GERAIS (y=820): Abaixo das estatísticas
        self.draw_metrics(generation, best_fitness, len(routes), y_offset=820)
        
        # PARTE INFERIOR (y=930): Detalhes das rotas
        if route_details:
            self.draw_route_details(route_details)
        
        # Atualizar display
        pygame.display.flip()
        self.clock.tick(self.fps)
        
        return True
    
    def close(self):
        """Fecha o visualizador."""
        pygame.quit()
        sys.exit()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Exemplo de uso
if __name__ == '__main__':
    # Teste simples
    viz = PygameVisualizer()
    
    # Dados de teste
    points = [(-23.5880, -46.6400), (-23.5650, -46.6520), (-23.5950, -46.6750)]
    priorities = ['critico', 'alto', 'medio']
    depot = (-23.5505, -46.6333)
    
    generation = 0
    while viz.running and generation < 100:
        # Simular rotas (aqui viria do AG real)
        routes = [[0, 1], [2]]
        fitness = 100 - generation  # Simulando melhoria
        
        if not viz.update(points, priorities, routes, depot, generation, fitness):
            break
        
        generation += 1
    
    viz.close()

