# 🏥 Sistema de Otimização de Rotas Médicas

**Tech Challenge IADT - Fase 2**

Sistema de otimização de rotas para distribuição de medicamentos e insumos hospitalares utilizando Algoritmos Genéticos e integração com LLMs para geração de relatórios e instruções.

---

## 📋 Visão Geral

Este projeto resolve o problema do "Caixeiro Viajante Médico" (TSP/VRP) aplicado ao contexto hospitalar, considerando:

- ✅ Prioridades de entrega (crítico, alto, médio, baixo)
- ✅ Capacidade limitada de carga dos veículos
- ✅ Autonomia limitada dos veículos
- ✅ Múltiplos veículos (VRP - Vehicle Routing Problem)
- ✅ Geração automática de instruções via LLM
- ✅ Relatórios de eficiência e sugestões de melhorias

---

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.9+
- pip ou Poetry

### Instalação

```bash
# Clonar o repositório
git clone <url-do-repositorio>
cd Tech-Challange-2

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### Configuração

1. Copiar arquivo de exemplo de configuração:
```bash
cp config/config.example.json config/config.json
```

2. Adicionar sua API key da LLM em `config/config.json`

### Executar

```bash
# Executar otimização de rotas
python src/main.py

# Executar com visualização
python src/main.py --visualize

# Executar notebook de demonstração
jupyter notebook notebooks/demo_otimizacao.ipynb
```

---

## 📁 Estrutura do Projeto

```
Tech-Challange-2/
├── README.md                      # Este arquivo
├── requirements.txt               # Dependências do projeto
├── .gitignore                     # Arquivos a ignorar no Git
├── config/
│   ├── config.example.json        # Exemplo de configuração
│   └── config.json                # Configuração local (não versionado)
├── src/
│   ├── __init__.py
│   ├── main.py                    # Ponto de entrada principal
│   ├── genetic_algorithm/
│   │   ├── __init__.py
│   │   ├── tsp_base.py           # Código base TSP adaptado
│   │   ├── vrp_solver.py         # Solver VRP com restrições
│   │   ├── operators.py          # Operadores genéticos
│   │   └── fitness.py            # Funções de fitness
│   ├── models/
│   │   ├── __init__.py
│   │   ├── delivery_point.py     # Modelo de ponto de entrega
│   │   ├── vehicle.py            # Modelo de veículo
│   │   └── route.py              # Modelo de rota
│   ├── constraints/
│   │   ├── __init__.py
│   │   ├── capacity.py           # Restrição de capacidade
│   │   ├── priority.py           # Restrição de prioridade
│   │   └── autonomy.py           # Restrição de autonomia
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── map_plotter.py        # Plotagem em mapas
│   │   └── dashboard.py          # Dashboard interativo
│   ├── llm_integration/
│   │   ├── __init__.py
│   │   ├── instructions_generator.py  # Gera instruções
│   │   ├── report_generator.py       # Gera relatórios
│   │   └── prompts.py                # Templates de prompts
│   └── utils/
│       ├── __init__.py
│       ├── distance_calculator.py  # Cálculo de distâncias
│       └── data_loader.py          # Carregamento de dados
├── tests/
│   ├── __init__.py
│   ├── test_genetic_algorithm.py
│   ├── test_constraints.py
│   ├── test_models.py
│   └── test_llm_integration.py
├── data/
│   ├── sample_delivery_points.json  # Pontos de entrega exemplo
│   ├── sample_vehicles.json         # Frota exemplo
│   └── real_addresses.json          # Endereços reais (opcional)
├── notebooks/
│   ├── demo_otimizacao.ipynb       # Demonstração do sistema
│   ├── analise_performance.ipynb   # Análise de performance
│   └── comparativo_algoritmos.ipynb # Comparativo com outros métodos
├── docs/
│   ├── arquitetura.md              # Documentação da arquitetura
│   ├── algoritmo_genetico.md       # Detalhes do AG
│   ├── relatorio_tecnico.md        # Relatório técnico completo
│   └── diagramas/                  # Diagramas do sistema
└── scripts/
    ├── generate_test_data.py       # Gerar dados de teste
    └── benchmark.py                # Benchmarking

