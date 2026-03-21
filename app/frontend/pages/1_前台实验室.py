from __future__ import annotations

import streamlit as st

from app.backend.models.schemas import SDLRequest
from app.frontend.shared_ui import (
    build_front_lab_request_inputs,
    configure_page,
    get_front_lab_advanced_settings,
    get_last_summary,
    get_service,
    inject_theme,
    parameter_display_items,
    render_metric_grid,
    render_status_banner,
    result_display_items,
    set_last_summary,
)


configure_page("前台实验室")


def main() -> None:
    inject_theme()
    service = get_service()
    advanced = get_front_lab_advanced_settings()
    desired_half_life, tolerance, execute = build_front_lab_request_inputs(
        strategy=advanced["strategy"],
        target_mode=advanced["target_mode"],
    )
    advanced = get_front_lab_advanced_settings()
    request = SDLRequest(
        desired_half_life=desired_half_life,
        tolerance=tolerance,
        max_rounds=advanced["max_rounds"],
        initial_random_samples=advanced["initial_random_samples"],
        target_mode=advanced["target_mode"],
        strategy=advanced["strategy"],
        weights=advanced["weights"],
    )

    if execute:
        set_last_summary(service.run_closed_loop(request))

    summary = get_last_summary()

    if summary is None:
        st.markdown('<div class="data-block">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">本次实验任务</h3>', unsafe_allow_html=True)
        st.info("设置目标后点击“启动虚拟实验”，这里会返回本次最优实验方案和实验结果。")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    tone = "success" if summary.best_result.target_error <= summary.tolerance else "warn"
    message = (
        f"本次最佳 half_life 为 {summary.best_result.half_life:.2f} h，已经进入允许误差范围内。"
        if tone == "success"
        else f"本次最佳 half_life 为 {summary.best_result.half_life:.2f} h，距离目标还差 {summary.best_result.target_error:.3f}。"
    )
    render_status_banner("本次实验结论", message, tone=tone)

    render_metric_grid(
        [
            ("目标值", f"{request.desired_half_life:.1f} h"),
            ("最佳结果", f"{summary.best_result.half_life:.2f} h"),
            ("目标误差", f"{summary.best_result.target_error:.3f}"),
            ("实验轮次", str(len(summary.rounds))),
            ("运行状态", summary.status),
            ("优化策略", summary.strategy_used),
        ],
        columns=3,
    )

    st.markdown('<h3 class="section-title">实验回报单</h3>', unsafe_allow_html=True)
    st.markdown('<p class="section-copy">下面是这次实验最值得汇报的两部分：系统给出的方案 X，以及实验返回的结果 Y。</p>', unsafe_allow_html=True)
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown('<div class="data-block">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">本次最佳实验方案 X</h3>', unsafe_allow_html=True)
        st.markdown('<p class="section-copy">系统基于当前目标和已观测数据生成的推荐实验条件。</p>', unsafe_allow_html=True)
        render_metric_grid(parameter_display_items(summary.best_parameters), columns=2)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="data-block">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">本次最佳实验结果 Y</h3>', unsafe_allow_html=True)
        st.markdown('<p class="section-copy">虚拟实验返回的关键输出，用来判断这次方案是否接近目标。</p>', unsafe_allow_html=True)
        render_metric_grid(result_display_items(summary.best_result), columns=2)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<p class="muted-copy">本页只展示本次实验执行结果。历史 run、误差收敛、每轮明细和诊断信息请到后台观测室查看。</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
