# Handoff Notes

这份文档给后续要接真实接口、真实实验执行或真实数据回流的团队。

## 项目定位

当前仓库是一个可运行的 SDL demo 基座：

- 前端用于演示虚拟实验室流程
- 后端用于跑通目标 `Y -> 推荐 X -> 执行实验 -> 返回 Y -> 再优化`
- 当前实验执行和观测值来自模拟器
- 后续真实系统可以替换执行层和数据层，而不必从零开始重写闭环逻辑

## 当前已经跑通的能力

- BayBE 作为默认优化路径
- SQLite 持久化 run 和 experiment 记录
- Markdown / JSON 报告输出
- Streamlit 多页面演示前端
- FastAPI API 入口
- Docker 部署配置

## 当前不是最终生产系统的部分

- 实验执行仍是模拟器，不是实际机器人或工位
- 观测值 `Y` 仍是模拟返回，不是真实检测数据
- 前端是演示型页面，不是最终业务产品前端
- 历史分析页面仍是 demo 深度，不是完整中台

## 建议的接手顺序

### 1. 保留不动的部分

- `app/backend/models/`
- `app/backend/services/sdl_service.py`
- `app/backend/storage/sqlite_store.py`
- `app/backend/reporting/report_generator.py`

这些部分已经形成最基本的闭环骨架。

### 2. 优先替换的部分

- `app/backend/simulation/drug_lab_simulator.py`
- `app/backend/integrations/opentrons_executor.py`
- `app/backend/integrations/chemos_orchestrator.py`

真实接入时，优先把“模拟实验输出”替换成“真实执行 + 真实观测值”。

### 3. 后续可扩展部分

- 增加真实数据接口
- 增加模型对比与 benchmark 页面
- 增加历史处方复用能力
- 增加权限、审计和任务编排

## 当前前端结构

- `app/frontend/streamlit_app.py`
  总览页
- `app/frontend/pages/1_前台实验室.py`
  面向实验任务发起和演示
- `app/frontend/pages/2_后台观测室.py`
  面向历史 run、误差和诊断
- `app/frontend/pages/3_接入路线.py`
  面向未来真实接入说明

后续如果要改成正式产品前端，可以直接替换 Streamlit 层，而保留后端逻辑。

## 当前运行方式

### 本地

```bash
cd /Users/yuwen/work/ai-self-driving-drug-lab
source .venv/bin/activate
streamlit run app/frontend/streamlit_app.py
```

### Docker

```bash
docker compose up --build
```

## 数据输出位置

- SQLite 数据库：`outputs/sdl_lab.db`
- 报告文件：`outputs/*.md`
- 结构化报告：`outputs/*.json`

## 关键约束

- `strategy="baybe"` 是当前默认路径
- `auto` 已移除
- BayBE 失败时直接报错，不做静默兜底
- `surrogate` 仅保留给显式 benchmark