```

---

## 🧬 Algoritmo Genético - Detalhes Técnicos

### Representação Genética

Cada cromossomo representa uma solução para o problema de múltiplos veículos:
- **Cromossomo**: `[R1, R2, ..., Rn]` onde cada `Ri` é uma rota de um veículo
- **Rota**: Sequência de pontos de entrega `[P1, P2, ..., Pk]`

### Operadores Genéticos

1. **Seleção**: Torneio com elitismo
2. **Crossover**: Order Crossover (OX) adaptado para VRP
3. **Mutação**: 
   - Swap (troca de posições)
   - Inversão de segmento
   - Realocação entre veículos

### Função de Fitness Multi-Critério

```python
fitness = w1 * distancia_total 
        + w2 * penalizacao_capacidade 
        + w3 * penalizacao_autonomia
        - w4 * bonus_prioridades
        + w5 * penalizacao_balanceamento
```

---

## 🤖 Integração com LLM

### Funcionalidades

1. **Geração de Instruções para Motoristas**
   - Passo a passo detalhado
   - Observações sobre prioridades
   - Alertas especiais

2. **Relatórios de Eficiência**
   - Análise de performance
   - Comparativos temporais
   - Identificação de padrões

3. **Sistema de Perguntas e Respostas**
   - Interface em linguagem natural
   - Consultas sobre rotas
   - Sugestões de otimização

### LLMs Suportadas

- OpenAI GPT-4 / GPT-3.5
- Anthropic Claude
- Modelos locais via Ollama

---

## 📊 Visualização

O sistema oferece **duas formas de visualização**:

### 🎮 1. Pygame - Tempo Real

Visualização durante a execução do algoritmo genético:
- ✅ Vê a evolução ao vivo
- ✅ Gráficos de convergência em tempo real
- ✅ Controles interativos (pausar, screenshot)
- ✅ Ideal para debugging e tuning

```bash
python src/main.py --optimize --pygame
```

### 🗺️ 2. Folium - Mapas Interativos

Mapas reais após otimização:
- ✅ Pontos de entrega coloridos por prioridade
- ✅ Rotas traçadas por veículo (cores distintas)
- ✅ Popups com informações detalhadas
- ✅ Exporta HTML para compartilhar
- ✅ Ideal para relatórios e apresentações

```bash
python src/main.py --optimize --map
```

### 🔄 Híbrido (Recomendado)

Use ambos! Pygame durante desenvolvimento, Folium para resultado final:

```bash
python src/main.py --optimize --pygame --map
```

Consulte [VISUALIZACAO_GUIA.md](VISUALIZACAO_GUIA.md) para detalhes completos.

---

## 🧪 Testes

```bash
# Executar todos os testes
pytest tests/

# Executar com cobertura
pytest --cov=src tests/

# Executar teste específico
pytest tests/test_genetic_algorithm.py
```

---

## 📈 Benchmark e Comparativos

O sistema inclui comparações com:
- ✅ Algoritmo guloso (Nearest Neighbor)
- ✅ Força bruta (instâncias pequenas)
- ✅ Savings Algorithm (Clarke-Wright)
- ✅ Google OR-Tools (opcional)

---

## 🔧 Configuração Avançada

### Parâmetros do Algoritmo Genético

Editar em `config/config.json`:

```json
{
  "genetic_algorithm": {
    "population_size": 100,
    "generations": 500,
    "mutation_rate": 0.3,
    "crossover_rate": 0.8,
    "elitism_rate": 0.1,
    "tournament_size": 5
  },
  "constraints": {
    "vehicle_capacity": 100,
    "vehicle_autonomy": 50,
    "priorities": ["critico", "alto", "medio", "baixo"]
  },
  "llm": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "sua-api-key-aqui",
    "temperature": 0.7
  }
}
```

---

## 📚 Documentação Adicional

- [Arquitetura do Sistema](docs/arquitetura.md)
- [Algoritmo Genético Detalhado](docs/algoritmo_genetico.md)
- [Relatório Técnico Completo](docs/relatorio_tecnico.md)

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto é parte do Tech Challenge IADT - Fase 2.

---

## 👥 Autores

- [Seu Nome] - Desenvolvimento inicial

---

## 🙏 Agradecimentos

- Código base TSP fornecido pela IADT
- Bibliotecas open-source utilizadas
- Comunidade Python

---

## 📞 Contato

Para dúvidas ou sugestões, abra uma issue no repositório.

---

**Status do Projeto**: 🚧 Em Desenvolvimento

Última atualização: Outubro 2025

