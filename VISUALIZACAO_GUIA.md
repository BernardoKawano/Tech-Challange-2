# 🎨 Guia de Visualização - Pygame vs Folium

## 📊 Duas Abordagens Complementares

O projeto suporta **duas formas de visualização**, cada uma com seu propósito:

---

## 🎮 1. Pygame - Visualização em Tempo Real

### 📝 Quando Usar:
- ✅ **Durante desenvolvimento** - ver o AG evoluindo
- ✅ **Debugging** - identificar problemas visualmente
- ✅ **Tuning de parâmetros** - ajustar e ver resultado imediato
- ✅ **Demonstrações ao vivo** - mostrar o sistema funcionando

### ⚡ Vantagens:
- Vê a evolução **frame a frame**
- Gráfico de convergência em tempo real
- Interativo (pausar, screenshot)
- Feedback visual imediato

### 🎯 Como Usar:

```python
from src.visualization.pygame_visualizer import PygameVisualizer
from src.genetic_algorithm.vrp_solver import VRPSolver
from src.utils.data_loader import load_delivery_points, load_vehicles

# Carregar dados
points = load_delivery_points('data/sample_delivery_points.json')
vehicles = load_vehicles('data/sample_vehicles.json')

# Criar solver
solver = VRPSolver(points, vehicles)

# Criar visualizador
viz = PygameVisualizer(width=1200, height=600)

# Executar com visualização em tempo real
for generation in range(500):
    # Evoluir uma geração
    solver.evolve_one_generation()
    
    # Obter melhor solução atual
    best_solution = solver.get_best_solution()
    
    # Extrair dados para visualização
    point_coords = [p.get_coordinates() for p in points]
    priorities = [p.priority.value for p in points]
    routes = best_solution.get_routes_as_indices()
    depot = solver.depot_location
    
    # Atualizar visualização
    if not viz.update(
        point_coords, 
        priorities, 
        routes, 
        depot,
        generation,
        best_solution.fitness
    ):
        break  # Usuário fechou a janela

viz.close()
```

### 🎮 Controles:
- **ESPAÇO** - Pausar/Continuar
- **S** - Salvar screenshot
- **Q** - Sair

### 📸 Capturas de Tela:
Screenshots são salvos automaticamente como `screenshot_gen_X.png`

---

## 🗺️ 2. Folium - Mapas Interativos Reais

### 📝 Quando Usar:
- ✅ **Resultado final** - apresentar solução otimizada
- ✅ **Relatórios** - documentar e compartilhar
- ✅ **Mapas reais** - ver rotas em contexto geográfico real
- ✅ **Análise detalhada** - clicar e explorar informações

### ⚡ Vantagens:
- Mapas **reais** (OpenStreetMap)
- Exporta **HTML** para compartilhar
- Popups com **informações detalhadas**
- Zoom e navegação interativa
- Perfeito para **apresentações**

### 🎯 Como Usar:

```python
from src.visualization.map_plotter import MapPlotter
from src.genetic_algorithm.vrp_solver import VRPSolver

# Após otimização completa
solver = VRPSolver(points, vehicles)
solver.optimize(generations=500)  # Executa sem visualização

# Obter melhor solução
best_solution = solver.get_best_solution()

# Criar mapa
plotter = MapPlotter(center=[-23.5505, -46.6333], zoom=12)

# Adicionar depósito
plotter.add_depot(
    location=(-23.5505, -46.6333),
    name="Hospital Central",
    popup_text="Depósito - Ponto de partida"
)

# Adicionar rotas
for vehicle_idx, route in enumerate(best_solution.routes):
    plotter.add_route(
        route=route,
        vehicle_name=f"Veículo {vehicle_idx + 1}",
        color=plotter.get_vehicle_color(vehicle_idx)
    )

# Salvar mapa
plotter.save('outputs/rotas_otimizadas.html')
print("Mapa salvo em outputs/rotas_otimizadas.html")
```

### 🌐 Resultado:
Abre o arquivo HTML em qualquer navegador e explora o mapa interativo!

---

## 🔄 3. Abordagem Híbrida (Recomendada)

### 💡 Melhor dos Dois Mundos:

```python
from src.visualization.pygame_visualizer import PygameVisualizer
from src.visualization.map_plotter import MapPlotter
from src.genetic_algorithm.vrp_solver import VRPSolver

# 1. Desenvolvimento com Pygame
print("Otimizando rotas com visualização em tempo real...")

viz = PygameVisualizer()
solver = VRPSolver(points, vehicles)

for generation in range(500):
    solver.evolve_one_generation()
    best = solver.get_best_solution()
    
    # Atualizar visualização Pygame
    viz.update(
        [p.get_coordinates() for p in points],
        [p.priority.value for p in points],
        best.get_routes_as_indices(),
        solver.depot_location,
        generation,
        best.fitness
    )

viz.close()

# 2. Resultado final com Folium
print("\nGerando mapa interativo final...")

plotter = MapPlotter()
plotter.add_depot(solver.depot_location, "Hospital Central")

for idx, route in enumerate(solver.get_best_solution().routes):
    plotter.add_route(route, f"Veículo {idx+1}")

plotter.save('outputs/resultado_final.html')
print("✅ Mapa salvo! Abra outputs/resultado_final.html")
```

