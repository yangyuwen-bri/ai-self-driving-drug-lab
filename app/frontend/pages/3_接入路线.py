from __future__ import annotations

import streamlit as st

from app.frontend.shared_ui import (
    configure_page,
    get_last_summary,
    inject_theme,
    integration_payload,
    render_card,
    render_metric_grid,
    render_page_head,
)


configure_page("接入路线")


def main() -> None:
    inject_theme()
    latest_summary = get_last_summary()

    payload = integration_payload(latest_summary)
    render_page_head(
        "真实实验室接入路线",
        "这一页说明当前 demo 已经预留了哪些接口，以及后续如何从虚拟实验过渡到真实执行与真实数据回流。",
        tags=["Simulation-first", "Opentrons", "ChemOS"],
    )

    top_left, top_right = st.columns([1.05, 1], gap="large")
    with top_left:
        st.markdown('<h3 class="section-title">当前接入状态</h3>', unsafe_allow_html=True)
        st.markdown('<p class="section-copy">当前版本还是 simulation-first，但执行层、编排层和固定组分记录都已经有占位。</p>', unsafe_allow_html=True)
        render_metric_grid(
            [
                ("执行层", f"{payload['opentrons']['platform']} / {payload['opentrons']['mode']}"),
                ("编排层", f"{payload['chemos']['platform']} / {payload['chemos']['mode']}"),
                ("固定组分", payload["fixed_components"]["buffer_system"]),
                ("API 比例", f"{payload['fixed_components']['primary_api_ratio']:.1f} %"),
            ],
            columns=2,
        )

    with top_right:
        st.markdown('<h3 class="section-title">接入后的目标形态</h3>', unsafe_allow_html=True)
        st.markdown('<p class="section-copy">系统最终会分成执行、观测和知识沉淀三层，各自承担不同职责。</p>', unsafe_allow_html=True)
        cols = st.columns(3)
        with cols[0]:
            render_card("前台实验室", "负责接收任务、执行实验、记录真实操作状态。")
        with cols[1]:
            render_card("后台观测室", "负责接收真实 Y、更新模型、重新推荐 X 并保留完整 run 历史。")
        with cols[2]:
            render_card("知识资产层", "沉淀最优配方、工艺窗口、模型表现和实验报告。")

    st.markdown('<h3 class="section-title">后续替换顺序</h3>', unsafe_allow_html=True)
    st.markdown('<p class="section-copy">建议按执行层、观测层、数据接口、知识资产四个阶段推进，而不是一次性替换。</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    with cols[0]:
        render_card("1. 替换执行层", "把虚拟实验执行替换成 Opentrons 或人工实验工位。")
    with cols[1]:
        render_card("2. 替换观测层", "把模拟返回的 Y 替换成真实测量数据。")
    with cols[2]:
        render_card("3. 增加数据接口", "接入 LIMS、ELN、仪器日志或 ChemOS 编排。")
    with cols[3]:
        render_card("4. 增加后台对比", "扩展模型对比、工艺复用和长期知识沉淀页面。")


if __name__ == "__main__":
    main()
