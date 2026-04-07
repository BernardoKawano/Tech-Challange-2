# APP_FLOW

## Fluxo principal do viewer web

1. Carregar `outputs/session/latest_context.json`.
2. Exibir hero com resumo da simulacao.
3. Exibir KPI cards.
4. Navegar por abas:
   - `Mapa`: renderiza ultimo mapa HTML.
   - `Visao geral`: tabela de rotas + expander detalhado.
   - `Relatorio`: renderiza ultimo markdown de relatorio.
   - `Chat`: conversa com contexto da simulacao.

## Fluxo de fallback
- Sem contexto: status card com acao `python main.py`.
- Sem mapa: status card com acao `python test_folium.py`.
- Sem relatorio: status card com acao `python main.py`.
- Sem Ollama: status card com acao de instalacao/inicializacao.
