from __future__ import annotations

import streamlit as st

from app.frontend.shared_ui import (
    count_completed_runs,
    configure_page,
    get_last_summary,
    get_store,
    inject_theme,
    records_to_dataframe,
    render_metric_grid,
    render_metric_box,
    render_round_cards,
    render_run_cards,
    render_page_head,
    render_status_banner,
    render_svg_line_chart,
    summarize_strategy,
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

    render_page_head(
        "后台观测室",
        "这里集中查看历史 run、关键轨迹、每轮明细和诊断结论，用来解释系统为什么得到当前结果。",
        tags=["Back Office", f"{len(runs_df)} runs", "Diagnostics"],
    )

    top_left, top_right = st.columns([1.2, 1], gap="large")
    with top_left:
        st.markdown('<h3 class="section-title">历史 runs</h3>', unsafe_allow_html=True)
        st.markdown('<p class="section-copy">这里保留最近几次实验记录。左侧选择 run，主区用卡片对比目标、状态、策略和完成时间。</p>', unsafe_allow_html=True)
        if runs_df.empty:
            st.info("数据库中还没有历史运行记录。")
        else:
            summary_cols = st.columns(3)
            with summary_cols[0]:
                render_metric_box("累计 runs", str(len(runs_df)))
            with summary_cols[1]:
                render_metric_box("已完成 runs", str(count_completed_runs(runs_df)))
            with summary_cols[2]:
                render_metric_box("当前目标 Y", f"{runs_df.iloc[0]['desired_half_life']:.1f} h")
            render_run_cards(runs_df, selected_run_id=selected_run_id, limit=8)

    with top_right:
        st.markdown('<h3 class="section-title">选中 run 诊断</h3>', unsafe_allow_html=True)
        st.markdown('<p class="section-copy">先确认这次 run 的目标、状态和策略，再往下看误差、评分和关键输出的收敛过程。</p>', unsafe_allow_html=True)
        if selected_run_id is None:
            st.info("先去前台实验室运行至少一次实验。")
        else:
            run_row = runs_df.loc[runs_df["run_id"] == selected_run_id].iloc[0]
            render_metric_grid(
                [
                    ("run_id", str(run_row["run_id"])),
                    ("目标值", f"{float(run_row['desired_half_life']):.1f} h"),
                    ("状态", str(run_row["status"])),
                    ("策略", summarize_strategy(str(run_row["strategy_used"]))),
                ],
                columns=2,
            )
            if latest_summary is not None and latest_summary.run_id == selected_run_id:
                st.markdown(
                    f'<p class="muted-copy">最新报告：{latest_summary.report_path}</p>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown('<p class="muted-copy">报告路径已写入本地 outputs 目录，可在仓库环境中查看。</p>', unsafe_allow_html=True)

    st.markdown('<h3 class="section-title">收敛与复盘</h3>', unsafe_allow_html=True)
    st.markdown('<p class="section-copy">从误差、评分和关键输出三个角度复盘这次 run 如何逼近目标，并查看每轮实验记录。</p>', unsafe_allow_html=True)
    if selected_run_id is None:
        st.info("请先在前台实验室完成至少一次运行。")
    else:
        records_df = records_to_dataframe(store.list_run_experiments(selected_run_id))
        if records_df.empty:
            st.warning("该 run 没有轮次数据。")
        else:
            best_row = records_df.loc[records_df["desirability"].idxmax()]
            latest_row = records_df.iloc[-1]
            target_value = float(runs_df.loc[runs_df["run_id"] == selected_run_id].iloc[0]["desired_half_life"])
            gap = abs(float(best_row["half_life"]) - target_value)
            tone = "success" if gap <= float(runs_df.loc[runs_df["run_id"] == selected_run_id].iloc[0]["tolerance"]) else "warn"
            message = (
                f"最佳轮次 half_life 为 {best_row['half_life']:.2f} h，已进入目标范围。"
                if tone == "success"
                else f"最佳轮次 half_life 为 {best_row['half_life']:.2f} h，仍比目标偏离 {gap:.3f}。"
            )
            render_status_banner("诊断结论", message, tone=tone)

            render_metric_grid(
                [
                    ("最佳误差", f"{best_row['target_error']:.3f}"),
                    ("最佳评分", f"{best_row['desirability']:.4f}"),
                    ("最佳 half_life", f"{best_row['half_life']:.2f} h"),
                    ("最新 half_life", f"{latest_row['half_life']:.2f} h"),
                ],
                columns=4,
            )

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

            st.markdown("##### 每轮实验明细")
            render_round_cards(
                records_df[
                    [
                        "round",
                        "created_at",
                        "half_life",
                        "stability_index",
                        "solubility",
                        "yield_percent",
                        "target_error",
                        "desirability",
                    ]
                ]
            )


if __name__ == "__main__":
    main()
