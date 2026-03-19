from __future__ import annotations

import streamlit as st

from app.frontend.shared_ui import (
    configure_page,
    get_last_summary,
    get_store,
    inject_theme,
    render_card,
    render_metric_box,
)


configure_page("虚拟药物实验室总览")


def main() -> None:
    inject_theme()
    store = get_store()
    runs = store.list_runs()
    latest_summary = get_last_summary()

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="eyebrow">Virtual Self-Driving Drug Lab</div>
            <h1 class="hero-title">虚拟实验室演示总览</h1>
            <p class="hero-copy">面向药物配方研发的自驱动实验演示平台。</p>
            <span class="chip">前后台分视图</span>
            <span class="chip">当前记录 {len(runs)} 次 runs</span>
            <span class="chip">默认策略 BayBE</span>
            <span class="chip">为真实实验接入做准备</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    intro_left, intro_right = st.columns([1.1, 1], gap="large")
    with intro_left:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("#### 模块入口")
        cols = st.columns(3)
        with cols[0]:
            render_card("前台实验室", "目标设定、处方生成、虚拟实验。")
        with cols[1]:
            render_card("后台观测室", "run 历史、误差收敛、结果诊断。")
        with cols[2]:
            render_card("接入路线", "真实实验室、真实数据、系统对接。")
        st.markdown("</div>", unsafe_allow_html=True)

    with intro_right:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("#### 平台状态")
        cols = st.columns(3)
        with cols[0]:
            render_metric_box("累计 runs", str(len(runs)))
        with cols[1]:
            render_metric_box("当前模式", "Simulation")
        with cols[2]:
            render_metric_box("最近 run", "-" if latest_summary is None else latest_summary.run_id)
        st.json(
            {
                "execution_mode": "simulation-first",
                "current_data_source": "virtual lab simulator",
                "future_data_source": "robot measurements / LIMS / ELN",
            }
        )
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
