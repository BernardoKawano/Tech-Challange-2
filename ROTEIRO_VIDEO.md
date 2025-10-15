# 🎬 ROTEIRO PARA GRAVAÇÃO DO VÍDEO
## Tech Challenge #2 - Sistema de Otimização de Rotas com AG e LLM

---

## ⏱️ TEMPO ESTIMADO: 10-15 MINUTOS

---

## 📋 PREPARAÇÃO ANTES DE GRAVAR

### ✅ Checklist Pré-Gravação
- [ ] Ollama rodando (`ollama serve` em janela separada)
- [ ] Ambiente virtual ativado (`.venv\Scripts\activate`)
- [ ] Navegador pronto para abrir HTML
- [ ] Editor de texto pronto para mostrar arquivos gerados
- [ ] OBS/Gravador configurado
- [ ] Microfone testado
- [ ] Fecha outras janelas/programas

---

## 🎯 ESTRUTURA DO VÍDEO (10-15 MIN)

### **1. INTRODUÇÃO (1-2 min)**

**Fale:**
> "Olá! Sou [seu nome] e vou apresentar o Tech Challenge #2: Sistema de Otimização de Rotas para Distribuição de Suprimentos Médicos usando Algoritmos Genéticos e LLMs."

**Mostre na tela:**
- README.md aberto
- Estrutura do projeto (explorador de arquivos)

**Explique rapidamente:**
- Problema: Otimizar rotas de entrega com múltiplos veículos
- Solução: Algoritmo Genético + Visualizações + LLM
- Tecnologias: Python, Pygame, Folium, Ollama

---

### **2. ESTRUTURA DO CÓDIGO (2-3 min)**

**Mostre os principais módulos:**

**A. Models** (`src/models/`)
```
Mostre: delivery_point.py
Fale: "Aqui temos o modelo de ponto de entrega com prioridades: CRÍTICO, ALTO, MÉDIO, BAIXO"
```

**B. Genetic Algorithm** (`src/genetic_algorithm/`)
```
Mostre: ga_engine.py, fitness.py, operators.py
Fale: "O algoritmo genético implementa seleção por torneio, crossover PMX e mutações SWAP/MOVE/INVERSION"
```

**C. Visualizations** (`src/visualization/`)
```
Mostre: pygame_visualizer.py, folium_visualizer.py
Fale: "Duas visualizações: Pygame para tempo real e Folium para mapas interativos HTML"
```

**D. LLM Integration** (`src/llm_integration/`)
```
Mostre: instruction_generator.py, report_generator.py
Fale: "Integração com Ollama para gerar instruções e relatórios automaticamente"
```

---

### **3. DADOS DE ENTRADA (1 min)**

**Mostre:** `data/sample_delivery_points.json`

**Fale:**
> "Temos 15 pontos de entrega reais em São Paulo, incluindo hospitais e centros médicos, com diferentes prioridades e cargas."

**Mostre:** `data/sample_vehicles.json`

**Fale:**
> "E 5 veículos com diferentes capacidades e autonomias: vans refrigeradas, vans padrão e caminhonetes."

---

### **4. DEMONSTRAÇÃO PRÁTICA (5-7 min) ⭐ PRINCIPAL**

**Execute:** `python teste_ag_interativo.py`

#### **4.1. Menu Interativo (30 seg)**
```
Mostre: Tela de seleção no Pygame
Fale: "O sistema permite escolher parâmetros interativamente:"
```

**Selecione:**
- Veículos: 3
- Pontos: 10
- Gerações: 500

#### **4.2. Evolução do Algoritmo Genético (2-3 min)**
```
Mostre: Visualização em tempo real
Fale: "Aqui vemos a evolução do algoritmo em tempo real:
       - Mapa com rotas sendo otimizadas
       - Gráfico de convergência
       - Métricas de fitness
       - Estatísticas de mutações e crossovers"
```

**Destaque:**
- Cores diferentes para cada veículo
- Pontos marcados com letras (A, B, C...)
- Filtros interativos por veículo
- Legendas explicativas

**DICA:** Pause o vídeo ou acelere se demorar muito!

#### **4.3. Resultados Finais (1 min)**
```
Mostre: Tela final do Pygame com solução ótima
Fale: "Ao final, temos:
       - Rotas otimizadas para cada veículo
       - Distâncias totais
       - Utilização de capacidade
       - Verificação de autonomia"
```

