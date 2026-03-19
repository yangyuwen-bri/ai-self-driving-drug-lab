from __future__ import annotations

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
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(7, 22, 30, 0.98), rgba(8, 27, 38, 0.98));
            border-right: 1px solid var(--line);
        }
        .hero-card, .panel-card, .flow-card, .stat-card {
            background: linear-gradient(180deg, var(--panel), var(--panel-strong));
            border: 1px solid var(--line);
            border-radius: 22px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.18);
        }
        .hero-card {
            padding: 1.5rem 1.6rem;
            margin-bottom: 1rem;
        }
        .panel-card {
            padding: 1.15rem 1.2rem;
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
            max-width: 60rem;
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
        max_rounds = st.slider("最大实验轮次", 3, 20, 8)
        initial_random_samples = st.slider("冷启动探索轮次", 3, 12, 6)
        target_mode = st.radio("任务模式", ["multi", "single"], index=0, horizontal=True)
        strategy = st.selectbox("优化引擎", ["baybe", "surrogate"])
        st.markdown("### 多目标权重")
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
