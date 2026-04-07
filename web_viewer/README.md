# Web Viewer (Teste no navegador)

Este diretório contém um protótipo para apresentar o projeto no navegador, com:
- KPI da última execução
- tabela de rotas
- mapa Folium embutido
- relatório Markdown
- chat simples com Llama (Ollama)

## 1) Pré-requisitos

- já ter rodado uma simulação (`python main.py`) para gerar:
  - `outputs/session/latest_context.json`
  - `outputs/maps/*.html`
  - `outputs/reports/*.md`
- opcional para chat:
  - `ollama serve`
  - `ollama pull llama2`

## 2) Instalação mínima

No ambiente virtual do projeto:

```bash
pip install -r web_viewer/requirements.txt
```

## 3) Executar o viewer

```bash
streamlit run web_viewer/app_streamlit.py
```

## 4) O que validar no teste

1. Aba `Visao geral`: KPI + tabela de rotas.
2. Aba `Mapa`: mapa HTML carregando sem erro.
3. Aba `Relatorio`: markdown renderizado corretamente.
4. Aba `Chat`: ativar toggle e enviar 2-3 perguntas.

## 5) Próximos passos sugeridos

- trocar chat para streaming visual por token (UX de "tempo real" mais natural);
- adicionar filtros por prioridade/veículo no mapa;
- adicionar botão "baixar relatório PDF";
- transformar este protótipo em front oficial (com login e histórico).