---

### **5. MAPA HTML INTERATIVO (1-2 min)**

**Abra:** `outputs/maps/rotas_otimizadas_3v_10p_500g.html`

**Mostre:**
- Mapa interativo com zoom
- Pontos com popups (clique neles!)
- Rotas coloridas com setas animadas
- Legenda interativa
- Mini-mapa no canto

**Fale:**
> "O sistema gera um mapa HTML interativo com Folium, que pode ser compartilhado com a equipe de logística. Clicando nos pontos, vemos detalhes de cada entrega."

---

### **6. INSTRUÇÕES GERADAS POR LLM (1-2 min)**

**Abra:** `outputs/instructions/instrucoes_Van_Refrigerada_01_3v_10p.txt`

**Mostre o conteúdo e leia trechos:**

**Fale:**
> "O sistema usa Ollama com o modelo Llama2 para gerar instruções detalhadas para cada motorista, incluindo:"
> - Pontos de entrega em ordem
> - Endereços e prioridades
> - Estimativas de tempo
> - Dicas de navegação

**Mostre:** Arquivo de outra van para comparar

---

### **7. RELATÓRIO DE EFICIÊNCIA (1 min)**

**Abra:** `outputs/reports/relatorio_*.md`

**Mostre:**
- Análise geral de eficiência
- Estatísticas do algoritmo genético
- Sugestões de melhoria

**Fale:**
> "O LLM também gera um relatório analítico que pode ser usado pela gerência para tomada de decisões."

---

### **8. CÓDIGO-FONTE DETALHADO (1-2 min) - OPCIONAL**

**Se tiver tempo, mostre rapidamente:**

**A. Função de Fitness** (`src/genetic_algorithm/fitness.py`)
```python
# Mostre a função calculate_fitness
Fale: "A função de fitness considera múltiplos critérios:
       - Distância total
       - Prioridades
       - Equilíbrio de carga
       - Violações de capacidade/autonomia"
```

**B. Operadores Genéticos** (`src/genetic_algorithm/operators.py`)
```python
# Mostre crossover_pmx e mutate_swap
Fale: "Implementamos operadores clássicos adaptados para VRP"
```

**C. Integração LLM** (`src/llm_integration/instruction_generator.py`)
```python
# Mostre a função generate_instructions
Fale: "A integração com Ollama usa templates de prompt estruturados"
```

---

### **9. TESTES E VALIDAÇÃO (30 seg) - OPCIONAL**

**Mostre no terminal:**
```bash
python test_folium.py
```

**Fale:**
> "O projeto inclui scripts de teste para validar cada componente isoladamente."

---

### **10. CONCLUSÃO (1 min)**

**Fale:**
> "Em resumo, desenvolvemos um sistema completo que:"
> 
> ✅ Otimiza rotas usando Algoritmos Genéticos
> ✅ Visualiza resultados em tempo real (Pygame)
> ✅ Gera mapas interativos (Folium)
> ✅ Cria instruções automáticas (LLM/Ollama)
> ✅ Produz relatórios gerenciais (LLM/Ollama)
> ✅ Respeita restrições reais (capacidade, autonomia, prioridades)
> 
> "O código está no GitHub [mostre link] e está pronto para uso em produção com dados reais."
> 
> "Obrigado!"

---

## 🎨 DICAS DE APRESENTAÇÃO

### ✅ O QUE FAZER:
- Fale de forma clara e pausada
- Explique o QUE está mostrando E POR QUÊ é importante
- Use exemplos práticos ("Se um hospital precisa de suprimentos urgentes...")
- Mostre entusiasmo! É um projeto completo!
- Se errar, não pare: continue naturalmente

### ❌ O QUE EVITAR:
- Não leia código linha por linha (apenas explique conceitos)
- Não fique em silêncio por muito tempo
- Não acelere demais (deixe tempo para absorver)
- Não se desculpe por erros pequenos

---

## 📝 SCRIPT RÁPIDO (SE PRECISAR DE ALGO DECORADO)

### Introdução (versão curta):
> "Olá! Vou apresentar um sistema de otimização de rotas para distribuição de suprimentos médicos. O sistema usa algoritmos genéticos para encontrar as melhores rotas, visualizações interativas para acompanhamento, e inteligência artificial (LLM) para gerar instruções automáticas. Vamos ver como funciona!"

