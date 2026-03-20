from __future__ import annotations

import streamlit as st

from app.frontend.shared_ui import (
    build_front_lab_sidebar,
    configure_page,
    get_last_summary,
    get_service,
    inject_theme,
    render_metric_box,
    render_svg_line_chart,
    set_last_summary,
    summary_to_rounds_dataframe,
)


configure_page("前台实验室")


def main() -> None:
    inject_theme()
    service = get_service()
    request, execute = build_front_lab_sidebar()

    if execute:
        set_last_summary(service.run_closed_loop(request))

    summary = get_last_summary()
    rounds_df = summary_to_rounds_dataframe(summary)

    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">Front Lab</div>
            <h1 class="hero-title">前台实验室</h1>
            <p class="hero-copy">输入目标半衰期，系统自动推荐实验处方并完成一轮虚拟闭环优化。</p>
            <div class="hero-actions">
                <span class="chip">目标 Y</span>
                <span class="chip">最佳处方 X</span>
                <span class="chip">实验结果 Y</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 1], gap="large")
    with left:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("#### 当前任务")
        if summary is None:
            st.info("还没有运行结果。请在左侧设置目标并点击“启动虚拟实验闭环”。")
        else:
            metric_cols = st.columns(3)
            with metric_cols[0]:
                render_metric_box("目标值", f"{request.desired_half_life:.1f} h")
            with metric_cols[1]:
                render_metric_box("最佳 half_life", f"{summary.best_result.half_life:.2f} h")
            with metric_cols[2]:
                render_metric_box("目标误差", f"{summary.best_result.target_error:.3f}")

            metric_cols = st.columns(3)
            with metric_cols[0]:
                render_metric_box("实验轮次", str(len(summary.rounds)))
            with metric_cols[1]:
                render_metric_box("运行状态", summary.status)
            with metric_cols[2]:
                render_metric_box("优化策略", summary.strategy_used)

            st.markdown("##### 推荐的最佳实验处方 X")
            st.json(summary.best_parameters.model_dump())

            st.markdown("##### 当前最佳实验结果 Y")
            st.json(summary.best_result.model_dump())
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("#### 本次设置")
        render_metric_box("允许误差", f"{request.tolerance:.2f}")
        render_metric_box("任务模式", request.target_mode)
        render_metric_box("优化引擎", request.strategy)
        st.markdown('<p class="muted-copy">更多参数已折叠到左侧“高级设置”，前台页只保留演示所需的核心信息。</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("#### 闭环轨迹")
    if rounds_df.empty:
        st.info("运行完成后，这里会显示每轮实验的收敛过程。")
    else:
        chart_cols = st.columns(2, gap="large")
        with chart_cols[0]:
            render_svg_line_chart(
                "half_life 收敛轨迹",
                rounds_df.set_index("round")[["half_life"]],
                ["half_life"],
                colors=["#7ae7ff"],
                height=320,
            )
        with chart_cols[1]:
            render_svg_line_chart(
                "目标误差",
                rounds_df.set_index("round")[["target_error"]],
                ["target_error"],
                colors=["#ff9478"],
                height=320,
            )

        st.dataframe(
            rounds_df[
                [
                    "round",
                    "temperature",
                    "humidity",
                    "aux1_ratio",
                    "aux2_ratio",
                    "duration",
                    "stirring_speed",
                    "pH",
                    "solvent_concentration",
                    "half_life",
                    "target_error",
                    "is_best",
                ]
            ],
            use_container_width=True,
            height=280,
        )
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
