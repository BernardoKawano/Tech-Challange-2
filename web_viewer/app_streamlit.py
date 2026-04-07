"""
Prototipo web para visualizacao do projeto no navegador.

Executar:
    streamlit run web_viewer/app_streamlit.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = ROOT / "outputs"
SESSION_FILE = OUTPUTS_DIR / "session" / "latest_context.json"
MAPS_DIR = OUTPUTS_DIR / "maps"
REPORTS_DIR = OUTPUTS_DIR / "reports"
CSS_FILE = ROOT / "web_viewer" / "theme.css"
DATA_DIR = ROOT / "data"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def inject_theme() -> None:
    if CSS_FILE.exists():
        css = CSS_FILE.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_status_card(title: str, message: str, action_hint: str, level: str = "info") -> None:
    st.markdown(
        f"""
        <div class="status-card status-{level} fade-in">
            <h3>{title}</h3>
            <p>{message}</p>
            <code>{action_hint}</code>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(context: Dict[str, Any]) -> None:
    metrics = context.get("metrics", {})
    routes = context.get("routes", [])
    deliveries = sum(route.get("num_deliveries", 0) for route in routes)
    st.markdown(
        f"""
        <section class="hero fade-in">
            <p class="eyebrow">Otimizacao de rotas medicas</p>
            <h1>Painel da ultima simulacao</h1>
            <p class="subtitle">
                {len(routes)} veiculos • {deliveries} entregas • {metrics.get('total_distance', 0):.2f} km totais
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(context: Dict[str, Any]) -> None:
    metrics = context.get("metrics", {})
    ga_stats = context.get("ga_stats", {})
    routes = context.get("routes", [])
    deliveries = sum(route.get("num_deliveries", 0) for route in routes)
    cards = [
        ("Distancia total", f"{metrics.get('total_distance', 0):.2f} km"),
        ("Fitness final", f"{metrics.get('fitness', 0):.2f}"),
        ("Entregas", str(deliveries)),
        ("Geracoes", str(ga_stats.get("total_generations", "N/A"))),
    ]

    st.markdown('<section class="kpi-grid">', unsafe_allow_html=True)
    for label, value in cards:
        st.markdown(
            f"""
            <article class="kpi-card fade-in">
                <p class="kpi-label">{label}</p>
                <p class="kpi-value">{value}</p>
            </article>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</section>", unsafe_allow_html=True)


def load_sample_entities(num_vehicles: int, num_points: int):
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from src.models import DeliveryPoint, Vehicle

    with (DATA_DIR / "sample_delivery_points.json").open("r", encoding="utf-8") as f:
        points_data = json.load(f)[:num_points]
    with (DATA_DIR / "sample_vehicles.json").open("r", encoding="utf-8") as f:
        vehicles_data = json.load(f)[:num_vehicles]

    points = [DeliveryPoint.from_dict(p) for p in points_data]
    vehicles = [Vehicle.from_dict(v) for v in vehicles_data]
    return points, vehicles


def build_ga_config(num_points: int, num_generations: int) -> Dict[str, Any]:
    population_size = max(50, num_points * 5)
    return {
        "population_size": population_size,
        "num_generations": num_generations,
        "crossover_rate": 0.8,
        "mutation_rate": 0.3,
        "elitism_rate": 0.1,
        "tournament_size": 3,
        "convergence_threshold": 0.0001,
        "max_gens_without_improvement": num_generations,
        "fitness_weights": {
            "distance": 1.0,
            "capacity": 1000.0,
            "autonomy": 1000.0,
            "priority": 5.0,
            "balance": 2.0,
            "num_vehicles": 3.0,
        },
        "mutation_types": ["swap", "inversion", "move"],
        "mutation_weights": [0.4, 0.3, 0.3],
        "crossover_type": "order",
        "selection_type": "tournament",
        "enable_logging": False,
    }


def render_live_simulation() -> None:
    st.markdown("### Simulacao ao vivo (estilo Pygame no navegador)")
    st.caption("Evolucao em tempo real: melhores rotas, fitness e progresso por geracao.")

    c1, c2, c3 = st.columns(3)
    with c1:
        num_vehicles = st.slider("Veiculos", min_value=1, max_value=5, value=2, step=1)
    with c2:
        num_points = st.slider("Pontos", min_value=5, max_value=50, value=15, step=1)
    with c3:
        num_generations = st.slider("Geracoes", min_value=50, max_value=1200, value=300, step=50)

    run_now = st.button("Iniciar simulacao ao vivo", type="primary", use_container_width=True)
    if not run_now:
        return

    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from src.genetic_algorithm import GeneticAlgorithm
        from src.visualization.folium_visualizer import FoliumVisualizer
    except Exception as e:
        render_status_card(
            "Dependencias de simulacao indisponiveis",
            f"Nao foi possivel carregar os modulos do AG: {e}",
            "pip install -r requirements.txt",
            level="error",
        )
        return

    progress_bar = st.progress(0)
    status_slot = st.empty()
    chart_slot = st.empty()
    details_slot = st.empty()
    final_map_slot = st.empty()

    try:
        points, vehicles = load_sample_entities(num_vehicles=num_vehicles, num_points=num_points)
        config = build_ga_config(num_points=num_points, num_generations=num_generations)
        depot = (-23.5505, -46.6333)

        ga = GeneticAlgorithm(
            delivery_points=points,
            vehicles=vehicles,
            depot_coord=depot,
            config=config,
        )

        history_rows: List[Dict[str, Any]] = []

        def on_generation(ga_instance, generation, best_chromosome, avg_fitness):
            best_fitness = float(best_chromosome.fitness)
            history_rows.append(
                {
                    "geracao": generation,
                    "melhor_fitness": best_fitness,
                    "fitness_medio": float(avg_fitness),
                }
            )

            pct = min(100, int((generation / max(1, num_generations)) * 100))
            progress_bar.progress(pct)
            status_slot.markdown(
                f"**Geracao {generation}/{num_generations}**  \n"
                f"Melhor fitness: `{best_fitness:.2f}` | Medio: `{float(avg_fitness):.2f}`"
            )

            if len(history_rows) >= 2:
                chart_slot.line_chart(
                    history_rows,
                    x="geracao",
                    y=["melhor_fitness", "fitness_medio"],
                    height=260,
                    use_container_width=True,
                )

            if generation % 5 == 0 or generation == num_generations:
                details = ga_instance.get_best_solution_details()
                routes_data = []
                for route in details.get("routes", []):
                    routes_data.append(
                        {
                            "Veiculo": route.get("vehicle_name", "N/A"),
                            "Entregas": route.get("num_deliveries", 0),
                            "Distancia (km)": round(route.get("distance_km", 0), 2),
                            "Uso cap. (%)": round(route.get("capacity_usage_%", 0), 1),
                            "Rota": " -> ".join(route.get("points", []))[:48],
                        }
                    )
                details_slot.dataframe(routes_data, use_container_width=True, hide_index=True)

        best_solution = ga.run(generation_callback=on_generation)
        progress_bar.progress(100)

        final_details = ga.get_best_solution_details()
        status_slot.success(
            f"Simulacao finalizada. Fitness final: {final_details.get('fitness', 0):.2f} | "
            f"Distancia total: {final_details.get('total_distance_km', 0):.2f} km"
        )

        folium_points = []
        for p in points:
            folium_points.append(
                {
                    "name": p.name,
                    "latitude": p.latitude,
                    "longitude": p.longitude,
                    "priority": p.priority.name,
                    "weight": p.weight_kg,
                    "volume": p.volume_m3,
                    "service_time_min": p.service_time_minutes,
                    "description": getattr(p, "description", p.item_description),
                }
            )

        folium_vehicles = [
            {
                "name": v.name,
                "capacity_kg": v.capacity_kg,
                "capacity_volume_m3": v.capacity_volume_m3,
                "autonomy_km": v.autonomy_km,
            }
            for v in vehicles
        ]

        folium_viz = FoliumVisualizer(center=depot)
        map_obj = folium_viz.create_map(
            delivery_points=folium_points,
            routes=best_solution.get_routes(),
            vehicles=folium_vehicles,
            zoom_start=12,
        )
        with final_map_slot.container():
            st.markdown("#### Mapa final da melhor geracao")
            st.components.v1.html(map_obj.get_root().render(), height=640, scrolling=True)

    except Exception as e:
        render_status_card(
            "Falha durante simulacao ao vivo",
            f"Ocorreu um erro durante a execucao: {e}",
            "Tente menos geracoes/pontos para validar rapidamente",
            level="error",
        )


def render_routes_table(context: Dict[str, Any]) -> None:
    routes = context.get("routes", [])
    if not routes:
        render_status_card(
            "Sem rotas para exibir",
            "Nenhum dado de rota foi encontrado no contexto atual.",
            "python main.py",
            level="warning",
        )
        return

    table_data: List[Dict[str, Any]] = []
    for route in routes:
        full_route = " -> ".join(route.get("points", []))
        truncated_route = full_route if len(full_route) <= 34 else f"{full_route[:34]}..."
        table_data.append(
            {
                "Veiculo": route.get("vehicle_name", "N/A"),
                "Entregas": route.get("num_deliveries", 0),
                "Distancia (km)": round(route.get("distance_km", 0), 2),
                "Uso capacidade (%)": round(route.get("capacity_usage_%", 0), 1),
                "Rota": truncated_route,
            }
        )
    st.dataframe(table_data, use_container_width=True, hide_index=True)

    with st.expander("Ver detalhe completo das rotas"):
        for route in routes:
            full_route = " -> ".join(route.get("points", []))
            st.markdown(f"- **{route.get('vehicle_name', 'N/A')}**: {full_route}")


def render_map_html() -> None:
    latest_map = latest_file(MAPS_DIR, "*.html")
    st.subheader("Mapa interativo")
    if not latest_map:
        render_status_card(
            "Mapa ainda indisponivel",
            "Nao ha arquivos HTML em outputs/maps para renderizar.",
            "python test_folium.py",
            level="warning",
        )
        return

    loading = st.empty()
    loading.markdown('<div class="skeleton skeleton-map"></div>', unsafe_allow_html=True)
    html = latest_map.read_text(encoding="utf-8")
    loading.empty()
    st.caption(f"Fonte de dados: {latest_map.name}")
    st.components.v1.html(html, height=720, scrolling=True)


def render_report_markdown() -> None:
    latest_report = latest_file(REPORTS_DIR, "*.md")
    st.subheader("Relatorio da ultima execucao")
    if not latest_report:
        render_status_card(
            "Relatorio nao encontrado",
            "Nenhum arquivo de relatorio foi gerado na ultima execucao.",
            "python main.py",
            level="warning",
        )
        return

    loading = st.empty()
    loading.markdown(
        '<div class="skeleton skeleton-line"></div><div class="skeleton skeleton-line short"></div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Fonte de dados: {latest_report.name}")
    report_text = latest_report.read_text(encoding="utf-8")
    loading.empty()
    st.markdown(report_text)


def render_chat(context: Dict[str, Any]) -> None:
    st.subheader("Chat com Llama")
    st.caption("Conversa com contexto da simulacao atual.")

    use_chat = st.toggle("Ativar chat com Llama", value=False)
    if not use_chat:
        render_status_card(
            "Chat em espera",
            "Ative o toggle para iniciar a sessao de perguntas.",
            "ollama serve",
            level="info",
        )
        return

    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from src.llm_integration import QASystem
    except Exception as e:
        render_status_card(
            "Erro ao carregar chat",
            f"Nao foi possivel carregar QASystem: {e}",
            "pip install ollama",
            level="error",
        )
        return

    if "qa_system" not in st.session_state:
        try:
            qa = QASystem(provider="ollama", model="llama2")
            qa.load_context(
                routes=context.get("routes", []),
                vehicles=context.get("vehicles", []),
                delivery_points=context.get("delivery_points", []),
                metrics=context.get("metrics", {}),
                ga_stats=context.get("ga_stats", {}),
            )
            st.session_state.qa_system = qa
            st.session_state.chat_messages = []
        except Exception as e:
            render_status_card(
                "Conexao com Ollama falhou",
                f"Erro ao conectar com Ollama: {e}",
                "ollama serve && ollama pull llama2",
                level="error",
            )
            return

    st.markdown('<div class="chat-status fade-in">Status: conectado ao contexto da simulacao</div>', unsafe_allow_html=True)
    question = st.text_input("Pergunta")
    if st.button("Enviar pergunta", type="primary") and question.strip():
        with st.spinner("Consultando Llama..."):
            answer = st.session_state.qa_system.ask(question.strip())
        st.session_state.chat_messages.append({"q": question.strip(), "a": answer})

    for msg in reversed(st.session_state.get("chat_messages", [])):
        st.markdown(
            f"""
            <div class="chat-message user fade-in">
              <div class="chat-row user">
                <p class="chat-label">Voce</p>
                <p class="chat-text">{msg['q']}</p>
              </div>
            </div>
            <div class="chat-message assistant fade-in">
              <div class="chat-row assistant">
                <p class="chat-label">Assistente</p>
                <p class="chat-text">{msg['a']}</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(page_title="VRP Web Viewer", layout="wide")
    inject_theme()

    if not SESSION_FILE.exists():
        render_status_card(
            "Contexto de simulacao ausente",
            "O arquivo outputs/session/latest_context.json nao foi encontrado.",
            "python main.py",
            level="error",
        )
        return

    context = load_json(SESSION_FILE)
    render_hero(context)
    render_kpis(context)

    tab_live, tab_map, tab_overview, tab_report, tab_chat = st.tabs(
        ["Ao vivo", "Mapa", "Visao geral", "Relatorio", "Chat"]
    )

    with tab_live:
        render_live_simulation()
    with tab_map:
        st.markdown("### Mapa da operacao")
        render_map_html()
    with tab_overview:
        st.markdown("### Rotas por veiculo")
        render_routes_table(context)
    with tab_report:
        st.markdown("### Relatorio consolidado")
        render_report_markdown()
    with tab_chat:
        st.markdown("### Conversa operacional")
        render_chat(context)


if __name__ == "__main__":
    main()
