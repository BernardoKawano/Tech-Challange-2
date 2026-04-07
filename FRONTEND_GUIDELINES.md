# FRONTEND_GUIDELINES

## Escopo
Este documento cobre apenas o front do `web_viewer`.

## Estrutura
- `web_viewer/app_streamlit.py`: layout e composicao de blocos.
- `web_viewer/theme.css`: tokens e estilo visual.

## Convencoes
- Separar funcoes de render por bloco (`hero`, `kpi`, `mapa`, `relatorio`, `chat`).
- Evitar logica de negocio no front.
- Estados vazios/erro devem usar `render_status_card`.
- Evitar texto tecnico em UX quando existir acao recomendada.

## Acessibilidade
- Manter foco visivel para teclado.
- Preservar contraste de texto e componentes.
- Respeitar `prefers-reduced-motion`.

## Responsividade
- Mobile first para densidade de componentes.
- Grid fluido para KPI.
- Evitar alturas fixas em novos blocos (exceto embeds externos como mapa).
