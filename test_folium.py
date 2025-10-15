"""
Script de Teste para o Visualizador Folium.

Este script testa a geração de mapas HTML interativos usando os dados
de exemplo do projeto.
"""
import json
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.visualization.folium_visualizer import FoliumVisualizer, generate_route_map, get_point_label


def test_folium_basic():
    """Teste básico do visualizador Folium."""
    
    print("="*70)
    print("TESTE DO VISUALIZADOR FOLIUM")
    print("="*70)
    print()
    
    # Carregar dados de exemplo
    print("📂 Carregando dados de exemplo...")
    
    data_dir = project_root / "data"
    
    # Carregar pontos de entrega
    with open(data_dir / "sample_delivery_points.json", 'r', encoding='utf-8') as f:
        all_points = json.load(f)
    
    # Carregar veículos
    with open(data_dir / "sample_vehicles.json", 'r', encoding='utf-8') as f:
        vehicles = json.load(f)
    
    print(f"   ✓ {len(all_points)} pontos de entrega carregados")
    print(f"   ✓ {len(vehicles)} veículos carregados")
    print()
    
    # Usar apenas primeiros 15 pontos
    delivery_points = all_points[:15]
    
    # Definir rotas de exemplo (3 veículos)
    # Rota 1: Pontos 0, 2, 4, 7, 9 (5 entregas)
    # Rota 2: Pontos 1, 3, 5, 8, 10, 12 (6 entregas)
    # Rota 3: Pontos 6, 11, 13, 14 (4 entregas)
    routes = [
        [0, 2, 4, 7, 9],      # Veículo 1 - Van Refrigerada 01
        [1, 3, 5, 8, 10, 12], # Veículo 2 - Van Padrão 02
        [6, 11, 13, 14]       # Veículo 3 - Caminhonete 03
    ]
    
    print("🗺️ Criando mapa interativo...")
    print(f"   • 3 veículos")
    print(f"   • 15 pontos de entrega")
    print(f"   • {sum(len(r) for r in routes)} entregas totais")
    print()
    
    # Exibir detalhes das rotas
    print("📋 DETALHES DAS ROTAS:")
    print("-" * 70)
    for i, route in enumerate(routes, 1):
        vehicle = vehicles[i-1]
        route_letters = ' → '.join([get_point_label(idx) for idx in route])
        print(f"   Veículo {i} - {vehicle['name']}")
        print(f"   └─ {len(route)} entregas: Depósito → {route_letters} → Depósito")
    print("-" * 70)
    print()
    
    # Criar visualizador
    viz = FoliumVisualizer()
    
    # Criar mapa
    mapa = viz.create_map(
        delivery_points=delivery_points,
        routes=routes,
        vehicles=vehicles[:3],  # Usar apenas os 3 primeiros veículos
        zoom_start=12,
        show_route_arrows=True
    )
    
    # Salvar mapa
    filepath = viz.save_map(mapa, "teste_rotas_exemplo.html")
    
    # Informações finais
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print()
    print("📍 RECURSOS DO MAPA:")
    print("   • Marcadores coloridos por prioridade")
    print("   • Linhas coloridas para cada veículo")
    print("   • Setas animadas mostrando direção")
    print("   • Popups clicáveis com informações")
    print("   • Legenda interativa")
    print("   • Mini mapa de navegação")
    print("   • Controle de tela cheia")
    print("   • Zoom e navegação")
    print()
    print("🌐 COMO VISUALIZAR:")
    print(f"   1. Abra o arquivo: {filepath.absolute()}")
    print("   2. Use qualquer navegador (Chrome, Firefox, Edge, etc.)")
    print("   3. Clique nos marcadores para ver detalhes")
    print("   4. Clique nas linhas para ver informações da rota")
    print()
    print("="*70)
    
    return filepath


def test_folium_quick():
    """Teste usando a função auxiliar rápida."""
    
    print()
    print("="*70)
    print("TESTE RÁPIDO (usando função auxiliar)")
    print("="*70)
    print()
    
    # Carregar dados usando project_root
    data_dir = project_root / "data"
    
    with open(data_dir / "sample_delivery_points.json", 'r', encoding='utf-8') as f:
        points = json.load(f)[:15]
    
    with open(data_dir / "sample_vehicles.json", 'r', encoding='utf-8') as f:
        vehicles = json.load(f)
    
    # Rotas simples
    routes = [
        [0, 1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12, 13, 14]
    ]
    
    print("🚀 Gerando mapa com função auxiliar...")
    
    # Gerar mapa usando função auxiliar
    filepath = generate_route_map(
        delivery_points=points,
        routes=routes,
        vehicles=vehicles[:3],
        output_filename="teste_rotas_rapido.html"
    )
    
    print(f"✅ Mapa gerado: {filepath.name}")
    print()
    
    return filepath


if __name__ == "__main__":
    try:
        # Teste básico
        filepath1 = test_folium_basic()
        
        # Teste rápido
        filepath2 = test_folium_quick()
        
        print()
        print("🎉 TODOS OS TESTES PASSARAM!")
        print()
        print("📁 ARQUIVOS GERADOS:")
        print(f"   1. {filepath1.name}")
        print(f"   2. {filepath2.name}")
        print()
        print("💡 DICA: Arraste os arquivos .html para o navegador!")
        print()
        
    except FileNotFoundError as e:
        print()
        print("❌ ERRO: Arquivo não encontrado!")
        print(f"   {e}")
        print()
        print("💡 Certifique-se de executar este script do diretório Tech-Challange-2/")
        print()
        
    except Exception as e:
        print()
        print("❌ ERRO INESPERADO:")
        print(f"   {e}")
        print()
        import traceback
        traceback.print_exc()

