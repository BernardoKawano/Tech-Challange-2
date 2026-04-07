"""
Teste Interativo do Algoritmo Genético com Interface Pygame.

Este script mostra uma tela de configuração NO PYGAME onde você escolhe:
- Número de veículos (1 a 5)
- Número de pontos de entrega (1 a 100)

Depois inicia a simulação com visualização completa.
"""

import sys
import json
import pygame
from pathlib import Path
from typing import Dict, Optional, Tuple

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Importar módulos
from src.models import DeliveryPoint, Vehicle
from src.visualization.pygame_visualizer import PygameVisualizer
from src.visualization.folium_visualizer import FoliumVisualizer
from src.genetic_algorithm import GeneticAlgorithm
from src.llm_integration import InstructionGenerator, ReportGenerator

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_GRAY = (240, 240, 240)
BLUE = (70, 130, 255)
GREEN = (100, 200, 100)
RED = (255, 100, 100)
ORANGE = (255, 165, 0)

# Cores dos veículos (para identificação visual)
VEHICLE_COLORS = [
    (255, 100, 100),   # Vermelho
    (100, 150, 255),   # Azul
    (100, 200, 100),   # Verde
    (255, 200, 100),   # Laranja
    (200, 100, 255)    # Roxo
]


def detect_display_size() -> Tuple[int, int]:
    """
    Detecta resolução atual do monitor para adaptar a interface.
    """
    pygame.init()
    info = pygame.display.Info()
    width = max(1024, info.current_w)
    height = max(720, info.current_h)
    return width, height


