# Changelog

## 2026-04-07

### Documentacao - clareza para entendimento e apresentacao
- Adicionado `TL;DR` com proposta de valor e resultado esperado em 30 segundos.
- Adicionadas secoes "Para Quem Este Projeto", "Fluxo do Sistema" e "Roteiro de Apresentacao (5-7 minutos)" no `README.md`.
- Corrigido link de clone para o repositorio real.
- Adicionada orientacao de execucao minima sem LLM.
- Adicionadas secoes de limitacoes conhecidas e troubleshooting rapido.
- Ajustado texto de status para refletir estado real do projeto (funcional com melhorias incrementais).

### Produto - chat conversacional e adaptacao de tela
- Implementado streaming de respostas no Q&A com Ollama em `src/llm_integration/qa_system.py` (`ask_stream` e sessao interativa com fluxo em tempo real).
- Adicionado `chat_realtime.py` para conversar com a ultima simulacao sem rerodar o AG.
- Integrado `main.py` para salvar contexto da simulacao em `outputs/session/latest_context.json`.
- Integrado `main.py` para abrir sessao de chat imediatamente ao final da simulacao, com contexto carregado automaticamente.
- Ajustada deteccao de resolucao do monitor e uso de janela adaptativa/resizable no `main.py`.
- Ajustado `PygameVisualizer` para layout dinamico por resolucao e suporte a resize de janela.

### UX Web Viewer - Phase 1 e Phase 2
- Criado `web_viewer/app_streamlit.py` como painel web para demonstracao no navegador.
- Criado `web_viewer/theme.css` com tema visual consistente (tokens de cor, tipografia, espacamento e componentes).
- Reforcada hierarquia visual com hero, KPI cards e navegacao priorizando mapa.
- Padronizados estados de vazio/erro com orientacao de acao.
- Refinadas tabs, tabela, inputs e botoes para maior consistencia e leitura.

### UX Web Viewer - Phase 3 (polish)
- Adicionadas microinteracoes visuais (hover/fade) para feedback de interface.
- Adicionados placeholders de carregamento (skeleton) para mapa e relatorio.
- Melhorada apresentacao do chat com bolhas distintas de usuario e assistente.

### UX Web Viewer - Design QA final
- Adicionados estilos de foco para navegacao por teclado e acessibilidade.
- Adicionado suporte a `prefers-reduced-motion`.
- Ajustado alinhamento de mensagens de chat (usuario a direita, assistente a esquerda).
- Adicionados documentos-base de arquitetura de design e produto (`DESIGN_SYSTEM.md`, `FRONTEND_GUIDELINES.md`, `APP_FLOW.md`, `PRD.md`, `TECH_STACK.md`).

### Web Viewer - modo "igual Pygame" no navegador
- Criada aba `Ao vivo` para executar o algoritmo genetico em tempo real no Streamlit.
- Adicionados controles de simulacao (veiculos, pontos e geracoes).
- Adicionados progresso de execucao, grafico de convergencia (melhor/medio) e tabela de rotas por geracao.
- Adicionado mapa final embutido com a melhor geracao ao termino da simulacao.