---

## 📊 Comparação Lado a Lado

| Recurso | Pygame | Folium |
|---------|--------|--------|
| **Tempo Real** | ✅ Sim | ❌ Não |
| **Mapas Reais** | ❌ Não | ✅ Sim |
| **Interativo** | ✅ Durante execução | ✅ Após execução |
| **Exportável** | Screenshots | HTML completo |
| **Gráficos** | ✅ Convergência | ❌ Não |
| **Popups** | ❌ Não | ✅ Sim |
| **Para Relatórios** | ⚠️ Screenshots | ✅ Ideal |
| **Para Debugging** | ✅ Ideal | ❌ Não |

---

## 🎯 Recomendação por Uso

### 🔧 Durante Desenvolvimento:
```python
# Use Pygame
viz = PygameVisualizer()
# ... desenvolvimento e ajustes ...
```

### 📊 Para Apresentação/Relatório:
```python
# Use Folium
plotter = MapPlotter()
# ... gerar mapa final ...
```

### 🚀 Para Demonstração Completa:
```python
# Use ambos!
# 1. Pygame durante otimização
# 2. Folium para resultado final
```

---

## 💻 Código Completo de Exemplo

### `exemplo_visualizacao_completa.py`

```python
"""
Exemplo completo mostrando ambas as visualizações.
"""

from src.models import DeliveryPoint, Vehicle, Priority
from src.visualization.pygame_visualizer import PygameVisualizer
# from src.visualization.map_plotter import MapPlotter (a criar)
import json

# Carregar dados
with open('data/sample_delivery_points.json', 'r', encoding='utf-8') as f:
    points_data = json.load(f)

with open('data/sample_vehicles.json', 'r', encoding='utf-8') as f:
    vehicles_data = json.load(f)

points = [DeliveryPoint.from_dict(p) for p in points_data]
vehicles = [Vehicle.from_dict(v) for v in vehicles_data]

print(f"✅ Carregados {len(points)} pontos e {len(vehicles)} veículos")

# Depot (Hospital Central)
depot = (-23.5505, -46.6333)

# ====================================
# PARTE 1: Visualização com Pygame
# ====================================

print("\n🎮 Iniciando visualização Pygame...")
print("Controles: ESPAÇO (pausar), S (screenshot), Q (sair)")

viz = PygameVisualizer(width=1200, height=600, fps=30)

# Simulação de evolução (substituir por AG real)
import random

generation = 0
max_generations = 100

while viz.running and generation < max_generations:
    # AQUI VIRIA: solver.evolve_one_generation()
    
    # Simulando rotas (dividir pontos entre veículos)
    num_vehicles = 3
    routes = []
    points_per_vehicle = len(points) // num_vehicles
    
    for v in range(num_vehicles):
        start_idx = v * points_per_vehicle
        end_idx = start_idx + points_per_vehicle if v < num_vehicles - 1 else len(points)
        routes.append(list(range(start_idx, end_idx)))
    
    # Simular melhoria de fitness
    fitness = 1000 - (generation * 5) + random.randint(-10, 10)
    
    # Atualizar visualização
    point_coords = [p.get_coordinates() for p in points]
    priorities = [p.priority.value for p in points]
    
    if not viz.update(point_coords, priorities, routes, depot, generation, fitness):
        print("Usuário fechou a janela.")
        break
    
    generation += 1

viz.close()

print(f"\n✅ Pygame concluído após {generation} gerações")

# ====================================
# PARTE 2: Mapa Folium (a implementar)
# ====================================

print("\n🗺️ Gerando mapa interativo Folium...")
print("(A implementar em map_plotter.py)")

# plotter = MapPlotter(center=depot, zoom=12)
# plotter.add_depot(depot, "Hospital Central")
# 
# for idx, route in enumerate(final_routes):
#     plotter.add_route(route, f"Veículo {idx+1}")
# 
# plotter.save('outputs/rotas_finais.html')
# print("✅ Mapa salvo em outputs/rotas_finais.html")

print("\n✨ Visualização completa!")
```

---

## 🎬 Próximos Passos

### 1. **Testar Pygame** (Já implementado)
```bash
cd Tech-Challange-2
python src/visualization/pygame_visualizer.py
```

### 2. **Implementar MapPlotter (Folium)**
- Criar `src/visualization/map_plotter.py`
- Usar biblioteca Folium
- Adicionar popups com informações

### 3. **Integrar com VRP Solver**
- Conectar visualizadores ao AG real
- Adicionar opção `--visualize` no main.py

---

## 📚 Recursos

### Pygame:
- [Pygame Tutorial](https://www.pygame.org/docs/)
- [Código Base TSP](../genetic_algorithm_tsp/tsp.py) - Já usa Pygame!

### Folium:
- [Folium Docs](https://python-visualization.github.io/folium/)
- [Exemplos](https://nbviewer.org/github/python-visualization/folium/tree/main/examples/)

---

**🎨 Use Pygame durante desenvolvimento, Folium para relatórios!**

*Atualizado: 14 de Outubro de 2025*

