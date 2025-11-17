# 🏥 Sistema de Otimização de Rotas para Distribuição de Suprimentos Médicos

<div align="center">

**Tech Challenge #2 - FIAP**

Sistema inteligente de otimização de rotas usando **Algoritmos Genéticos** + **LLM** + **Visualizações Interativas**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.5+-green.svg)](https://www.pygame.org/)
[![Folium](https://img.shields.io/badge/Folium-0.14+-orange.svg)](https://python-visualization.github.io/folium/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[🎥 Demonstração em Vídeo](#-demonstração) | [📖 Documentação](#-documentação) | [🚀 Começar](#-início-rápido)

</div>

---

## 🎥 Demonstração

> **Vídeo de apresentação do projeto:**

📺 **[ASSISTA NO YOUTUBE](https://youtu.be/kWew_1jsQjQ)** ➡️ https://youtu.be/kWew_1jsQjQ

<div align="center">

*Veja o sistema em ação: visualização em tempo real, mapas interativos e geração automática de instruções!*

</div>

---

## 📋 Sobre o Projeto

Este sistema resolve o **Vehicle Routing Problem (VRP)** aplicado à distribuição de suprimentos médicos em São Paulo, considerando:

- ✅ **Prioridades** (CRÍTICO, ALTO, MÉDIO, BAIXO)
- ✅ **Múltiplos veículos** com diferentes capacidades e autonomias
- ✅ **Restrições realistas** (capacidade, autonomia, tempo de serviço)
- ✅ **Visualização em tempo real** (Pygame)
- ✅ **Mapas interativos** (Folium/HTML)
- ✅ **Geração automática** de instruções e relatórios (LLM/Ollama)

### 🎯 Problema Resolvido

**Cenário:** Hospitais e centros médicos de São Paulo precisam receber suprimentos urgentes. Como otimizar as rotas para:
- Minimizar distância total
- Priorizar entregas críticas
- Respeitar limites de carga e autonomia
- Balancear carga entre veículos

**Solução:** Algoritmo Genético que evolui soluções até encontrar as rotas ótimas!

---

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.8+
- 8GB RAM (para LLM local)
- Windows/Linux/Mac

### 🔧 Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/seu-usuario/Tech-Challenge-2.git
cd Tech-Challenge-2

# 2. Criar ambiente virtual
python -m venv .venv

# 3. Ativar ambiente virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Instalar dependências
pip install -r requirements.txt
```

### 🤖 Configurar LLM (Ollama - Gratuito!)

```bash
# 1. Baixar Ollama
# Windows: https://ollama.ai/download/windows
# Linux/Mac: curl -fsSL https://ollama.com/install.sh | sh

# 2. Baixar modelo (demora ~15-30 min, só uma vez!)
ollama pull llama2

# 3. Iniciar servidor (deixar rodando!)
ollama serve
```

### ▶️ Executar

```bash
# Executar o sistema completo!
python main.py
```

**O que acontece:**
1. 🎮 Menu interativo (Pygame) para escolher parâmetros
2. 🧬 Algoritmo Genético otimiza as rotas
3. 🗺️ Gera mapa HTML interativo
4. 🤖 LLM cria instruções para motoristas
5. 📊 LLM gera relatório gerencial

**Resultados salvos em:**
- `outputs/maps/` - Mapas HTML (abrir no navegador!)
- `outputs/instructions/` - Instruções por veículo (.txt)
- `outputs/reports/` - Relatórios de eficiência (.md)
- `logs/genetic/` - Logs do algoritmo (.json)

---

## 📁 Estrutura do Projeto

```
Tech-Challenge-2/
│
├── main.py                       ⭐ SCRIPT PRINCIPAL
├── test_folium.py                   Teste do visualizador Folium
├── test_qa_system.py                Teste do sistema Q&A
│
├── src/                             Código fonte
│   ├── models/                      Modelos de dados
│   │   ├── delivery_point.py        • Ponto de entrega
│   │   ├── vehicle.py               • Veículo
│   │   └── route.py                 • Rota
│   │
│   ├── genetic_algorithm/           Algoritmo Genético
│   │   ├── chromosome.py            • Cromossomo (solução)
│   │   ├── fitness.py               • Função fitness
│   │   ├── operators.py             • Operadores (crossover, mutação)
│   │   ├── ga_engine.py             • Motor do AG
│   │   └── logger.py                • Logger
│   │
│   ├── visualization/               Visualizações
│   │   ├── pygame_visualizer.py     • Visualização tempo real
│   │   └── folium_visualizer.py     • Mapas HTML interativos
│   │
│   ├── llm_integration/             Integração LLM
│   │   ├── instruction_generator.py • Gera instruções
│   │   ├── report_generator.py      • Gera relatórios
│   │   └── qa_system.py             • Sistema Q&A
│   │
│   ├── utils/                       Utilitários
│   │   └── distance_calculator.py   • Cálculo de distâncias
│   │
│   └── constraints/                 Restrições
│       └── __init__.py              • Módulo de restrições
│
├── data/                            Dados
│   ├── sample_delivery_points.json  15 pontos reais em SP
│   └── sample_vehicles.json         5 tipos de veículos
│
├── config/                          Configurações
│   └── config.example.json          Exemplo de configuração
│
├── outputs/                         Saídas geradas ⭐
│   ├── maps/                        • Mapas HTML (exemplos incluídos)
│   ├── instructions/                • Instruções .txt
│   └── reports/                     • Relatórios .md
│
├── logs/                            Logs ⭐
│   └── genetic/                     • Logs do AG (*.json incluídos)
│
├── requirements.txt                 Dependências
├── README.md                        Documentação principal ⭐
└── .gitignore                       Git ignore
```

---

## 🧬 Algoritmo Genético

### Representação

**Cromossomo:** Lista de rotas (uma por veículo)
```python
Cromossomo = [
    [1, 5, 7, 3],      # Rota do Veículo 1: B → F → H → D
    [0, 2, 6],         # Rota do Veículo 2: A → C → G
    [4, 8, 9]          # Rota do Veículo 3: E → I → J
]
```

### Operadores

| Operador | Taxa | Descrição |
|----------|------|-----------|
| **Seleção** | - | Torneio (k=5) com elitismo (10%) |
| **Crossover** | 80% | PMX (Partially Mapped Crossover) adaptado |
| **Mutação SWAP** | 12% | Troca 2 pontos dentro de uma rota |
| **Mutação MOVE** | 12% | Move ponto entre veículos |
| **Mutação INVERSION** | 6% | Inverte segmento de rota |

### Função Fitness (Multi-Objetivo)

```python
fitness = distância_total 
        + 3.0 × penalidade_prioridades
        + 0.5 × penalidade_balanceamento
        + 1000.0 × violação_capacidade
        + 10000.0 × violação_autonomia
```

**Objetivo:** Minimizar fitness (quanto menor, melhor!)

### Parâmetros

- **População:** 100 indivíduos
- **Gerações:** 50-2000 (configurável)
- **Elitismo:** 10% melhores preservados
- **Parada:** Número fixo de gerações

---

## 🎮 Visualizações

### 1. Pygame - Tempo Real

Durante a otimização:
- 🗺️ Mapa com rotas evoluindo
- 📈 Gráfico de convergência
- 📊 Métricas ao vivo
- 🔍 Filtros por veículo
- 📉 Estatísticas do AG

**Controles:**
- `ESC` - Fechar
- `Clique` - Filtrar por veículo

### 2. Folium - Mapas HTML

Após otimização:
- 🗺️ Mapa real do OpenStreetMap
- 📍 Pontos coloridos por prioridade
- 🛣️ Rotas com setas animadas
- 💬 Popups com detalhes
- 🔍 Zoom, pan, fullscreen
- 📤 Compartilhável (HTML standalone)

**Exemplo:** `outputs/maps/rotas_otimizadas_3v_15p_500g.html`

---

## 🤖 Integração LLM

### Tecnologia: Ollama + Llama2

**Por quê Ollama?**
- ✅ 100% gratuito
- ✅ Roda localmente (privacidade!)
- ✅ Não precisa de API key
- ✅ Offline

### Funcionalidades

#### 1. Instruções para Motoristas

Gerado automaticamente para cada veículo:

```
INSTRUÇÕES DE ENTREGA - Van Refrigerada 01
=========================================

Veículo: Van Refrigerada 01
Capacidade: 150 kg / 1.5 m³
Autonomia: 200 km
Tipo: Van Refrigerada

Rota Total: 4 entregas | 30.46 km | ~45 min

SEQUÊNCIA DE ENTREGAS:
1. Hospital São Paulo (CRÍTICO)
   - Endereço: Av. Paulista, 123
   - Carga: 15.0 kg | 0.3 m³
   - Prioridade: CRÍTICO ⚠️
   - Tempo serviço: 10 min

[... mais entregas ...]
```

**Arquivo:** `outputs/instructions/instrucoes_Van_Refrigerada_01_3v_15p.txt`

#### 2. Relatórios Gerenciais

Análise completa da otimização:

```markdown
# RELATÓRIO DE EFICIÊNCIA - ROTAS OTIMIZADAS

## Resumo Executivo
- Veículos: 3
- Entregas: 15
- Distância total: 68.88 km
- Eficiência: 92%

## Análise por Veículo
...

## Sugestões de Melhoria
...
```

**Arquivo:** `outputs/reports/relatorio_3v_15p_500g_[timestamp].md`

---

## 🎨 Recursos Destacados

### ✨ Diferenciais

1. **Labeling Inteligente**
   - A-Z para primeiros 26 pontos
   - A1-Z1 para próximos 26
   - Suporta até 100 pontos!

2. **Menu Interativo Full HD**
   - Seleção de veículos (1-5)
   - Slider de pontos (1-100)
   - Slider de gerações (50-2000)
   - Visualização de características

3. **Filtros por Veículo**
   - Ver todas as rotas
   - Filtrar por veículo individual
   - Botões interativos

4. **Estatísticas Completas**
   - Crossovers realizados
   - Mutações por tipo
   - Fitness ao longo do tempo
   - Violações de restrições

5. **Dados Reais**
   - 15 hospitais/centros médicos em SP
   - Coordenadas aproximadas reais
   - Prioridades realistas

---

## 📖 Documentação

### Guias Principais

Todas as informações necessárias estão consolidadas neste README.

### Dados de Entrada

#### Pontos de Entrega (15 em SP)

Arquivo: `data/sample_delivery_points.json`

Incluem hospitais e centros médicos como:
- Hospital das Clínicas (CRÍTICO)
- Hospital Sírio-Libanês (ALTO)
- Hospital Albert Einstein (ALTO)
- UBS Vila Mariana (MÉDIO)
- ... e mais!

#### Veículos (5 tipos)

Arquivo: `data/sample_vehicles.json`

| Veículo | Capacidade | Autonomia | Tipo |
|---------|------------|-----------|------|
| Van Refrigerada 01 | 150 kg | 200 km | Refrigerada |
| Van Padrão 02 | 180 kg | 250 km | Padrão |
| Caminhonete 03 | 250 kg | 300 km | Carga |
| Van Grande 04 | 300 kg | 250 km | Grande |
| Utilitário 05 | 120 kg | 350 km | Compacto |

---

## ⚙️ Configurações

### Parâmetros Padrão

```python
# Algoritmo Genético
POPULATION_SIZE = 100
GENERATIONS = 500 (configurável no menu)
MUTATION_RATE = 0.30
CROSSOVER_RATE = 0.80
ELITISM_RATE = 0.10
TOURNAMENT_SIZE = 5

# Visualização
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# LLM
PROVIDER = "ollama"
MODEL = "llama2"
TEMPERATURE = 0.7
```

---

## 🧪 Testes

### Teste Rápido do Folium

```bash
python test_folium.py
```

Gera mapa de teste em: `outputs/maps/teste_rotas_exemplo.html`

### Execução Completa

```bash
# Configuração recomendada para teste:
# - 3 veículos
# - 10 pontos
# - 300 gerações
# Tempo: ~5-8 minutos
python main.py
```

---

## 📊 Resultados Esperados

### Métricas Típicas

Para 3 veículos e 15 pontos:

| Métrica | Valor Típico |
|---------|--------------|
| Distância total | 50-150 km |
| Fitness final | 80-150 |
| Convergência | 100-300 gerações |
| Tempo AG | 5-10 min |
| Tempo LLM | 3-5 min |
| Utilização capacidade | 20-80% |
| Violações | 0 |

### Arquivos Gerados

```
outputs/
├── maps/
│   └── rotas_otimizadas_3v_15p_500g.html          (~50KB)
├── instructions/
│   ├── instrucoes_Van_Refrigerada_01_3v_15p.txt   (~2KB)
│   ├── instrucoes_Van_Padrao_02_3v_15p.txt
│   └── instrucoes_Caminhonete_03_3v_15p.txt
└── reports/
    └── relatorio_3v_15p_500g_20251015_153045.md   (~5KB)
```

---

## 🛠️ Tecnologias

### Core

- **Python 3.8+** - Linguagem principal
- **NumPy** - Cálculos numéricos
- **Pygame** - Visualização tempo real
- **Folium** - Mapas HTML interativos
- **Matplotlib** - Gráficos

### LLM

- **Ollama** - Servidor LLM local
- **Llama2** - Modelo de linguagem (7B)

### Outras

- **Pathlib** - Manipulação de caminhos
- **JSON** - Serialização de dados
- **Dataclasses** - Estruturas de dados

---

## 📈 Complexidade do Projeto

### Estatísticas

- **Linhas de código:** ~2.000
- **Módulos:** 10+
- **Classes:** 15+
- **Funções:** 100+
- **Arquivos:** 20+ (código fonte)
- **Documentação:** 1.500+ linhas

### Conceitos Aplicados

- ✅ Algoritmos Genéticos
- ✅ Programação Orientada a Objetos
- ✅ Inteligência Artificial (LLM)
- ✅ Visualização de Dados
- ✅ Otimização Combinatória
- ✅ Interface Gráfica
- ✅ Processamento de Linguagem Natural

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto é parte do **Tech Challenge #2 - FIAP** e foi desenvolvido para fins educacionais.

---

## 👥 Autores

- **[Seu Nome]** - Desenvolvimento completo

### Contribuições

- Algoritmo Genético: Implementação customizada
- Visualizações: Pygame e Folium integrados
- LLM: Integração com Ollama
- Dados: Coletados e validados
- Documentação: Completa e detalhada

---

## 🙏 Agradecimentos

- **FIAP** - Tech Challenge e orientação
- **Comunidade Python** - Bibliotecas open-source
- **Ollama Team** - LLM local gratuito
- **OpenStreetMap** - Mapas
---

## 🎓 Contexto Acadêmico

**Instituição:** FIAP  
**Curso:** IA para Desenvolvedores
**Disciplina:** Tech Challenge #2  
**Data:** Outubro 2025

---

<div align="center">

### ⭐ Se este projeto foi útil, deixe uma estrela! ⭐

**Status:** ✅ 100% Completo e Funcional

Última atualização: Outubro 2025

</div>

---

<div align="center">

**Desenvolvido com ❤️ para o Tech Challenge #2**

[⬆ Voltar ao topo](#-sistema-de-otimização-de-rotas-para-distribuição-de-suprimentos-médicos)

</div>
