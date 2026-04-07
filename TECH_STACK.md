# TECH_STACK

## Frontend
- Streamlit (Python)
- CSS custom via injecao em `st.markdown`

## Dados de entrada do viewer
- `outputs/session/latest_context.json`
- `outputs/maps/*.html`
- `outputs/reports/*.md`

## Chat
- `src.llm_integration.QASystem`
- Ollama local (`llama2`)

## Limitacoes tecnicas
- Streamlit tem limites para controle fino de DOM.
- Mapa Folium e embed HTML (altura fixa controlada por parametro do componente).
- Streaming token-a-token no chat web ainda usa fluxo simples de resposta final no viewer.
