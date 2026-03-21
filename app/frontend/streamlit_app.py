from __future__ import annotations

import streamlit as st

from app.frontend.shared_ui import (
    configure_page,
    get_last_summary,
    get_store,
    inject_theme,
    render_status_banner,
    render_metric_box,
    render_page_head,
)


configure_page("虚拟药物实验室总览")


def main() -> None:
    inject_theme()
    store = get_store()
    runs = store.list_runs()
    latest_summary = get_last_summary()

    render_page_head(
        "虚拟实验室总览",
        "一个用于展示目标驱动闭环实验流程的虚拟实验室。前台负责执行，后台负责复盘。",
        tags=["Simulation-first", "Closed Loop"],
    )

    action_cols = st.columns([1, 1, 0.9], gap="large")
    with action_cols[0]:
        if st.button("进入前台实验室", use_container_width=True, type="primary"):
            st.switch_page("pages/1_前台实验室.py")
    with action_cols[1]:
        if st.button("查看后台观测室", use_container_width=True):
            st.switch_page("pages/2_后台观测室.py")
    with action_cols[2]:
        if st.button("查看接入路线", use_container_width=True):
            st.switch_page("pages/3_接入路线.py")

    render_status_banner(
        "使用路径",
        "先在前台设定目标并运行一轮虚拟实验，再到后台查看 run 历史、误差收敛和关键结果。",
        tone="default",
    )

    st.markdown("#### 当前状态")
    cols = st.columns(4)
    with cols[0]:
        render_metric_box("累计 runs", str(len(runs)))
    with cols[1]:
        render_metric_box("当前模式", "Simulation")
    with cols[2]:
        render_metric_box("默认策略", "BayBE")
    with cols[3]:
        render_metric_box("最近 run", "-" if latest_summary is None else latest_summary.run_id)


if __name__ == "__main__":
    main()
