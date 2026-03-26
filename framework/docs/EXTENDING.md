# Extending AutoQuant

`AutoQuant` 的核心目标是让你替换场景，而不是重写框架。

最常见的扩展点有 4 个：

## 1. 自定义 Scenario

定义：

- 参数空间 `X`
- 目标 `Y`
- 目标模式
- 固定组分和约束

入口类型：

- `autoquant.core.specs.ParameterSpec`
- `autoquant.core.specs.ObjectiveSpec`
- `autoquant.core.specs.ScenarioSpec`

## 2. 自定义 Planner

实现：

- `autoquant.planners.base.Planner`

只需要提供：

```python
def propose(self, scenario, campaign, history) -> PlannerSuggestion:
    ...
```

建议返回：

- `planner_name`
- `parameters`
- `rationale`
- `metadata`

如果 planner 依赖外部库，尽量像 `BayBEPlanner` 一样做成可选插件，不要破坏基础安装。

## 3. 自定义 Executor

实现：

- `autoquant.executors.base.Executor`

职责：

- 接收 planner 给出的候选参数
- 触发模拟器、人工流程或真实系统
- 返回 artifacts

artifact 可以是：

- payload
- 文件路径
- task id
- 仪器提交记录

## 4. 自定义 FeedbackProvider

实现：

- `autoquant.feedback.base.FeedbackProvider`

职责：

- 从执行产物、模拟器、文件或外部系统拿回测量结果
- 返回 `Measurement`

这一步最好只关心“怎么得到 `y`”，不要把优化逻辑塞进这里。

## 推荐模式

一个新的场景通常按下面顺序接入：

1. 定义 `ScenarioSpec`
2. 先接 simulation feedback
3. 跑通 `SequentialOrchestrator`
4. 再接更复杂的 planner
5. 最后补 benchmark

## 目录建议

如果你基于 AutoQuant 新增一个场景，推荐类似：

```text
my_project/
  spec.py
  planner.py
  simulator.py
  executor.py
  feedback.py
  run_example.py
```

如果场景成熟，再把它做成 packaged example。

## 配置化接入

如果不想把场景写死在 Python 里，可以直接用：

- `autoquant.scenarios.load_builtin_scenario()`
- `autoquant.scenarios.load_scenario_file()`

推荐做法是：

1. 先用 JSON 场景文件定义参数和目标
2. 再用 Python 实现 planner / simulator / feedback
3. 最后把它注册到你自己的应用或 CLI

## 注册内置组件

框架还提供了基础 registry：

- `build_planner_registry()`
- `build_executor_registry()`
- `build_feedback_registry()`

这适合：

- 做配置驱动应用
- 按名称创建 planner
- 在 UI 中展示“可选组件”
