from __future__ import annotations

import streamlit as st

from app.frontend.shared_ui import (
    configure_page,
    get_last_summary,
    get_store,
    inject_theme,
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
            <p class="hero-copy">这是一个可运行的虚拟实验室 demo，用来演示目标驱动的闭环实验优化流程，并为后续真实实验接入做准备。</p>
            <div class="hero-actions tight">
                <span class="chip">虚拟闭环实验</span>
                <span class="chip">BayBE 优化</span>
                <span class="chip">真实接入预留</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    action_cols = st.columns([1, 1, 1.45], gap="large")
    with action_cols[0]:
        if st.button("进入前台实验室", use_container_width=True, type="primary"):
            st.switch_page("pages/1_前台实验室.py")
    with action_cols[1]:
        if st.button("查看后台观测室", use_container_width=True):
            st.switch_page("pages/2_后台观测室.py")
    with action_cols[2]:
        st.markdown('<p class="muted-copy">先在前台设定目标并运行一轮虚拟实验，再去后台查看 run 历史、误差收敛和最佳结果。</p>', unsafe_allow_html=True)

    st.markdown("#### 模块入口")
    nav_cols = st.columns(3, gap="large")
    with nav_cols[0]:
        st.markdown(
            """
            <div class="nav-card">
                <div class="nav-title">前台实验室</div>
                <p class="nav-copy">输入目标半衰期，自动生成实验处方，并执行一轮虚拟闭环实验。</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with nav_cols[1]:
        st.markdown(
            """
            <div class="nav-card">
                <div class="nav-title">后台观测室</div>
                <p class="nav-copy">查看 run 历史、每轮误差变化、最佳结果和关键收敛轨迹。</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with nav_cols[2]:
        st.markdown(
            """
            <div class="nav-card">
                <div class="nav-title">接入路线</div>
                <p class="nav-copy">说明后续如何接入真实实验设备、实测数据回流和系统接口。</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### 当前 demo 状态")
    cols = st.columns(3)
    with cols[0]:
        render_metric_box("累计 runs", str(len(runs)))
    with cols[1]:
        render_metric_box("当前模式", "Simulation")
    with cols[2]:
        render_metric_box("最近 run", "-" if latest_summary is None else latest_summary.run_id)


if __name__ == "__main__":
    main()
