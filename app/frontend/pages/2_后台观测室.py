from __future__ import annotations

import streamlit as st

from app.frontend.shared_ui import (
    configure_page,
    get_last_summary,
    get_store,
    inject_theme,
    records_to_dataframe,
    render_metric_box,
    render_svg_line_chart,
    runs_to_dataframe,
)


configure_page("后台观测室")


def main() -> None:
    inject_theme()
    store = get_store()
    runs_df = runs_to_dataframe(store.list_runs())
    latest_summary = get_last_summary()

    with st.sidebar:
        st.markdown("### 后台观测设置")
        if runs_df.empty:
            selected_run_id = None
            st.info("还没有历史 run。先去前台实验室启动一轮虚拟实验。")
        else:
            selected_run_id = st.selectbox("选择一个 run 进行诊断", runs_df["run_id"].tolist(), index=0)

    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">Back Office</div>
            <h1 class="hero-title">后台观测室</h1>
            <p class="hero-copy">集中查看运行历史、误差收敛和结果诊断。</p>
            <span class="chip">历史 run 诊断</span>
            <span class="chip">误差收敛分析</span>
            <span class="chip">数据资产沉淀</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    upper_left, upper_right = st.columns([1.05, 1], gap="large")
    with upper_left:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("#### 运行总览")
        if runs_df.empty:
            st.info("数据库中还没有历史运行记录。")
        else:
            summary_cols = st.columns(3)
            with summary_cols[0]:
                render_metric_box("累计 runs", str(len(runs_df)))
            with summary_cols[1]:
                render_metric_box("最近目标 Y", f"{runs_df.iloc[0]['desired_half_life']:.1f} h")
            with summary_cols[2]:
                render_metric_box("最近策略", str(runs_df.iloc[0]["strategy_used"]))
            st.dataframe(runs_df, use_container_width=True, height=320)
        st.markdown("</div>", unsafe_allow_html=True)

    with upper_right:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("#### 最新状态")
        if latest_summary is not None:
            st.json(
                {
                    "run_id": latest_summary.run_id,
                    "status": latest_summary.status,
                    "report_path": latest_summary.report_path,
                }
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("#### 选中 Run 诊断")
    if selected_run_id is None:
        st.info("请先在前台实验室完成至少一次运行。")
    else:
        records_df = records_to_dataframe(store.list_run_experiments(selected_run_id))
        if records_df.empty:
            st.warning("该 run 没有轮次数据。")
        else:
            best_row = records_df.loc[records_df["desirability"].idxmax()]
            latest_row = records_df.iloc[-1]
            diag_cols = st.columns(3)
            with diag_cols[0]:
                render_metric_box("最佳误差", f"{best_row['target_error']:.3f}")
            with diag_cols[1]:
                render_metric_box("最佳 desirability", f"{best_row['desirability']:.4f}")
            with diag_cols[2]:
                render_metric_box("最新 half_life", f"{latest_row['half_life']:.2f} h")

            chart_cols = st.columns([1.1, 1], gap="large")
            with chart_cols[0]:
                render_svg_line_chart(
                    "误差与评分",
                    records_df.set_index("round")[["target_error", "desirability"]],
                    ["target_error", "desirability"],
                    colors=["#ff9478", "#7ae7ff"],
                    height=280,
                )
            with chart_cols[1]:
                render_svg_line_chart(
                    "关键实验输出",
                    records_df.set_index("round")[["half_life", "stability_index", "solubility"]],
                    ["half_life", "stability_index", "solubility"],
                    colors=["#7ae7ff", "#7effb2", "#ffd36f"],
                    height=280,
                )

            st.dataframe(
                records_df[
                    [
                        "round",
                        "created_at",
                        "half_life",
                        "stability_index",
                        "solubility",
                        "dissolution_rate",
                        "yield_percent",
                        "target_error",
                        "desirability",
                    ]
                ],
                use_container_width=True,
                height=300,
            )
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