class ConfigScreen:
    """Tela de configuração interativa no Pygame."""
    
    def __init__(self, width: Optional[int] = None, height: Optional[int] = None):
        """
        Inicializa a tela de configuração em TELA CHEIA.
        
        Args:
            width: Largura da janela (padrão Full HD)
            height: Altura da janela (padrão Full HD)
        """
        pygame.init()
        auto_width, auto_height = detect_display_size()
        self.width = width or auto_width
        self.height = height or auto_height
        
        # Janela adaptativa para qualquer resolução
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Configuracao do AG - VRP")
        self.clock = pygame.time.Clock()
        
        # Valores selecionados
        self.num_vehicles = 3  # Padrão
        self.num_points = 10   # Padrão
        self.num_generations = 100  # Padrão
        
        # Estado
        self.running = True
        self.confirmed = False
        
        # Botões de veículos - MINI
        self.vehicle_buttons = []
        button_width = 90  # Reduzido de 120
        button_height = 45  # Reduzido de 60
        total_width = 5 * button_width + 4 * 20  # 5 botões + 4 espaços menores
        start_x = (self.width - total_width) // 2
        y_vehicles = 180  # Mais próximo do título
        
        for i in range(5):
            x = start_x + i * (button_width + 20)  # Espaçamento reduzido
            self.vehicle_buttons.append(pygame.Rect(x, y_vehicles, button_width, button_height))
        
        # Slider de pontos - MINI
        slider_width = 700  # Reduzido de 900
        slider_height = 20  # Reduzido de 25
        slider_x = (self.width - slider_width) // 2
        slider_y = 300  # Mais próximo (era 380)
        self.points_slider_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
        self.points_slider_handle = pygame.Rect(0, 0, 14, 32)  # Reduzido
        self.dragging_points_slider = False
        
        # Slider de gerações - MINI
        slider_y_gens = 410  # Mais próximo (era 520)
        self.generations_slider_rect = pygame.Rect(slider_x, slider_y_gens, slider_width, slider_height)
        self.generations_slider_handle = pygame.Rect(0, 0, 14, 32)  # Reduzido
        self.dragging_gens_slider = False
        
        # Botão de iniciar - MENOR (mais acima)
        start_y = min(720, self.height - 120)
        self.start_button = pygame.Rect(self.width // 2 - 150, start_y, 300, 55)
    
    def update_points_slider_handle_position(self):
        """Atualiza posição do handle do slider de pontos."""
        ratio = (self.num_points - 1) / (100 - 1)
        x = self.points_slider_rect.x + ratio * self.points_slider_rect.width
        y = self.points_slider_rect.centery - self.points_slider_handle.height // 2
        self.points_slider_handle.x = x - self.points_slider_handle.width // 2
        self.points_slider_handle.y = y
    
    def update_gens_slider_handle_position(self):
        """Atualiza posição do handle do slider de gerações."""
        # Mapear num_generations (50-2000) para posição no slider
        ratio = (self.num_generations - 50) / (2000 - 50)
        x = self.generations_slider_rect.x + ratio * self.generations_slider_rect.width
        y = self.generations_slider_rect.centery - self.generations_slider_handle.height // 2
        self.generations_slider_handle.x = x - self.generations_slider_handle.width // 2
        self.generations_slider_handle.y = y
    
    def handle_events(self):
        """Processa eventos da interface."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.w, event.h
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Verificar clique nos botões de veículos
                for i, button in enumerate(self.vehicle_buttons):
                    if button.collidepoint(mouse_pos):
                        self.num_vehicles = i + 1
                
                # Verificar clique no slider de pontos
                if self.points_slider_handle.collidepoint(mouse_pos):
                    self.dragging_points_slider = True
                elif self.points_slider_rect.collidepoint(mouse_pos):
                    self.update_points_from_mouse(mouse_pos[0])
                
                # Verificar clique no slider de gerações
                if self.generations_slider_handle.collidepoint(mouse_pos):
                    self.dragging_gens_slider = True
                elif self.generations_slider_rect.collidepoint(mouse_pos):
                    self.update_gens_from_mouse(mouse_pos[0])
                
                # Verificar clique no botão de iniciar
                if self.start_button.collidepoint(mouse_pos):
                    self.confirmed = True
                    self.running = False
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging_points_slider = False
                self.dragging_gens_slider = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_points_slider:
                    self.update_points_from_mouse(event.pos[0])
                if self.dragging_gens_slider:
                    self.update_gens_from_mouse(event.pos[0])
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.running = False
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.confirmed = True
                    self.running = False
    
    def update_points_from_mouse(self, mouse_x: int):
        """Atualiza num_points baseado na posição do mouse no slider."""
        x = max(self.points_slider_rect.x, 
                min(mouse_x, self.points_slider_rect.x + self.points_slider_rect.width))
        ratio = (x - self.points_slider_rect.x) / self.points_slider_rect.width
        self.num_points = int(1 + ratio * (100 - 1))
        self.num_points = max(1, min(100, self.num_points))
    
    def update_gens_from_mouse(self, mouse_x: int):
        """Atualiza num_generations baseado na posição do mouse no slider."""
        x = max(self.generations_slider_rect.x, 
                min(mouse_x, self.generations_slider_rect.x + self.generations_slider_rect.width))
        ratio = (x - self.generations_slider_rect.x) / self.generations_slider_rect.width
        # Mapear para num_generations (50-2000) em incrementos de 50
        self.num_generations = int(50 + ratio * (2000 - 50))
        self.num_generations = (self.num_generations // 50) * 50  # Arredondar para múltiplo de 50
        self.num_generations = max(50, min(2000, self.num_generations))
    
    def draw_rounded_rect(self, surface, color, rect, radius, border_color=None, border_width=0):
        """Desenha retângulo com cantos arredondados."""
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        if border_color and border_width > 0:
            pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)
    
    def draw(self):
        """Desenha a interface em TELA CHEIA COMPACTA."""
        self.screen.fill(WHITE)
        
        # Título - MINI
        font_title = pygame.font.Font(None, 52)  # Reduzido de 70
        title = font_title.render("CONFIGURACAO DO ALGORITMO GENETICO", True, BLACK)
        title_rect = title.get_rect(center=(self.width // 2, 45))  # Mais próximo do topo
        self.screen.blit(title, title_rect)
        
        # Subtítulo - MINI
        font_subtitle = pygame.font.Font(None, 26)  # Reduzido de 32
        subtitle = font_subtitle.render("Escolha os parametros para otimizacao de rotas", True, DARK_GRAY)
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 85))  # Mais próximo
        self.screen.blit(subtitle, subtitle_rect)
        
        # === SEÇÃO: VEÍCULOS ===
        font_section = pygame.font.Font(None, 32)  # Reduzido de 40
        font_text = pygame.font.Font(None, 22)  # Reduzido de 28
        
        # Título da seção VEÍCULOS - CENTRALIZADO E MINI
        vehicles_title = font_section.render("NUMERO DE VEICULOS:", True, BLACK)
        vehicles_title_rect = vehicles_title.get_rect(center=(self.width // 2, 135))  # Mais próximo
        self.screen.blit(vehicles_title, vehicles_title_rect)
        
        # Botões de veículos (1 a 5) - TEXTO MINI
        font_button = pygame.font.Font(None, 32)  # Reduzido de 38
        for i, button in enumerate(self.vehicle_buttons):
            # Cor do botão
            if self.num_vehicles == i + 1:
                color = BLUE
                text_color = WHITE
            else:
                color = LIGHT_GRAY
                text_color = DARK_GRAY
            
            # Desenhar botão com bordas arredondadas
            self.draw_rounded_rect(self.screen, color, button, 15, BLACK, 3)
            
            # Texto do botão (número grande)
            text = font_button.render(str(i + 1), True, text_color)
            text_rect = text.get_rect(center=button.center)
            self.screen.blit(text, text_rect)
        
        # Descrição - ABAIXO DOS BOTÕES MINI
        desc = font_text.render(f"Selecionado: {self.num_vehicles} veiculo(s)", True, DARK_GRAY)
        desc_rect = desc.get_rect(center=(self.width // 2, 238))  # Mais próximo
        self.screen.blit(desc, desc_rect)
        
        # === SEÇÃO: PONTOS DE ENTREGA === MINI
        points_title = font_section.render("PONTOS DE ENTREGA:", True, BLACK)  # Texto mais curto
        points_title_rect = points_title.get_rect(center=(self.width // 2, 270))  # Mais próximo
        self.screen.blit(points_title, points_title_rect)
        
        # Desenhar trilho do slider de pontos
        pygame.draw.rect(self.screen, GRAY, self.points_slider_rect, border_radius=15)
        
        # Atualizar posição do handle de pontos
        self.update_points_slider_handle_position()
        
        # Desenhar handle do slider de pontos
        pygame.draw.rect(self.screen, BLUE, self.points_slider_handle, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, self.points_slider_handle, 3, border_radius=10)
        
        # Labels do slider - MINI
        font_label = pygame.font.Font(None, 26)  # Reduzido de 32
        label_min = font_label.render("1", True, DARK_GRAY)
        label_max = font_label.render("100", True, DARK_GRAY)
        self.screen.blit(label_min, (self.points_slider_rect.x - 35, self.points_slider_rect.centery - 10))
        self.screen.blit(label_max, (self.points_slider_rect.x + self.points_slider_rect.width + 12, 
                                     self.points_slider_rect.centery - 10))
        
        # Valor atual - MINI
        font_value = pygame.font.Font(None, 48)  # Reduzido de 60
        value_text = font_value.render(str(self.num_points), True, BLUE)
        value_rect = value_text.get_rect(center=(self.width // 2, 350))  # Mais próximo
        self.screen.blit(value_text, value_rect)
        
        # === SEÇÃO: NÚMERO DE GERAÇÕES === MINI
        gens_title = font_section.render("GERACOES:", True, BLACK)  # Texto mais curto
        gens_title_rect = gens_title.get_rect(center=(self.width // 2, 375))  # Mais próximo
        self.screen.blit(gens_title, gens_title_rect)
        
        # Desenhar trilho do slider de gerações
        pygame.draw.rect(self.screen, GRAY, self.generations_slider_rect, border_radius=15)
        
        # Atualizar posição do handle de gerações
        self.update_gens_slider_handle_position()
        
        # Desenhar handle do slider de gerações
        pygame.draw.rect(self.screen, ORANGE, self.generations_slider_handle, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, self.generations_slider_handle, 3, border_radius=10)
        
        # Labels do slider de gerações
        label_min_gens = font_label.render("50", True, DARK_GRAY)
        label_max_gens = font_label.render("2000", True, DARK_GRAY)
        self.screen.blit(label_min_gens, (self.generations_slider_rect.x - 40, self.generations_slider_rect.centery - 12))
        self.screen.blit(label_max_gens, (self.generations_slider_rect.x + self.generations_slider_rect.width + 15, 
                                          self.generations_slider_rect.centery - 12))
        
        # Valor atual de gerações
        value_gens_text = font_value.render(str(self.num_generations), True, ORANGE)
        value_gens_rect = value_gens_text.get_rect(center=(self.width // 2, 460))  # Mais próximo
        self.screen.blit(value_gens_text, value_gens_rect)
        
        # === INFORMAÇÕES DOS VEÍCULOS SELECIONADOS === MINI
        vehicles_info_y = 505  # Mais próximo
        font_vehicle_info = pygame.font.Font(None, 20)  # Reduzido de 24
        
        # Ler dados dos veículos
        import json
        from pathlib import Path
        project_root = Path(__file__).parent
        vehicles_file = project_root / 'data' / 'sample_vehicles.json'
        
        if vehicles_file.exists():
            with open(vehicles_file, 'r', encoding='utf-8') as f:
                vehicles_data = json.load(f)
            
            # Mostrar veículos selecionados
            vehicles_to_show = vehicles_data[:self.num_vehicles]
            
            # Título - MINI
            font_vehicles_title = pygame.font.Font(None, 28)  # Reduzido de 36
            vehicles_info_title = font_vehicles_title.render(f"VEICULOS SELECIONADOS ({self.num_vehicles}):", True, BLACK)
            vehicles_info_title_rect = vehicles_info_title.get_rect(center=(self.width // 2, vehicles_info_y))
            self.screen.blit(vehicles_info_title, vehicles_info_title_rect)
            
            # Mostrar cada veículo - MINI
            y_offset = vehicles_info_y + 30  # Reduzido de 35
            x_start = 200
            col_width = 480  # Reduzido de 520
            
            for i, vehicle in enumerate(vehicles_to_show):
                # Posição da coluna (máximo 3 por linha)
                col = i % 3
                row = i // 3
                x = x_start + col * col_width
                y = y_offset + row * 45  # Mais compacto (era 55)
                
                # Nome do veículo com cor
                vehicle_color = VEHICLE_COLORS[i % len(VEHICLE_COLORS)]
                vehicle_name = font_vehicle_info.render(f"● {vehicle['name']}", True, vehicle_color)
                self.screen.blit(vehicle_name, (x, y))
                
                # Especificações - MINI
                specs = f"Cap: {vehicle['capacity_kg']}kg | Auto: {vehicle['autonomy_km']}km"
                specs_text = font_vehicle_info.render(specs, True, DARK_GRAY)
                self.screen.blit(specs_text, (x + 18, y + 20))  # Reduzido de 25
        
        # === RESUMO === MINI
        summary_y = 628  # Mais próximo (era 640)
        summary_width = 1300  # Reduzido de 1500
        summary_height = 65  # Reduzido de 80
        summary_x = (self.width - summary_width) // 2
        summary_box = pygame.Rect(summary_x, summary_y, summary_width, summary_height)
        self.draw_rounded_rect(self.screen, LIGHT_GRAY, summary_box, 15, DARK_GRAY, 2)
        
        # Título do resumo - MINI
        font_summary_title = pygame.font.Font(None, 28)  # Reduzido de 36
        summary_title = font_summary_title.render("RESUMO DA CONFIGURACAO:", True, BLACK)
        summary_title_rect = summary_title.get_rect(center=(self.width // 2, summary_y + 18))
        self.screen.blit(summary_title, summary_title_rect)
        
        # Detalhes - MINI
        pop_size = max(50, self.num_points * 5)
        
        font_details = pygame.font.Font(None, 26)  # Reduzido de 32
        details_text = f"Veiculos: {self.num_vehicles}  |  Pontos: {self.num_points}  |  Populacao: {pop_size}  |  Geracoes: {self.num_generations}"
        details = font_details.render(details_text, True, DARK_GRAY)
        details_rect = details.get_rect(center=(self.width // 2, summary_y + 42))
        self.screen.blit(details, details_rect)
        
        # === BOTÃO INICIAR === COMPACTO
        mouse_pos = pygame.mouse.get_pos()
        if self.start_button.collidepoint(mouse_pos):
            button_color = GREEN
        else:
            button_color = (80, 180, 80)
        
        # Desenhar botão
        self.draw_rounded_rect(self.screen, button_color, self.start_button, 15, BLACK, 3)
        
        # Texto do botão - MINI
        font_start = pygame.font.Font(None, 38)  # Reduzido de 48
        start_text = font_start.render("INICIAR SIMULACAO", True, WHITE)
        start_rect = start_text.get_rect(center=self.start_button.center)
        self.screen.blit(start_text, start_rect)
        
        # Instruções - MINI
        font_instr = pygame.font.Font(None, 22)  # Reduzido de 26
        instr1 = font_instr.render("Clique nos botoes para selecionar | Arraste o slider", True, GRAY)
        instr2 = font_instr.render("Pressione ENTER ou clique em INICIAR | ESC ou Q para sair", True, GRAY)
        
        instr1_rect = instr1.get_rect(center=(self.width // 2, self.height - 60))
        instr2_rect = instr2.get_rect(center=(self.width // 2, self.height - 30))
        
        self.screen.blit(instr1, instr1_rect)
        self.screen.blit(instr2, instr2_rect)
        
        pygame.display.flip()
    
    def run(self) -> Optional[Tuple[int, int, int]]:
        """
        Executa a tela de configuração.
        
        Returns:
            Tupla (num_vehicles, num_points, num_generations) ou None se cancelado
        """
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        
        if self.confirmed:
            return (self.num_vehicles, self.num_points, self.num_generations)
        return None


def run_simulation(num_vehicles: int, num_points: int, num_generations: int):
    """
    Executa a simulação com os parâmetros escolhidos.
    
    Args:
        num_vehicles: Número de veículos
        num_points: Número de pontos de entrega
        num_generations: Número de gerações
    """
    print("\n" + "="*60)
    print("INICIANDO SIMULACAO...")
    print("="*60)
    print(f"Veiculos: {num_vehicles}")
    print(f"Pontos: {num_points}")
    print(f"Geracoes: {num_generations}")
    
    # Carregar dados
    print("\nCarregando dados...")
    
    data_dir = project_root / 'data'
    delivery_points_file = data_dir / 'sample_delivery_points.json'
    vehicles_file = data_dir / 'sample_vehicles.json'
    
    # Verificar se arquivos existem
    if not delivery_points_file.exists():
        print(f"\nERRO: Arquivo nao encontrado!")
        print(f"   Esperado: {delivery_points_file}")
        sys.exit(1)
    
    # Carregar pontos de entrega (limitado ao número escolhido)
    with open(delivery_points_file, 'r', encoding='utf-8') as f:
        points_data = json.load(f)
    
    points_data = points_data[:num_points]
    points = [DeliveryPoint.from_dict(p) for p in points_data]
    print(f"Carregados {len(points)} pontos de entrega")
    
    # Carregar veículos (limitado ao número escolhido)
    with open(vehicles_file, 'r', encoding='utf-8') as f:
        vehicles_data = json.load(f)
    
    vehicles_data = vehicles_data[:num_vehicles]
    vehicles = [Vehicle.from_dict(v) for v in vehicles_data]
    print(f"Carregados {len(vehicles)} veiculos:")
    print()
    for i, vehicle in enumerate(vehicles):
        print(f"  Veiculo {i+1}: {vehicle.name}")
        print(f"    Capacidade: {vehicle.capacity_kg} kg | {vehicle.capacity_volume_m3} m³")
        print(f"    Autonomia: {vehicle.autonomy_km} km")
        print()
    
    # Depósito
    depot = (-23.5505, -46.6333)
    
    # Configurações do AG
    population_size = max(50, num_points * 5)
    
    config = {
        'population_size': population_size,
        'num_generations': num_generations,  # Usar o valor fornecido pelo usuário
        'crossover_rate': 0.8,
        'mutation_rate': 0.3,
        'elitism_rate': 0.1,
        'tournament_size': 3,
        'convergence_threshold': 0.0001,  # Mais rigoroso (era 0.001)
        'max_gens_without_improvement': num_generations,  # NUNCA para antes! (era num_generations // 10)
        'fitness_weights': {
            'distance': 1.0,
            'capacity': 1000.0,  # Penalidade MUITO ALTA (era 10.0) - quase hard constraint
            'autonomy': 1000.0,  # Penalidade MUITO ALTA (era 10.0) - quase hard constraint
            'priority': 5.0,
            'balance': 2.0,
            'num_vehicles': 3.0
        },
        'mutation_types': ['swap', 'inversion', 'move'],
        'mutation_weights': [0.4, 0.3, 0.3],
        'crossover_type': 'order',
        'selection_type': 'tournament',
        'enable_logging': True,
        'log_dir': 'logs/genetic'
    }
    
    print("\nConfiguracao do AG:")
    print(f"  Populacao: {config['population_size']}")
    print(f"  Geracoes: {config['num_generations']}")
    print(f"  Crossover: {config['crossover_rate']*100:.0f}% (tipo: {config['crossover_type']})")
    print(f"  Mutacao: {config['mutation_rate']*100:.0f}%")
    print(f"  Selecao: {config['selection_type']}")
    
    # Inicializar visualização Pygame
    print("\nIniciando visualizacao Pygame...")
    window_width, window_height = detect_display_size()
    print(f"Janela adaptativa detectada: {window_width}x{window_height}")
    
    viz = PygameVisualizer(width=window_width, height=window_height, fps=30)
    
    # Criar motor do AG
    print("\nInicializando Algoritmo Genetico...")
    ga = GeneticAlgorithm(
        delivery_points=points,
        vehicles=vehicles,
        depot_coord=depot,
        config=config
    )
    
    # Variáveis para armazenar estatísticas e detalhes
    current_stats = {}
    current_details = {}
    
    # Callback para atualizar visualização
    def update_visualization(ga_instance, generation, best_chromosome, avg_fitness):
        """Callback chamado a cada geração."""
        nonlocal current_stats, current_details
        
        # Obter estatísticas do AG
        current_stats = ga_instance.get_statistics()
        
        # Obter detalhes da melhor solução
        current_details = ga_instance.get_best_solution_details()
        
        # Extrair coordenadas dos pontos
        point_coords = [p.get_coordinates() for p in points]
        priorities = [p.priority.value for p in points]
        
        # Extrair rotas do melhor cromossomo
        routes = best_chromosome.get_routes()
        
        # Atualizar visualização com estatísticas e detalhes
        if not viz.update(
            delivery_points_coords=point_coords,
            delivery_points_priorities=priorities,
            routes=routes,
            depot_coord=depot,
            generation=generation,
            best_fitness=best_chromosome.fitness,
            ag_stats=current_stats,
            route_details=current_details
        ):
            return False
        
        return True
    
    print("\nControles:")
    print("  ESPACO - Pausar/Continuar")
    print("  S - Salvar screenshot")
    print("  Q - Sair")
    print("  Mouse - Clicar nos botoes para filtrar veiculos")
    
    print("\n" + "="*60)
    print("INICIANDO EVOLUCAO...")
    print("="*60 + "\n")
    
    # Executar AG com visualização
    simulation_context = None
    try:
        best_solution = ga.run(generation_callback=update_visualization)
        
        # Mostrar solução final
        print("\n" + "="*60)
        print("MELHOR SOLUCAO ENCONTRADA")
        print("="*60)
        
        details = ga.get_best_solution_details()
        stats = ga.get_statistics()
        
        print(f"\nFitness: {details['fitness']:.2f}")
        print(f"Distancia Total: {details['total_distance_km']:.2f} km")
        print(f"Veiculos Usados: {len(details['routes'])}")  # Corrigido: calcular a partir das rotas
        print(f"Total de Entregas: {details['total_deliveries']}")
        
        print(f"\nEstatisticas do AG:")
        print(f"  Crossovers: {stats['total_crossovers']}")
        print(f"  Mutacoes: {stats['total_mutations']}")
        print(f"  Tipo de Selecao: {stats['selection_type']}")
        print(f"  Tipo de Crossover: {stats['crossover_type']}")
        
        if stats['mutation_types']:
            print(f"\n  Tipos de Mutacao:")
            for mut_type, count in stats['mutation_types'].items():
                print(f"    - {mut_type}: {count}")
        
        print(f"\nRotas:")
        print(f"  {best_solution.to_string()}")

        # Salvar contexto para chat conversacional em tempo real
        try:
            session_dir = project_root / "outputs" / "session"
            session_dir.mkdir(parents=True, exist_ok=True)
            session_file = session_dir / "latest_context.json"

            simulation_context = {
                "routes": details["routes"],
                "vehicles": [
                    {
                        "name": v.name,
                        "capacity_kg": v.capacity_kg,
                        "capacity_volume_m3": v.capacity_volume_m3,
                        "autonomy_km": v.autonomy_km,
                    }
                    for v in vehicles
                ],
                "delivery_points": [
                    {
                        "name": p.name,
                        "priority": p.priority.name.lower(),
                        "weight_kg": p.weight_kg,
                        "volume_m3": p.volume_m3,
                        "address": getattr(p, "address", "N/A"),
                    }
                    for p in points
                ],
                "metrics": {
                    "total_distance": details.get("total_distance_km", 0),
                    "fitness": details.get("fitness", 0),
                    "capacity_violations": 0,
                    "autonomy_violations": 0,
                    "total_vehicles": len(vehicles),
                },
                "ga_stats": {
                    "total_generations": ga.current_generation,
                    "total_crossovers": stats.get("total_crossovers", 0),
                    "total_mutations": stats.get("total_mutations", 0),
                    "selection_type": stats.get("selection_type", "N/A"),
                    "crossover_type": stats.get("crossover_type", "N/A"),
                },
            }

            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(simulation_context, f, ensure_ascii=False, indent=2)
            print(f"\nContexto do chat salvo em: {session_file}")
        except Exception as context_error:
            print(f"\nAviso: nao foi possivel salvar contexto do chat: {context_error}")
        
        print(f"\nDetalhes por Veiculo:")
        violations_found = False
        for route_info in details['routes']:
            print(f"\n  {route_info['vehicle_name']}:")
            print(f"    Entregas: {route_info['num_deliveries']}")
            print(f"    Distancia: {route_info['distance_km']:.2f} km (Autonomia: {route_info.get('autonomy_km', 'N/A')} km)")
            
            # VERIFICAR VIOLAÇÃO DE AUTONOMIA
            autonomy_km = route_info.get('autonomy_km', float('inf'))
            if route_info['distance_km'] > autonomy_km:
                print(f"    ⚠️  VIOLACAO DE AUTONOMIA! Excesso: {route_info['distance_km'] - autonomy_km:.2f} km")
                violations_found = True
            
            print(f"    Carga: {route_info['load_kg']:.1f} / {route_info['capacity_kg']:.1f} kg "
                  f"({route_info['capacity_usage_%']:.1f}%)")
            
            # VERIFICAR VIOLAÇÃO DE CAPACIDADE
            if route_info['capacity_usage_%'] > 100:
                print(f"    ⚠️  VIOLACAO DE CAPACIDADE! Excesso: {route_info['capacity_usage_%'] - 100:.1f}%")
                violations_found = True
            
            print(f"    Rota: {' → '.join(route_info['points'])}")
        
        if violations_found:
            print(f"\n⚠️⚠️⚠️  ATENCAO: Solucao contém VIOLACOES de restricoes! ⚠️⚠️⚠️")
        
        print("\n" + "="*60)
        print(f"LOGS SALVOS EM: logs/genetic/")
        print("="*60)
        
        # GERAR MAPA HTML INTERATIVO (FOLIUM)
        print("\n" + "="*60)
        print("GERANDO MAPA HTML INTERATIVO...")
        print("="*60)
        
        try:
            # Preparar dados para o Folium
            folium_points = []
            for point in points:
                folium_points.append({
                    'name': point.name,
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'priority': point.priority.name,  # CRITICO, ALTO, MEDIO, BAIXO
                    'weight': point.weight_kg,
                    'volume': point.volume_m3,
                    'service_time_min': point.service_time_minutes,  # Corrigido: service_time_minutes
                    'description': getattr(point, 'description', point.item_description)  # Fallback para item_description
                })
            
            # Preparar dados dos veículos
            folium_vehicles = []
            for vehicle in vehicles:
                folium_vehicles.append({
                    'name': vehicle.name,
                    'capacity_kg': vehicle.capacity_kg,
                    'capacity_volume_m3': vehicle.capacity_volume_m3,
                    'autonomy_km': vehicle.autonomy_km
                })
            
            # Obter rotas do melhor cromossomo
            folium_routes = best_solution.get_routes()
            
            # Criar visualizador Folium
            folium_viz = FoliumVisualizer(center=depot)
            
            # Criar e salvar mapa
            mapa_html = folium_viz.create_and_save_map(
                delivery_points=folium_points,
                routes=folium_routes,
                vehicles=folium_vehicles,
                filename=f"rotas_otimizadas_{num_vehicles}v_{num_points}p_{num_generations}g.html",
                zoom_start=12
            )
            
            print(f"\n✅ Mapa HTML gerado com sucesso!")
            print(f"   Arquivo: {mapa_html.name}")
            print(f"   Local: {mapa_html.parent}")
            print(f"\n💡 Abra o arquivo no navegador para visualizar o mapa interativo!")
            
        except Exception as e:
            print(f"\n❌ ERRO ao gerar mapa Folium: {e}")
            print("   A simulacao continuara normalmente.")
        
        print("="*60)
        
        # GERAR INSTRUÇÕES PARA MOTORISTAS (LLM)
        print("\n" + "="*60)
        print("GERANDO INSTRUÇÕES PARA MOTORISTAS (LLM)...")
        print("="*60)
        
        try:
            # Inicializar gerador de instruções (Ollama local)
            instruction_gen = InstructionGenerator(provider="ollama", model="llama2")
            
            # Gerar instruções para cada veículo
            for i, route_info in enumerate(details['routes']):
                print(f"\n📝 Gerando instruções para: {route_info['vehicle_name']}")
                
                # Preparar dados do veículo
                vehicle_data = {
                    'name': route_info['vehicle_name'],
                    'capacity_kg': route_info['capacity_kg'],
                    'autonomy_km': route_info.get('autonomy_km', 'N/A'),
                    'vehicle_type': vehicles[i].vehicle_type if i < len(vehicles) else 'Van',
                    'is_refrigerated': vehicles[i].is_refrigerated if i < len(vehicles) else False
                }
                
                # Preparar dados dos pontos da rota
                route_points_data = []
                route = best_solution.get_routes()[i]
                for point_idx in route:
                    if point_idx < len(points):
                        p = points[point_idx]
                        route_points_data.append({
                            'name': p.name,
                            'address': getattr(p, 'address', 'N/A'),
                            'priority': p.priority.name,
                            'weight': p.weight_kg,
                            'volume': p.volume_m3
                        })
                
                # Gerar instruções
                instructions = instruction_gen.generate_instructions(
                    vehicle=vehicle_data,
                    route_points=route_points_data,
                    total_distance=route_info['distance_km'],
                    estimated_time=route_info['distance_km'] / 40.0  # ~40 km/h
                )
                
                # Salvar instruções
                filename = f"instrucoes_{route_info['vehicle_name'].replace(' ', '_')}_{num_vehicles}v_{num_points}p.txt"
                instruction_gen.save_instructions(instructions, filename)
            
            print(f"\n✅ Instruções geradas com sucesso para todos os veículos!")
            
        except ImportError as e:
            print(f"\n⚠️ LLM não disponível: {e}")
            print("   Para usar LLM, instale o Ollama: https://ollama.ai/download/windows")
            print("   E execute: pip install ollama")
            print("   Consulte: COMECE_AQUI_LLM.txt")
        
        except Exception as e:
            print(f"\n❌ ERRO ao gerar instruções: {e}")
            print("   A simulacao continuara normalmente.")
            print("   Verifique se o Ollama está rodando: ollama serve")
        
        print("="*60)
        
        # GERAR RELATÓRIO DE EFICIÊNCIA (LLM)
        print("\n" + "="*60)
        print("GERANDO RELATÓRIO DE EFICIÊNCIA (LLM)...")
        print("="*60)
        
        try:
            # Inicializar gerador de relatórios (Ollama local)
            report_gen = ReportGenerator(provider="ollama", model="llama2")
            
            # Preparar métricas
            metrics_data = {
                'total_distance': details.get('total_distance', 0),
                'total_vehicles': len(vehicles),
                'total_deliveries': sum(r['num_deliveries'] for r in details['routes']),
                'violations': 0  # Podemos melhorar isso depois
            }
            
            # Gerar relatório
            report = report_gen.generate_report(
                metrics=metrics_data,
                ga_stats=stats,
                route_details=details['routes']
            )
            
            # Salvar relatório
            filename = f"relatorio_{num_vehicles}v_{num_points}p_{num_generations}g"
            report_gen.save_report(report, prefix=filename)
            
            print(f"\n✅ Relatório gerado com sucesso!")
            
        except ImportError as e:
            print(f"\n⚠️ LLM não disponível: {e}")
            print("   Para usar LLM, instale o Ollama: https://ollama.ai/download/windows")
            print("   E execute: pip install ollama")
            print("   Consulte: COMECE_AQUI_LLM.txt")
        
        except Exception as e:
            print(f"\n❌ ERRO ao gerar relatório: {e}")
            print("   A simulacao continuara normalmente.")
            print("   Verifique se o Ollama está rodando: ollama serve")
        
        print("="*60)
        
        # Manter visualização aberta INDEFINIDAMENTE
        print("\n" + "="*60)
        print("SIMULACAO CONCLUIDA!")
        print("="*60)
        print("\nA janela permanecera aberta para analise.")
        print("\nControles:")
        print("  ESPACO - Pausar/Retomar")
        print("  S - Salvar screenshot")
        print("  Mouse - Clicar nos botoes de veiculos para filtrar")
        print("  Q - Sair")
        print("\nPressione Q na janela Pygame para encerrar.")
        print("="*60)
        
        # Loop INFINITO para manter janela aberta
        # A janela só fecha quando o usuário pressionar Q
        while viz.running:
            viz.handle_events()
            
            # Continuar exibindo a melhor solução
            point_coords = [p.get_coordinates() for p in points]
            priorities = [p.priority.value for p in points]
            routes = best_solution.get_routes()
            
            viz.update(
                delivery_points_coords=point_coords,
                delivery_points_priorities=priorities,
                routes=routes,
                depot_coord=depot,
                generation=ga.current_generation,
                best_fitness=best_solution.fitness,
                ag_stats=stats,
                route_details=details
            )
            
            viz.clock.tick(10)  # 10 FPS para economizar recursos
        return simulation_context
    
    except KeyboardInterrupt:
        print("\n\nExecucao interrompida pelo usuario.")
        viz.close()
        return simulation_context
    
    except Exception as e:
        print(f"\n\nERRO: {e}")
        import traceback
        traceback.print_exc()
        viz.close()
        return simulation_context
    
    # NÃO usar finally para não fechar prematuramente


if __name__ == '__main__':
    # Mostrar tela de configuracao com tamanho adaptado ao monitor
    config_screen = ConfigScreen()
    result = config_screen.run()
    
    if result:
        num_vehicles, num_points, num_generations = result
        # Executar simulação com os parâmetros escolhidos
        simulation_context = run_simulation(num_vehicles, num_points, num_generations)
        
        # Após fechar Pygame, oferecer sessão de Q&A
        print("\n" + "="*60)
        print("SIMULACAO CONCLUIDA!")
        print("="*60)
        
        print("\nDeseja fazer perguntas sobre as rotas otimizadas agora? (s/n): ", end="")
        try:
            choice = input().strip().lower()
            if choice in ('s', 'sim'):
                print("\n" + "="*60)
                print("INICIANDO SESSAO DE PERGUNTAS E RESPOSTAS (Q&A)")
                print("="*60)
                print("\nCarregando chat conversacional com dados da ultima otimizacao...")
                
                try:
                    from src.llm_integration import QASystem, interactive_qa_session
                    
                    # Configurar sistema Q&A
                    qa = QASystem(provider="ollama", model="llama2")
                    if simulation_context:
                        qa.load_context(
                            routes=simulation_context["routes"],
                            vehicles=simulation_context["vehicles"],
                            delivery_points=simulation_context["delivery_points"],
                            metrics=simulation_context["metrics"],
                            ga_stats=simulation_context.get("ga_stats", {}),
                        )
                        interactive_qa_session(qa, stream=True)
                    else:
                        print("\nNao foi possivel carregar o contexto da simulacao.")
                        print("Execute novamente e tente abrir o chat ao final.")
                    
                except ImportError as e:
                    print(f"\nErro ao carregar sistema Q&A: {e}")
                    print("Certifique-se de que o pacote ollama e o servidor local estao disponiveis.")
        
        except (EOFError, KeyboardInterrupt):
            print("\n")
        
        # Mensagem final
        print("\n" + "="*60)
        print("Execucao finalizada!")
        print("="*60)
        print("\nArquivos gerados em:")
        print("   • outputs/maps/           (mapas HTML)")
        print("   • outputs/instructions/   (instruções motoristas)")
        print("   • outputs/reports/        (relatórios gerenciais)")
        print("   • outputs/session/        (contexto para chat)")
        print("\nPara conversar novamente com o Llama em tempo real:")
        print("   python chat_realtime.py")
        print()
    else:
        print("\nConfiguracao cancelada pelo usuario.")
