from __future__ import annotations

import html
import pandas as pd
import streamlit as st

from app.backend.core.config import load_fixed_components
from app.backend.models.schemas import ExperimentParameters, ExperimentRecord, SDLRequest, SDLRunSummary
from app.backend.services.sdl_service import SDLService
from app.backend.storage.sqlite_store import SQLiteExperimentStore


def configure_page(page_title: str, page_icon: str = "🧪") -> None:
    st.set_page_config(
        page_title=page_title,
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon=page_icon,
    )


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #06121a;
            --panel: rgba(9, 24, 34, 0.84);
            --panel-strong: rgba(9, 24, 34, 0.96);
            --line: rgba(106, 227, 255, 0.18);
            --accent: #7ae7ff;
            --accent-2: #ffd36f;
            --accent-3: #7effb2;
            --text: #eff8fb;
            --muted: #95b3be;
        }
        .stApp {
            background:
                radial-gradient(circle at 10% 20%, rgba(122,231,255,0.12), transparent 28%),
                radial-gradient(circle at 85% 15%, rgba(126,255,178,0.10), transparent 25%),
                linear-gradient(180deg, #041018 0%, #071923 100%);
            color: var(--text);
        }
        [data-testid="stHeader"] {
            background: transparent;
            height: 0;
        }
        [data-testid="stToolbar"] {
            right: 1rem;
            top: 0.75rem;
        }
        [data-testid="stDecoration"] {
            display: none;
        }
        [data-testid="stStatusWidget"] {
            display: none;
        }
        [data-testid="stSidebarNav"] {
            padding-top: 1rem;
        }
        [data-testid="stSidebarNav"] > div:first-child {
            display: none;
        }
        .block-container {
            padding-top: 1.25rem !important;
            padding-bottom: 2rem !important;
            max-width: 1480px !important;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(7, 22, 30, 0.98), rgba(8, 27, 38, 0.98));
            border-right: 1px solid var(--line);
        }
        [data-testid="stSidebarNav"] a {
            color: rgba(239, 248, 251, 0.72);
        }
        [data-testid="stSidebarNav"] a:hover,
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            color: var(--text);
            background: rgba(122, 231, 255, 0.08);
        }
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: var(--text);
        }
        .hero-card, .panel-card, .flow-card, .stat-card {
            background: linear-gradient(180deg, var(--panel), var(--panel-strong));
            border: 1px solid var(--line);
            border-radius: 22px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.18);
        }
        .hero-card {
            padding: 1.5rem 1.6rem 1.3rem 1.6rem;
            margin-bottom: 1rem;
        }
        .panel-card {
            padding: 1.15rem 1.2rem;
        }
        [data-testid="stJson"] > div,
        [data-testid="stCodeBlock"] > div,
        .stDataFrame {
            border-radius: 18px;
            overflow: hidden;
        }
        [data-testid="stJson"] pre,
        [data-testid="stCodeBlock"] pre {
            background: rgba(7, 18, 27, 0.96) !important;
            color: var(--text) !important;
        }
        .flow-card, .stat-card {
            padding: 0.95rem 1rem;
        }
        .eyebrow {
            color: var(--accent);
            font-size: 0.78rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            font-weight: 700;
            margin-bottom: 0.45rem;
        }
        .hero-title {
            margin: 0;
            font-size: 2.1rem;
            line-height: 1.05;
        }
        .hero-copy {
            color: var(--muted);
            margin: 0.65rem 0 1rem 0;
            max-width: 44rem;
        }
        .hero-actions {
            display: flex;
            gap: 0.7rem;
            flex-wrap: wrap;
            margin-top: 0.95rem;
        }
        .hero-actions.tight {
            margin-top: 0.8rem;
        }
        .chip {
            display: inline-block;
            margin-right: 0.55rem;
            margin-bottom: 0.45rem;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            border: 1px solid var(--line);
            background: rgba(122, 231, 255, 0.08);
            color: var(--text);
            font-size: 0.88rem;
        }
        .callout {
            padding: 0.9rem 1rem;
            border-radius: 18px;
            border: 1px solid rgba(255, 211, 111, 0.25);
            background: rgba(255, 211, 111, 0.08);
            color: var(--text);
            margin-top: 0.8rem;
        }
        .mini-label {
            font-size: 0.76rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 0.35rem;
        }
        .mini-value {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--text);
            word-break: break-word;
        }
        .step-title {
            margin: 0 0 0.2rem 0;
            font-size: 1rem;
            color: var(--text);
        }
        .step-copy {
            margin: 0;
            color: var(--muted);
            font-size: 0.92rem;
        }
        .muted-copy {
            color: var(--muted);
            font-size: 0.95rem;
            margin: 0;
        }
        .nav-card {
            background: linear-gradient(180deg, rgba(9, 24, 34, 0.84), rgba(9, 24, 34, 0.96));
            border: 1px solid rgba(106, 227, 255, 0.18);
            border-radius: 22px;
            padding: 1.15rem 1.15rem 1rem 1.15rem;
            min-height: 180px;
        }
        .nav-title {
            margin: 0 0 0.45rem 0;
            color: var(--text);
            font-size: 1.1rem;
            font-weight: 700;
        }
        .nav-copy {
            margin: 0;
            color: var(--muted);
            font-size: 0.98rem;
            line-height: 1.6;
        }
        div[data-testid="stButton"] > button {
            border-radius: 999px;
            border: 1px solid rgba(106, 227, 255, 0.22);
            background: rgba(122, 231, 255, 0.08);
            color: var(--text);
            font-weight: 700;
            min-height: 2.75rem;
        }
        div[data-testid="stButton"] > button:hover {
            border-color: rgba(122, 231, 255, 0.42);
            color: var(--text);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_service() -> SDLService:
    return SDLService()


def get_store() -> SQLiteExperimentStore:
    return SQLiteExperimentStore()


def ensure_session_state() -> None:
    if "last_summary" not in st.session_state:
        st.session_state["last_summary"] = None


def get_last_summary() -> SDLRunSummary | None:
    ensure_session_state()
    return st.session_state["last_summary"]


def set_last_summary(summary: SDLRunSummary) -> None:
    ensure_session_state()
    st.session_state["last_summary"] = summary


def runs_to_dataframe(rows: list) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([dict(row) for row in rows])


def summary_to_rounds_dataframe(summary: SDLRunSummary | None) -> pd.DataFrame:
    if summary is None:
        return pd.DataFrame()
    return pd.DataFrame(
        [
            {
                "round": item.round_index,
                **item.parameters.model_dump(),
                **item.result.model_dump(),
                "is_best": item.is_best,
            }
            for item in summary.rounds
        ]
    )


def records_to_dataframe(records: list[ExperimentRecord]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(
        [
            {
                "round": item.round_index,
                "created_at": item.created_at.isoformat(),
                **item.parameters.model_dump(),
                **item.result.model_dump(),
            }
            for item in records
        ]
    )


def render_card(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="flow-card">
            <div class="step-title">{title}</div>
            <p class="step-copy">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_box(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="mini-label">{label}</div>
            <div class="mini-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_svg_line_chart(
    title: str,
    dataframe: pd.DataFrame,
    columns: list[str],
    colors: list[str] | None = None,
    height: int = 280,
) -> None:
    if dataframe.empty or not columns:
        st.info("暂无图表数据。")
        return

    chart_df = dataframe[columns].astype(float)
    width = 720
    padding_left = 46
    padding_right = 18
    padding_top = 20
    padding_bottom = 34
    inner_width = width - padding_left - padding_right
    inner_height = height - padding_top - padding_bottom

    x_values = list(range(len(chart_df.index)))
    all_values = [float(value) for column in columns for value in chart_df[column].tolist()]
    min_y = min(all_values)
    max_y = max(all_values)
    if min_y == max_y:
        min_y -= 1.0
        max_y += 1.0

    if colors is None:
        colors = ["#7ae7ff", "#7effb2", "#ffd36f", "#ff9478"]

    def x_coord(position: int) -> float:
        if len(x_values) == 1:
            return padding_left + inner_width / 2
        return padding_left + inner_width * position / max(len(x_values) - 1, 1)

    def y_coord(value: float) -> float:
        ratio = (value - min_y) / (max_y - min_y)
        return padding_top + inner_height * (1.0 - ratio)

    line_markup: list[str] = []
    legend_markup: list[str] = []
    for index, column in enumerate(columns):
        color = colors[index % len(colors)]
        points = " ".join(
            f"{x_coord(position):.1f},{y_coord(float(value)):.1f}"
            for position, value in enumerate(chart_df[column].tolist())
        )
        line_markup.append(
            f'<polyline fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" '
            f'stroke-linejoin="round" points="{points}" />'
        )
        for position, value in enumerate(chart_df[column].tolist()):
            line_markup.append(
                f'<circle cx="{x_coord(position):.1f}" cy="{y_coord(float(value)):.1f}" r="3.5" fill="{color}" />'
            )
        legend_markup.append(
            f'<span style="display:inline-flex;align-items:center;margin-right:14px;color:#eff8fb;font-size:13px;">'
            f'<span style="width:10px;height:10px;border-radius:999px;background:{color};display:inline-block;margin-right:6px;"></span>'
            f'{html.escape(column)}</span>'
        )

    x_axis = (
        f'<line x1="{padding_left}" y1="{padding_top + inner_height}" '
        f'x2="{padding_left + inner_width}" y2="{padding_top + inner_height}" '
        f'stroke="rgba(255,255,255,0.18)" stroke-width="1" />'
    )
    y_axis = (
        f'<line x1="{padding_left}" y1="{padding_top}" x2="{padding_left}" '
        f'y2="{padding_top + inner_height}" stroke="rgba(255,255,255,0.18)" stroke-width="1" />'
    )

    tick_markup: list[str] = []
    for position in range(len(x_values)):
        x = x_coord(position)
        tick_markup.append(
            f'<text x="{x:.1f}" y="{padding_top + inner_height + 22}" text-anchor="middle" '
            f'fill="#95b3be" font-size="12">{position + 1}</text>'
        )

    y_labels = [min_y, (min_y + max_y) / 2, max_y]
    for label in y_labels:
        y = y_coord(label)
        tick_markup.append(
            f'<line x1="{padding_left}" y1="{y:.1f}" x2="{padding_left + inner_width}" y2="{y:.1f}" '
            f'stroke="rgba(255,255,255,0.08)" stroke-width="1" />'
        )
        tick_markup.append(
            f'<text x="{padding_left - 8}" y="{y + 4:.1f}" text-anchor="end" '
            f'fill="#95b3be" font-size="12">{label:.2f}</text>'
        )

    svg = f"""
    <div style="background:linear-gradient(180deg, rgba(9,24,34,0.84), rgba(9,24,34,0.96));
                border:1px solid rgba(106,227,255,0.18); border-radius:18px; padding:14px 14px 8px 14px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <div style="color:#eff8fb;font-size:16px;font-weight:700;">{html.escape(title)}</div>
        <div>{"".join(legend_markup)}</div>
      </div>
      <svg viewBox="0 0 {width} {height}" width="100%" height="{height}" preserveAspectRatio="none">
        {x_axis}
        {y_axis}
        {''.join(tick_markup)}
        {''.join(line_markup)}
      </svg>
    </div>
    """
    st.markdown(svg, unsafe_allow_html=True)


def default_request() -> SDLRequest:
    return SDLRequest(
        desired_half_life=12.0,
        tolerance=0.5,
        max_rounds=8,
        initial_random_samples=6,
        target_mode="multi",
        strategy="baybe",
        weights={
            "half_life": 0.6,
            "stability_index": 0.3,
            "solubility": 0.1,
        },
    )


def build_front_lab_sidebar() -> tuple[SDLRequest, bool]:
    with st.sidebar:
        st.markdown("### 前台实验任务")
        desired_half_life = st.slider("目标半衰期 Y（小时）", 4.0, 24.0, 12.0, 0.1)
        tolerance = st.slider("允许误差", 0.1, 2.0, 0.5, 0.05)
        with st.expander("高级设置"):
            max_rounds = st.slider("最大实验轮次", 3, 20, 8)
            initial_random_samples = st.slider("冷启动探索轮次", 3, 12, 6)
            target_mode = st.radio("任务模式", ["multi", "single"], index=0, horizontal=True)
            strategy = st.selectbox("优化引擎", ["baybe", "surrogate"])
            st.markdown("#### 多目标权重")
            half_life_weight = st.slider("half_life", 0.0, 1.0, 0.6, 0.05)
            stability_weight = st.slider("stability", 0.0, 1.0, 0.3, 0.05)
            solubility_weight = st.slider("solubility", 0.0, 1.0, 0.1, 0.05)
        execute = st.button("启动虚拟实验闭环", use_container_width=True, type="primary")
        st.caption("模式：Simulation")

    request = SDLRequest(
        desired_half_life=desired_half_life,
        tolerance=tolerance,
        max_rounds=max_rounds,
        initial_random_samples=initial_random_samples,
        target_mode=target_mode,
        strategy=strategy,
        weights={
            "half_life": half_life_weight,
            "stability_index": stability_weight,
            "solubility": solubility_weight,
        },
    )
    return request, execute


def integration_payload(summary: SDLRunSummary | None) -> dict:
    service = get_service()
    if summary is not None:
        opentrons_payload = service.opentrons.build_protocol_payload(summary.best_parameters)
    else:
        placeholder = ExperimentParameters(
            temperature=42.0,
            humidity=58.0,
            aux1_ratio=2.0,
            aux2_ratio=1.0,
            duration=180.0,
            stirring_speed=520.0,
            pH=6.2,
            solvent_concentration=20.0,
        )
        opentrons_payload = service.opentrons.build_protocol_payload(placeholder)
        opentrons_payload["status"] = "waiting_for_demo_run"
    return {
        "fixed_components": load_fixed_components(),
        "opentrons": opentrons_payload,
        "chemos": service.chemos.describe(),
    }
