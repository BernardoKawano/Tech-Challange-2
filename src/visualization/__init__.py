"""
Módulo de visualização de rotas e métricas.

Este módulo oferece duas formas de visualização:

1. **Pygame** - Visualização em tempo real durante execução do AG
   - Vê a evolução frame a frame
   - Gráficos de convergência
   - Controles interativos

2. **Folium** - Mapas interativos após otimização
   - Mapas reais do mundo
   - Exporta HTML
   - Ideal para relatórios

Consulte VISUALIZACAO_GUIA.md para detalhes completos.
"""

from .pygame_visualizer import PygameVisualizer

# Importações serão adicionadas conforme implementadas
# from .map_plotter import MapPlotter, plot_routes

__all__ = ['PygameVisualizer']
