from __future__ import annotations

import streamlit as st

from app.frontend.shared_ui import (
    configure_page,
    get_last_summary,
    inject_theme,
    integration_payload,
    render_card,
)


configure_page("接入路线")


def main() -> None:
    inject_theme()
    latest_summary = get_last_summary()

    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">Integration Roadmap</div>
            <h1 class="hero-title">真实实验室接入路线</h1>
            <p class="hero-copy">从虚拟实验走向真实实验执行与真实数据回流。</p>
            <span class="chip">Simulation-first</span>
            <span class="chip">真实执行待接入</span>
            <span class="chip">数据回流待接入</span>
            <span class="chip">前后台架构已预留</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_left, top_right = st.columns([1.05, 1], gap="large")
    with top_left:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("#### 当前状态")
        st.json(integration_payload(latest_summary))
        st.markdown("</div>", unsafe_allow_html=True)

    with top_right:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("#### 接入后的目标形态")
        cols = st.columns(3)
        with cols[0]:
            render_card("前台实验室", "负责接收任务、执行实验、记录真实操作状态。")
        with cols[1]:
            render_card("后台观测室", "负责接收真实 Y、更新模型、重新推荐 X 并保留完整 run 历史。")
        with cols[2]:
            render_card("知识资产层", "沉淀最优配方、工艺窗口、模型表现和实验报告。")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("#### 后续替换顺序")
    cols = st.columns(4)
    with cols[0]:
        render_card("1. 替换执行层", "把虚拟实验执行替换成 Opentrons 或人工实验工位。")
    with cols[1]:
        render_card("2. 替换观测层", "把模拟返回的 Y 替换成真实测量数据。")
    with cols[2]:
        render_card("3. 增加数据接口", "接入 LIMS、ELN、仪器日志或 ChemOS 编排。")
    with cols[3]:
        render_card("4. 增加后台对比", "扩展模型对比、工艺复用和长期知识沉淀页面。")
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
