"""
Script de Demonstração do Sistema de Q&A (Perguntas e Respostas).

Permite fazer perguntas em linguagem natural sobre rotas otimizadas.
"""

import sys
from pathlib import Path

# Adicionar src ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.llm_integration import QASystem, interactive_qa_session


def demo_qa_system():
    """Demonstração do sistema de Q&A com dados de exemplo."""
    
    print("="*70)
    print(" DEMONSTRAÇÃO: SISTEMA DE PERGUNTAS E RESPOSTAS SOBRE ROTAS")
    print("="*70)
    
    # 1. Configurar sistema Q&A
    print("\n1️⃣  Configurando sistema Q&A...")
    
    try:
        qa = QASystem(provider="ollama", model="llama2")
    except Exception as e:
        print(f"\n❌ Erro ao configurar Ollama: {e}")
        print("\n💡 Certifique-se de que:")
        print("   • Ollama está instalado: https://ollama.ai")
        print("   • Servidor está rodando: ollama serve")
        print("   • Modelo foi baixado: ollama pull llama2")
        return
    
    # 2. Carregar contexto de exemplo
    print("\n2️⃣  Carregando contexto de rotas...")
    
    # Dados de exemplo (simula resultado de otimização)
    routes = [
        {
            'vehicle_name': 'Van Refrigerada 01',
            'points': ['A', 'C', 'E', 'G'],
            'distance_km': 42.5,
            'capacity_usage_percent': 78.5,
            'load_kg': 118.0,
            'capacity_kg': 150.0
        },
        {
            'vehicle_name': 'Van Padrão 02',
            'points': ['B', 'D', 'F'],
            'distance_km': 28.3,
            'capacity_usage_percent': 62.8,
            'load_kg': 113.0,
            'capacity_kg': 180.0
        },
        {
            'vehicle_name': 'Caminhonete 03',
            'points': ['H', 'I', 'J', 'K'],
            'distance_km': 38.7,
            'capacity_usage_percent': 45.2,
            'load_kg': 113.0,
            'capacity_kg': 250.0
        }
    ]
    
    vehicles = [
        {'name': 'Van Refrigerada 01', 'capacity_kg': 150, 'autonomy_km': 200, 'is_refrigerated': True},
        {'name': 'Van Padrão 02', 'capacity_kg': 180, 'autonomy_km': 250, 'is_refrigerated': False},
        {'name': 'Caminhonete 03', 'capacity_kg': 250, 'autonomy_km': 300, 'is_refrigerated': False}
    ]
    
    delivery_points = [
        {'name': 'Hospital das Clínicas', 'priority': 'critico', 'weight_kg': 35.5},
        {'name': 'UBS Vila Mariana', 'priority': 'critico', 'weight_kg': 15.5},
        {'name': 'Hospital Sírio-Libanês', 'priority': 'critico', 'weight_kg': 32.0},
        {'name': 'Clínica Santa Cruz', 'priority': 'alto', 'weight_kg': 8.2},
        {'name': 'Centro de Saúde Mooca', 'priority': 'alto', 'weight_kg': 18.7},
        {'name': 'UPA Penha', 'priority': 'alto', 'weight_kg': 16.9},
        {'name': 'Hospital São Camilo', 'priority': 'critico', 'weight_kg': 25.0},
        {'name': 'Farmácia Popular', 'priority': 'medio', 'weight_kg': 12.5},
        {'name': 'Casa de Repouso', 'priority': 'baixo', 'weight_kg': 6.5},
        {'name': 'Centro Médico', 'priority': 'baixo', 'weight_kg': 7.2},
        {'name': 'Consultório', 'priority': 'baixo', 'weight_kg': 4.5}
    ]
    
    metrics = {
        'total_distance': 109.5,
        'fitness': 125.8,
        'capacity_violations': 0,
        'autonomy_violations': 0,
        'total_vehicles': 3
    }
    
    ga_stats = {
        'total_generations': 500,
        'total_crossovers': 1250,
        'total_mutations': 375
    }
    
    qa.load_context(
        routes=routes,
        vehicles=vehicles,
        delivery_points=delivery_points,
        metrics=metrics,
        ga_stats=ga_stats
    )
    
    # 3. Exemplos de perguntas
    print("\n3️⃣  Exemplos de perguntas...")
    print("\n" + "-"*70)
    
    example_questions = [
        "Qual veículo tem a maior distância a percorrer?",
        "Algum veículo está com capacidade muito baixa?",
        "Quantas entregas críticas temos no total?",
        "Qual é a eficiência geral das rotas?",
    ]
    
    print("\n📝 Exemplos de perguntas que você pode fazer:")
    for i, q in enumerate(example_questions, 1):
        print(f"   {i}. {q}")
    
    # 4. Testar algumas perguntas automaticamente
    print("\n\n4️⃣  Testando perguntas automaticamente...\n")
    
    # Pergunta 1
    print("-"*70)
    response = qa.ask(example_questions[0])
    print(f"\n📊 Resposta:\n{response}\n")
    
    # Pergunta 2
    print("-"*70)
    response = qa.ask(example_questions[2])
    print(f"\n📊 Resposta:\n{response}\n")
    
    # 5. Sugestões de melhoria
    print("-"*70)
    print("\n5️⃣  Gerando sugestões de melhoria...\n")
    suggestions = qa.suggest_improvements()
    print(f"💡 Sugestões:\n{suggestions}\n")
    
    # 6. Identificar gargalos
    print("-"*70)
    print("\n6️⃣  Identificando gargalos...\n")
    bottlenecks = qa.find_bottlenecks()
    print(f"⚠️  Gargalos:\n{bottlenecks}\n")
    
    print("-"*70)
    
    # 7. Sessão interativa (opcional)
    print("\n\n7️⃣  Sessão Interativa (OPCIONAL)")
    print("\nDeseja iniciar uma sessão interativa de perguntas? (s/n): ", end='')
    
    try:
        choice = input().strip().lower()
        if choice == 's':
            interactive_qa_session(qa)
    except (EOFError, KeyboardInterrupt):
        print("\n\nSessão cancelada.")
    
    # 8. Exportar log
    print("\n\n8️⃣  Exportando log de perguntas...")
    output_path = project_root / "outputs" / "reports" / "qa_log_demo.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    qa.export_qa_log(str(output_path))
    
    print("\n" + "="*70)
    print(" DEMONSTRAÇÃO CONCLUÍDA!")
    print("="*70)
    print(f"\n📁 Log salvo em: {output_path}")
    print("\n💡 Para usar no seu código:")
    print("   from src.llm_integration import QASystem")
    print("   qa = QASystem(provider='ollama', model='llama2')")
    print("   qa.load_context(routes, vehicles, points, metrics)")
    print("   resposta = qa.ask('Sua pergunta aqui')")
    print()


if __name__ == "__main__":
    try:
        demo_qa_system()
    except KeyboardInterrupt:
        print("\n\n👋 Demonstração interrompida. Até logo!")
    except Exception as e:
        print(f"\n❌ Erro na demonstração: {e}")
        import traceback
        traceback.print_exc()

