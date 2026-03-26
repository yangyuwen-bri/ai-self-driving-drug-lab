# AutoQuant

`AutoQuant` 是一个面向目标驱动闭环优化场景的开源框架。

它解决的不是“单次预测”，而是这类问题：

1. 定义目标 `y*`
2. 基于历史 `(x, y)` 生成下一轮候选 `x`
3. 执行模拟、人工流程或真实系统
4. 读取反馈 `y`
5. 更新 planner 表现并继续迭代

一句话说，`AutoQuant` 是一个 **simulation-first 的闭环量化优化框架**。

## 适用场景

- 配方优化
- 工艺参数调优
- 材料性能搜索
- 工业过程控制
- 任何“给定目标指标，反推下一轮参数并迭代优化”的场景

## 核心设计

框架围绕 6 个可插拔层组织：

- `spec`
  - 定义参数、目标、固定组分和约束
- `planner`
  - 根据历史和目标提出下一轮候选 `x`
- `executor`
  - 把候选送到模拟器、人工流程或真实系统
- `feedback`
  - 读取测量结果 `y`
- `orchestrator`
  - 推进 DMTA 闭环
- `storage / modeling`
  - 记录 campaign 历史并总结 planner 表现

## 现有能力

- 通用领域模型：`ScenarioSpec / CampaignConfig / CampaignRoundRecord / Measurement`
- 通用目标评分：`match_bell + maximize`
- 可插拔 planner：
  - `RandomPlanner`
  - `AdaptivePlanner`
  - `BayBEPlanner`（可选）
- 可插拔 executor / feedback
- 最小同步 DMTA 编排器：`SequentialOrchestrator`
- 内存 store 与内存 model registry
- 通用 benchmark runner
- 两个 packaged examples：
  - `drug_lab`
  - `coating_line`

## 这轮新增的框架能力

- built-in scenario loader
  - `autoquant.scenarios.load_builtin_scenario("drug_lab")`
  - `autoquant.scenarios.load_scenario_file("scenario.json")`
- component registry
  - `autoquant.registry.build_planner_registry()`
  - `autoquant.registry.build_executor_registry()`
  - `autoquant.registry.build_feedback_registry()`
- benchmark report export
  - `BenchmarkReport.to_dict()`
  - `BenchmarkReport.to_markdown()`

## 安装

进入 `framework/` 目录后执行：

```bash
python -m pip install -e .
```

如果你需要 BayBE planner：

```bash
python -m pip install -e '.[baybe]'
```

## Quickstart

### 1. 运行药物配方示例

```bash
autoquant-drug-lab --target-half-life 12.0 --tolerance 0.5 --max-rounds 8
```

### 2. 运行工业涂布线示例

```bash
autoquant-coating-line --target-thickness 85 --tolerance 3 --max-rounds 8
```

### 3. 跑 planner benchmark

```bash
autoquant-coating-benchmark --target-thickness 85 --replicates 3 --max-rounds 5
```

输出都是 JSON，方便继续接 UI、报告或实验系统。

## Example Scenarios

### Drug Lab

一个 simulation-first 的药物配方示例，目标包括：

- `half_life`
- `stability_index`
- `solubility`

示例入口：

- `autoquant.examples.drug_lab.run_example`

### Coating Line

一个工业过程示例，目标包括：

- `coating_thickness`
- `adhesion_index`
- `throughput`

示例入口：

- `autoquant.examples.coating_line.run_example`
- `autoquant.examples.coating_line.benchmark_example`

## Public API Surface

当前建议直接使用的公共接口：

- `autoquant.core`
- `autoquant.planners`
- `autoquant.executors`
- `autoquant.feedback`
- `autoquant.orchestration`
- `autoquant.storage`
- `autoquant.modeling`
- `autoquant.benchmarking`
- `autoquant.scenarios`
- `autoquant.registry`

扩展约定见：

- `docs/EXTENDING.md`

## Build Your Own Scenario

一个最小自定义场景需要 4 步：

1. 定义 `ScenarioSpec`
2. 提供一个 `Planner`
3. 提供一个 `Executor` 和 `FeedbackProvider`
4. 用 `SequentialOrchestrator` 跑 campaign

最小代码结构类似：

```python
from autoquant.core import CampaignConfig, ObjectiveSpec, ParameterSpec, ScenarioSpec
from autoquant.executors import NoOpExecutor
from autoquant.feedback import SyntheticFeedbackProvider
from autoquant.modeling import InMemoryModelRegistry
from autoquant.orchestration import SequentialOrchestrator
from autoquant.planners import RandomPlanner
from autoquant.storage import InMemoryCampaignStore

scenario = ScenarioSpec(
    name="toy",
    parameters=[ParameterSpec("x", 0.0, 10.0)],
    objectives=[ObjectiveSpec("y", mode="match_bell", target=5.0, tolerance=0.5)],
)

campaign = CampaignConfig(
    campaign_id="toy-001",
    scenario_name=scenario.name,
    target={"y": 5.0},
    tolerance=0.5,
    max_rounds=5,
)

def measure(scenario, campaign, suggestion, artifacts):
    x = suggestion.parameters["x"]
    return Measurement(values={"y": x})

orchestrator = SequentialOrchestrator(
    planner=RandomPlanner(seed=7),
    executor=NoOpExecutor(),
    feedback_provider=SyntheticFeedbackProvider(measure),
    store=InMemoryCampaignStore(),
    model_registry=InMemoryModelRegistry(),
)

history = orchestrator.run_campaign(scenario, campaign)
```

如果你希望从配置文件加载场景，而不是手写 Python：

```python
from autoquant.scenarios import load_builtin_scenario, load_scenario_file

scenario = load_builtin_scenario("drug_lab")
other_scenario = load_scenario_file("my_scenario.json")
```

如果你希望按名字创建内置 planner / executor / feedback：

```python
from autoquant.registry import (
    build_executor_registry,
    build_feedback_registry,
    build_planner_registry,
)

planners = build_planner_registry()
executors = build_executor_registry()
feedback = build_feedback_registry()

random_planner = planners.create("random", seed=7)
noop_executor = executors.create("noop")
synthetic_feedback = feedback.create("synthetic", measure_fn=my_measure_fn)
```

## Benchmarking

`AutoQuant` 不只支持“跑一个例子”，也支持系统比较不同 planner。

使用：

- `autoquant.benchmarking.benchmark_planners`

它会：

- 对每个 planner 跑多次 campaign
- 聚合 `avg_best_error / success_rate / avg_rounds_run`
- 返回统一的 benchmark report

这一步对做自动选优和 planner selection 很关键。

## BayBE Plugin

`BayBEPlanner` 是可选 planner plugin。

特点：

- 自动从 `ScenarioSpec` 构建 BayBE search space
- 支持 `match_bell` 和 `maximize`
- 使用 `Random -> Botorch` 两阶段推荐

如果运行环境没有安装 BayBE，对框架其他部分没有影响。

## 运行测试

```bash
python -m unittest discover -s tests -v
```

## 仓库关系

当前这个目录位于一个更大的 demo 仓库中：

- `app/` 仍然是现有 demo app
- `framework/` 是独立的通用框架线

后续如果框架成熟，可以再单独拆成独立 repo。