### Explicação do AG:
> "O algoritmo genético funciona como a evolução natural: criamos uma população de soluções, selecionamos as melhores, fazemos cruzamento e mutações, e repetimos até encontrar a solução ótima. Aqui vocês veem esse processo acontecendo em tempo real."

### Explicação do LLM:
> "Usamos o Ollama, que é um LLM local e gratuito, para gerar automaticamente instruções detalhadas para os motoristas e relatórios analíticos para a gerência. Isso economiza horas de trabalho manual."

---

## ⚙️ CONFIGURAÇÕES RECOMENDADAS PARA DEMONSTRAÇÃO

### Para demonstração rápida (5-8 min total):
```
Veículos: 3
Pontos: 10
Gerações: 200-300
```

### Para demonstração completa (10-15 min total):
```
Veículos: 3
Pontos: 15
Gerações: 500
```

### Para demonstração impressionante (mas demora!):
```
Veículos: 5
Pontos: 20-30
Gerações: 1000
```

**DICA:** Você pode gravar duas vezes:
1. Uma vez com poucos pontos para ser rápido
2. Depois acelere o vídeo na edição para mostrar evolução completa

---

## 🎬 EDIÇÃO POSTERIOR (OPCIONAL)

Se quiser editar o vídeo depois:
- Adicione texto na tela com pontos-chave
- Acelere partes longas (evolução do AG)
- Adicione música de fundo suave
- Coloque seu nome/logo
- Adicione marcadores de tempo (capítulos)

---

## 📊 MÉTRICAS PARA MENCIONAR

Durante a apresentação, destaque números:
- "15 pontos de entrega reais em São Paulo"
- "5 tipos de veículos com diferentes capacidades"
- "Algoritmo testa 500 gerações em ~5 minutos"
- "Sistema gera instruções automáticas em 30-60 segundos"
- "Mapa HTML interativo com todas as rotas"

---

## 🚨 TROUBLESHOOTING DURANTE GRAVAÇÃO

**Se o Pygame demorar muito:**
- Reduza gerações para 200
- Use menos pontos (8-10)
- Ou grave e acelere na edição

**Se o LLM demorar muito:**
- Mencione: "Aguardando LLM processar..." (normal!)
- Ou edite depois para cortar espera

**Se algo der erro:**
- Pare, corrija, e recomece (edita depois)
- Ou continue e mencione: "Como podem ver no código, isso seria resolvido por..."

---

## ✅ CHECKLIST PÓS-GRAVAÇÃO

Antes de finalizar, verifique se mostrou:
- [ ] Código-fonte (estrutura)
- [ ] Dados de entrada (JSON)
- [ ] Visualização Pygame (tempo real)
- [ ] Mapa Folium (HTML interativo)
- [ ] Instruções LLM (arquivo txt)
- [ ] Relatório LLM (arquivo md)
- [ ] Explicação do algoritmo genético
- [ ] Explicação da integração LLM

---

## 🎯 OBJETIVO FINAL

Ao final do vídeo, quem assistir deve entender:
1. **O QUE** o sistema faz (otimiza rotas médicas)
2. **COMO** funciona (AG + Pygame + Folium + LLM)
3. **POR QUÊ** é útil (economiza tempo, otimiza recursos)
4. **QUALIDADE** do código (bem estruturado, documentado, funcional)

---

**BOA GRAVAÇÃO! 🎬 VOCÊ CONSEGUE! 🚀**

---

## 📎 ANEXOS

### Link do GitHub (prepare antes):
```
github.com/[seu-usuario]/Tech-Challenge-2
```

### Tecnologias usadas (para mencionar):
- Python 3.x
- Pygame (visualização tempo real)
- Folium (mapas interativos)
- Ollama + Llama2 (LLM local)
- Algoritmos Genéticos (otimização)

### Complexidade do projeto (para impressionar):
- ~2.000 linhas de código
- 10+ módulos organizados
- 15 pontos reais em SP
- 5 tipos de veículos
- 3 tipos de visualização
- 2 tipos de relatório automatizado

---

**ÚLTIMA DICA:** Pratique uma vez antes de gravar! Faz muita diferença! 🎯

