from __future__ import annotations

import streamlit as st

from app.frontend.shared_ui import (
    build_front_lab_sidebar,
    configure_page,
    get_last_summary,
    get_service,
    inject_theme,
    render_card,
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
            <p class="hero-copy">设定目标，自动生成配方，执行虚拟实验。</p>
            <span class="chip">输入目标 Y</span>
            <span class="chip">系统生成 X</span>
            <span class="chip">自动跑虚拟实验</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    flow_col_1, flow_col_2, flow_col_3, flow_col_4 = st.columns(4)
    with flow_col_1:
        render_card("1. 设定目标 Y", "例如目标半衰期 12 小时，并设置允许误差和最大轮次。")
    with flow_col_2:
        render_card("2. 生成实验处方 X", "BayBE 根据已有数据推荐温度、湿度、辅料比例和工艺参数。")
    with flow_col_3:
        render_card("3. 执行虚拟实验", "数字孪生模拟器返回本轮实验观测值 Y，模拟未来真实实验输出。")
    with flow_col_4:
        render_card("4. 自动闭环优化", "系统根据误差继续调参，直到结果接近目标 Y。")

    left, right = st.columns([1.05, 1], gap="large")
    with left:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("#### 当前任务看板")
        if summary is None:
            st.info("还没有运行结果。请在左侧设置目标并点击“启动虚拟实验闭环”。")
        else:
            metric_cols = st.columns(3)
            with metric_cols[0]:
                render_metric_box("Run ID", summary.run_id)
            with metric_cols[1]:
                render_metric_box("状态", summary.status)
            with metric_cols[2]:
                render_metric_box("策略", summary.strategy_used)

            metric_cols = st.columns(3)
            with metric_cols[0]:
                render_metric_box("最佳 half_life", f"{summary.best_result.half_life:.2f} h")
            with metric_cols[1]:
                render_metric_box("目标误差", f"{summary.best_result.target_error:.3f}")
            with metric_cols[2]:
                render_metric_box("实验轮次", str(len(summary.rounds)))

            st.markdown("##### 推荐的最佳实验处方 X")
            st.json(summary.best_parameters.model_dump())

            st.markdown("##### 当前最佳实验结果 Y")
            st.json(summary.best_result.model_dump())
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("#### 运行状态")
        st.json(
            {
                "mode": "simulation-first",
                "optimizer": request.strategy,
                "target_mode": request.target_mode,
                "tolerance": request.tolerance,
            }
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("#### 闭环轨迹")
    if rounds_df.empty:
        st.info("运行完成后，这里会显示每轮实验的收敛过程。")
    else:
        chart_cols = st.columns([1.2, 1], gap="large")
        with chart_cols[0]:
            render_svg_line_chart(
                "实验结果轨迹",
                rounds_df.set_index("round")[["half_life", "stability_index", "solubility"]],
                ["half_life", "stability_index", "solubility"],
                colors=["#7ae7ff", "#7effb2", "#ffd36f"],
                height=320,
            )
        with chart_cols[1]:
            render_svg_line_chart(
                "误差与评分",
                rounds_df.set_index("round")[["target_error", "desirability"]],
                ["target_error", "desirability"],
                colors=["#ff9478", "#7ae7ff"],
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
                    "stability_index",
                    "solubility",
                    "target_error",
                    "desirability",
                    "is_best",
                ]
            ],
            use_container_width=True,
            height=320,
        )
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
