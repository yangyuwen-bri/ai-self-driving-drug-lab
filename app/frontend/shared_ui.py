from __future__ import annotations

import html
import pandas as pd
import streamlit as st

from app.backend.core.config import load_fixed_components
from app.backend.models.schemas import ExperimentParameters, ExperimentRecord, ExperimentResult, ObjectiveWeights, SDLRunSummary
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
        [data-baseweb="select"] > div {
            background: rgba(7, 18, 27, 0.96) !important;
            border-color: rgba(106, 227, 255, 0.18) !important;
            color: var(--text) !important;
        }
        [data-baseweb="select"] * {
            color: var(--text) !important;
            fill: var(--text) !important;
        }
        div[role="listbox"] {
            background: rgba(7, 18, 27, 0.98) !important;
            border: 1px solid rgba(106, 227, 255, 0.18) !important;
        }
        div[role="option"] {
            background: transparent !important;
            color: var(--text) !important;
        }
        div[role="option"][aria-selected="true"] {
            background: rgba(122, 231, 255, 0.12) !important;
        }
        [data-testid="stAlert"] {
            background: rgba(12, 42, 67, 0.62) !important;
            border: 1px solid rgba(106, 227, 255, 0.16) !important;
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
        .control-card {
            background: linear-gradient(180deg, rgba(9, 24, 34, 0.9), rgba(9, 24, 34, 0.98));
            border: 1px solid rgba(106, 227, 255, 0.18);
            border-radius: 22px;
            padding: 1.15rem 1.15rem 1rem 1.15rem;
            margin-bottom: 1rem;
        }
        .page-head {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1.25rem;
            padding: 1rem 0 0.85rem 0;
            margin-bottom: 0.4rem;
            border-bottom: 1px solid rgba(106, 227, 255, 0.12);
        }
        .page-head h1 {
            margin: 0.12rem 0 0 0;
            font-size: 2rem;
            line-height: 1.05;
            color: var(--text);
        }
        .page-head-copy {
            margin: 0.42rem 0 0 0;
            max-width: 42rem;
            color: var(--muted);
            font-size: 0.98rem;
            line-height: 1.55;
        }
        .page-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            justify-content: flex-end;
        }
        .page-tag {
            display: inline-flex;
            align-items: center;
            padding: 0.42rem 0.78rem;
            border-radius: 999px;
            border: 1px solid rgba(106, 227, 255, 0.18);
            background: rgba(122, 231, 255, 0.06);
            color: var(--text);
            font-size: 0.84rem;
        }
        .status-banner {
            padding: 0.95rem 1rem;
            border-radius: 18px;
            margin-bottom: 1rem;
            border: 1px solid rgba(106, 227, 255, 0.18);
            background: rgba(122, 231, 255, 0.08);
        }
        .status-banner.success {
            border-color: rgba(126, 255, 178, 0.28);
            background: rgba(126, 255, 178, 0.09);
        }
        .status-banner.warn {
            border-color: rgba(255, 211, 111, 0.28);
            background: rgba(255, 211, 111, 0.09);
        }
        .status-title {
            margin: 0 0 0.2rem 0;
            font-size: 1rem;
            font-weight: 700;
            color: var(--text);
        }
        .status-copy {
            margin: 0;
            color: var(--text);
            font-size: 0.98rem;
            line-height: 1.5;
        }
        .section-title {
            margin: 0 0 0.8rem 0;
            font-size: 1.35rem;
            color: var(--text);
        }
        .section-copy {
            margin: -0.2rem 0 1rem 0;
            color: var(--muted);
            font-size: 0.95rem;
        }
        .console-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin-bottom: 0.9rem;
        }
        .console-title {
            margin: 0;
            font-size: 1.5rem;
            color: var(--text);
        }
        .console-copy {
            margin: 0.35rem 0 0 0;
            color: var(--muted);
            font-size: 0.95rem;
        }
        .console-meta {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            justify-content: flex-end;
        }
        .data-block {
            background: linear-gradient(180deg, rgba(6, 16, 24, 0.88), rgba(7, 18, 27, 0.96));
            border: 1px solid rgba(106, 227, 255, 0.14);
            border-radius: 20px;
            padding: 1rem 1rem 0.2rem 1rem;
            height: 100%;
        }
        .stack-list {
            display: flex;
            flex-direction: column;
            gap: 0.8rem;
        }
        .run-card, .round-card {
            background: linear-gradient(180deg, rgba(8, 19, 28, 0.96), rgba(7, 18, 27, 0.98));
            border: 1px solid rgba(106, 227, 255, 0.14);
            border-radius: 18px;
            padding: 0.95rem 1rem;
        }
        .run-card.selected, .round-card.selected {
            border-color: rgba(122, 231, 255, 0.34);
            box-shadow: 0 0 0 1px rgba(122, 231, 255, 0.12) inset;
        }
        .row-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.55rem;
        }
        .row-title {
            font-size: 1rem;
            font-weight: 700;
            color: var(--text);
            word-break: break-word;
        }
        .row-copy {
            margin: 0.2rem 0 0 0;
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.45;
        }
        .badge {
            display: inline-flex;
            align-items: center;
            padding: 0.24rem 0.52rem;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            border: 1px solid rgba(106, 227, 255, 0.16);
            color: var(--text);
            background: rgba(122, 231, 255, 0.08);
            white-space: nowrap;
        }
        .badge.success {
            border-color: rgba(126, 255, 178, 0.24);
            background: rgba(126, 255, 178, 0.10);
        }
        .badge.warn {
            border-color: rgba(255, 211, 111, 0.24);
            background: rgba(255, 211, 111, 0.10);
        }
        .mini-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.65rem 0.85rem;
            margin-top: 0.75rem;
        }
        .mini-grid.three {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }
        .mini-item-label {
            color: var(--muted);
            font-size: 0.74rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.18rem;
        }
        .mini-item-value {
            color: var(--text);
            font-size: 0.98rem;
            font-weight: 700;
            word-break: break-word;
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
        details[data-testid="stExpander"] {
            border: 1px solid rgba(106, 227, 255, 0.18);
            border-radius: 18px;
            background: rgba(122, 231, 255, 0.04);
        }
        details[data-testid="stExpander"] summary {
            color: var(--text) !important;
        }
        details[data-testid="stExpander"] summary p,
        details[data-testid="stExpander"] summary span,
        details[data-testid="stExpander"] summary svg {
            color: var(--text) !important;
            fill: var(--text) !important;
        }
        div[data-testid="stSlider"] {
            padding-top: 0.2rem;
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


def render_status_banner(title: str, body: str, tone: str = "default") -> None:
    tone_class = {
        "success": "success",
        "warn": "warn",
    }.get(tone, "")
    st.markdown(
        f"""
        <div class="status-banner {tone_class}">
            <div class="status-title">{html.escape(title)}</div>
            <p class="status-copy">{html.escape(body)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_head(title: str, body: str, tags: list[str] | None = None) -> None:
    tags_markup = ""
    if tags:
        tags_markup = "".join(f'<span class="page-tag">{html.escape(tag)}</span>' for tag in tags)
    st.markdown(
        f"""
        <div class="page-head">
            <div>
                <div class="eyebrow">Virtual Self-Driving Drug Lab</div>
                <h1>{html.escape(title)}</h1>
                <p class="page-head-copy">{html.escape(body)}</p>
            </div>
            <div class="page-meta">{tags_markup}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_grid(items: list[tuple[str, str]], columns: int = 3) -> None:
    if not items:
        return
    for start in range(0, len(items), columns):
        cols = st.columns(columns)
        chunk = items[start : start + columns]
        for index, col in enumerate(cols):
            if index >= len(chunk):
                continue
            with col:
                render_metric_box(chunk[index][0], chunk[index][1])


def humanize_strategy(strategy: str) -> str:
    return strategy.replace("_", " ").replace("->", " -> ").strip()


def summarize_strategy(strategy: str) -> str:
    normalized = strategy.replace(" ", "")
    mapping = {
        "baybe_random->baybe_botorch": "BayBE 随机探索 -> BoTorch",
        "random_bootstrap->surrogate_random_forest": "随机探索 -> 随机森林",
        "surrogate_random_forest": "随机森林代理",
        "baybe": "BayBE",
        "surrogate": "随机森林代理",
    }
    return mapping.get(normalized, humanize_strategy(strategy))


def count_completed_runs(runs_df: pd.DataFrame) -> int:
    if runs_df.empty or "status" not in runs_df.columns:
        return 0
    return int((runs_df["status"].astype(str) == "completed").sum())


def render_run_cards(runs_df: pd.DataFrame, selected_run_id: str | None, limit: int = 6) -> None:
    if runs_df.empty:
        st.info("暂无历史 runs。")
        return
    rows = list(runs_df.head(limit).iterrows())
    for start in range(0, len(rows), 2):
        cols = st.columns(2, gap="large")
        chunk = rows[start : start + 2]
        for col, (_, row) in zip(cols, chunk):
            status = str(row["status"])
            badge_class = "success" if status == "completed" else "warn"
            is_selected = selected_run_id == str(row["run_id"])
            selected_class = " selected" if is_selected else ""
            target_mode = str(row["target_mode"]) if "target_mode" in runs_df.columns else "legacy"
            finished_at = str(row["finished_at"])[:19] if "finished_at" in runs_df.columns else "-"
            strategy = summarize_strategy(str(row["strategy_used"]))
            with col:
                st.markdown(
                    f"""
                    <div class="run-card{selected_class}">
                        <div class="row-top">
                            <div class="row-title">{html.escape(str(row["run_id"]))}</div>
                            <span class="badge {badge_class}">{html.escape(status)}</span>
                        </div>
                        <p class="row-copy">目标 {float(row["desired_half_life"]):.1f} h · 容差 {float(row["tolerance"]):.2f}</p>
                        <div class="mini-grid">
                            <div><div class="mini-item-label">策略路径</div><div class="mini-item-value">{html.escape(strategy)}</div></div>
                            <div><div class="mini-item-label">Current View</div><div class="mini-item-value">{"当前诊断对象" if is_selected else "历史记录"}</div></div>
                            <div><div class="mini-item-label">Finished</div><div class="mini-item-value">{html.escape(finished_at)}</div></div>
                            <div><div class="mini-item-label">Run Mode</div><div class="mini-item-value">{html.escape(target_mode)}</div></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    if len(runs_df) > limit:
        st.markdown(f'<p class="muted-copy">当前显示最近 {limit} 条 run。完整选择列表保留在左侧。</p>', unsafe_allow_html=True)


def render_round_cards(records_df: pd.DataFrame) -> None:
    if records_df.empty:
        st.info("暂无轮次明细。")
        return
    best_error_index = records_df["target_error"].astype(float).idxmin()
    rows = list(records_df.iterrows())
    for start in range(0, len(rows), 2):
        cols = st.columns(2, gap="large")
        chunk = rows[start : start + 2]
        for col, (row_index, row) in zip(cols, chunk):
            badge_class = "success" if row_index == best_error_index else ""
            selected_class = " selected" if row_index == best_error_index else ""
            with col:
                st.markdown(
                    f"""
                    <div class="round-card{selected_class}">
                        <div class="row-top">
                            <div class="row-title">第 {int(row["round"])} 轮</div>
                            <span class="badge {badge_class}">{"最佳轮次" if row_index == best_error_index else "轮次记录"}</span>
                        </div>
                        <p class="row-copy">{html.escape(str(row["created_at"]))[:19]}</p>
                        <div class="mini-grid three">
                            <div><div class="mini-item-label">half_life</div><div class="mini-item-value">{float(row["half_life"]):.2f} h</div></div>
                            <div><div class="mini-item-label">target error</div><div class="mini-item-value">{float(row["target_error"]):.3f}</div></div>
                            <div><div class="mini-item-label">desirability</div><div class="mini-item-value">{float(row["desirability"]):.3f}</div></div>
                            <div><div class="mini-item-label">stability</div><div class="mini-item-value">{float(row["stability_index"]):.2f}</div></div>
                            <div><div class="mini-item-label">solubility</div><div class="mini-item-value">{float(row["solubility"]):.2f}</div></div>
                            <div><div class="mini-item-label">yield</div><div class="mini-item-value">{float(row["yield_percent"]):.1f}%</div></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def parameter_display_items(parameters: ExperimentParameters) -> list[tuple[str, str]]:
    return [
        ("温度", f"{parameters.temperature:.1f} °C"),
        ("湿度", f"{parameters.humidity:.1f} %"),
        ("辅料 A 比", f"{parameters.aux1_ratio:.2f}"),
        ("辅料 B 比", f"{parameters.aux2_ratio:.2f}"),
        ("时长", f"{parameters.duration:.1f} min"),
        ("搅拌速度", f"{parameters.stirring_speed:.0f} rpm"),
        ("pH", f"{parameters.pH:.2f}"),
        ("溶剂浓度", f"{parameters.solvent_concentration:.1f} %"),
    ]


def result_display_items(result: ExperimentResult) -> list[tuple[str, str]]:
    return [
        ("half_life", f"{result.half_life:.2f} h"),
        ("目标误差", f"{result.target_error:.3f}"),
        ("稳定性", f"{result.stability_index:.2f}"),
        ("溶解度", f"{result.solubility:.2f}"),
        ("溶出速率", f"{result.dissolution_rate:.3f}"),
        ("收率", f"{result.yield_percent:.1f} %"),
        ("综合评分", f"{result.desirability:.3f}"),
        ("数据来源", "虚拟实验" if result.source == "simulation" else "真实实验"),
    ]


def build_front_lab_request_inputs(strategy: str, target_mode: str) -> tuple[float, float, bool]:
    st.markdown('<div class="control-card">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="console-top">
            <div>
                <div class="eyebrow">Front Lab Console</div>
                <h2 class="console-title">实验发起台</h2>
                <p class="console-copy">设置本次实验目标并启动执行。历史轨迹和诊断统一放在后台观测室。</p>
            </div>
            <div class="console-meta">
                <span class="page-tag">Simulation</span>
                <span class="page-tag">{html.escape(strategy)}</span>
                <span class="page-tag">{html.escape(target_mode)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    control_cols = st.columns([1.2, 1, 1], gap="large")
    with control_cols[0]:
        desired_half_life = st.slider("目标半衰期 Y（小时）", 4.0, 24.0, 12.0, 0.1)
    with control_cols[1]:
        tolerance = st.slider("允许误差", 0.1, 2.0, 0.5, 0.05)
    with control_cols[2]:
        st.markdown('<div style="height: 1.6rem;"></div>', unsafe_allow_html=True)
        execute = st.button("启动虚拟实验", use_container_width=True, type="primary")
    with st.expander("高级实验设置（可选）", expanded=False):
        settings_cols = st.columns(2, gap="large")
        with settings_cols[0]:
            max_rounds = st.slider("最大实验轮次", 3, 20, 8)
            initial_random_samples = st.slider("冷启动探索轮次", 3, 12, 6)
            target_mode = st.radio("任务模式", ["multi", "single"], index=0 if target_mode == "multi" else 1, horizontal=True)
            strategy = st.selectbox("优化引擎", ["baybe", "surrogate"], index=0 if strategy == "baybe" else 1)
        with settings_cols[1]:
            st.markdown("#### 多目标权重")
            half_life_weight = st.slider("half_life", 0.0, 1.0, 0.6, 0.05)
            stability_weight = st.slider("stability", 0.0, 1.0, 0.3, 0.05)
            solubility_weight = st.slider("solubility", 0.0, 1.0, 0.1, 0.05)
    st.markdown("</div>", unsafe_allow_html=True)
    st.session_state["front_lab_advanced"] = {
        "max_rounds": max_rounds,
        "initial_random_samples": initial_random_samples,
        "target_mode": target_mode,
        "strategy": strategy,
        "weights": ObjectiveWeights(
            half_life=half_life_weight,
            stability_index=stability_weight,
            solubility=solubility_weight,
        ),
    }
    return desired_half_life, tolerance, execute


def get_front_lab_advanced_settings() -> dict:
    default = {
        "max_rounds": 8,
        "initial_random_samples": 6,
        "target_mode": "multi",
        "strategy": "baybe",
        "weights": ObjectiveWeights(
            half_life=0.6,
            stability_index=0.3,
            solubility=0.1,
        ),
    }
    return st.session_state.get("front_lab_advanced", default)


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
