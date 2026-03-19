# AI Self-Driving Drug Lab

一个面向药物配方研发的 Self-Driving Laboratory（SDL）演示型闭环原型。

这个仓库的目标不是直接替代真实实验室系统，而是提供一个：

- 可运行的虚拟实验室 demo
- 可演示的前后台分视图
- 可交接给后续真实接口团队的基础骨架

当前能力覆盖：

1. 实验数据库 + X/Y 关系建模
2. 用户输入目标 `Y` 后自动反推最优 `X`
3. 每轮自动执行模拟实验、记录结果、更新优化策略
4. 生成最优配方与实验报告
5. 为 Opentrons / ChemOS 2.0 / Atlas / Olympus / MADSci 预留真实集成位

## 快速开始

本地直接运行前端演示：

```bash
source .venv/bin/activate
streamlit run app/frontend/streamlit_app.py
```

打开：

- [http://localhost:8501](http://localhost:8501)

如果只想跑一轮 CLI 闭环：

```bash
source .venv/bin/activate
PYTHONPATH=. python scripts/run_demo_loop.py
```

## 仓库交付物

- 前端演示总览与分页面：`app/frontend/`
- 后端闭环逻辑：`app/backend/services/`
- 优化器与 BayBE 接入：`app/backend/optimization/`
- 模拟实验执行层：`app/backend/simulation/`
- SQLite 数据与报告输出：`outputs/`
- Docker 部署配置：`Dockerfile`、`docker-compose.yml`
- Render 部署配置：`render.yaml`
- 演示讲稿：`docs/DEMO_GUIDE.md`
- 接手说明：`docs/HANDOFF.md`

## 技术栈

- `BayBE`：核心 Bayesian Optimization 适配层，生产默认策略；未安装或运行失败时直接报错，不做静默兜底
- `FastAPI`：后端 API 入口（已写好兼容代码，安装依赖后启用）
- `Streamlit`：MVP 深色科技实验室前端
- `SQLite`：实验数据库
- `scikit-learn`：本地 surrogate model 重训
- `Docker` / `docker-compose`：部署入口

## 三大系统部分

### 第一部分：实验数据库 + X-Y 关系模型自动计算

- `app/backend/storage/sqlite_store.py`
- `app/backend/services/sdl_service.py`
- `app/backend/optimization/surrogate_optimizer.py`
- `app/backend/simulation/drug_lab_simulator.py`

### 第二部分：模拟实验前端界面

- `app/frontend/streamlit_app.py`
- 用户输入目标 `Y`
- 自动推荐最优 `X`
- 一键执行闭环实验

### 第三部分：后端算法界面

- 每轮自动重训 surrogate
- 展示轮次性能、最优组合、误差收敛
- 支持单目标与多目标 desirability

## 参数空间

固定配料保存在 [data/fixed_components.json](data/fixed_components.json)。

优化变量 `X`：

- `temperature`: 20.0~80.0
- `humidity`: 40.0~80.0
- `aux1_ratio`: 0.5~5.0
- `aux2_ratio`: 0.0~3.0
- `duration`: 60.0~300.0
- `stirring_speed`: 100.0~1000.0
- `pH`: 4.0~9.0
- `solvent_concentration`: 10.0~50.0

输出 `Y`：

- `half_life`
- `solubility`
- `stability_index`
- `dissolution_rate`
- `yield_percent`

## 集成路线图

以下仓库已经在项目文档和 integration stub 中对应到阶段化接入点：

1. BayBE: <https://github.com/emdgroup/baybe>
2. ChemOS 2.0: <https://github.com/malcolmsimgithub/ChemOS2.0>
3. Opentrons Python API: <https://github.com/Opentrons/opentrons>
4. Olympus: <https://github.com/aspuru-guzik-group/olympus>
5. Atlas: <https://github.com/aspuru-guzik-group/atlas>
6. MADSci: <https://github.com/AD-SDL/MADSci>
7. awesome-self-driving-labs: <https://github.com/AccelerationConsortium/awesome-self-driving-labs>

## 本地运行

当前推荐环境为已安装完整依赖的 `.venv`。因此：

- Streamlit MVP / FastAPI / BayBE 闭环都可直接运行
- `strategy="baybe"` 是默认生产路径，`strategy="surrogate"` 仅用于显式 benchmark

### 1. 创建并使用虚拟环境

当前本机最稳妥的方式是使用 `python3.12` 并复用已安装站点包：

```bash
python3.12 -m venv --system-site-packages .venv
source .venv/bin/activate
python --version
```

### 2. 运行 Streamlit MVP

```bash
source .venv/bin/activate
streamlit run app/frontend/streamlit_app.py
```

### 3. 运行 CLI 闭环 demo

```bash
source .venv/bin/activate
PYTHONPATH=. python scripts/run_demo_loop.py
```

### 4. 启用 API

```bash
source .venv/bin/activate
PYTHONPATH=. \
uvicorn app.backend.api.main:app --reload
```

如果后续联网安装完整依赖，可再执行：

```bash
pip install -r requirements.txt
```

注意：

- 不再支持 `auto` 策略
- `baybe` 路径失败时会直接抛错，避免误以为仍在使用最优优化器

## Docker

生产部署：

```bash
docker compose up --build
```

开发模式：

```bash
docker compose -f docker-compose.dev.yml up --build
```

说明：

- [docker-compose.yml](docker-compose.yml) 是生产态配置，不再把源码目录直接挂进容器
- 生产态使用命名卷 `sdl_outputs` 持久化 `SQLite` 数据库和报告文件
- [docker-compose.dev.yml](docker-compose.dev.yml) 保留源码挂载与 API `--reload`，仅用于本地开发

## Render 部署

仓库已包含 [render.yaml](render.yaml)，可以直接作为 Render Blueprint 导入。

推荐部署方式：

- 服务类型：`Web Service`
- Runtime：`Docker`
- 计划：`Starter`
- 持久化磁盘挂载路径：`/app/outputs`
- 健康检查路径：`/_stcore/health`

关键环境变量已写入 `render.yaml`：

- `PORT=10000`
- `SDL_DB_PATH=/app/outputs/sdl_lab.db`
- `SDL_REPORT_DIR=/app/outputs`

说明：

- Render 默认文件系统是临时的，因此需要磁盘来保留 `SQLite` 和报告文件
- 当前 demo 推荐只部署 Streamlit 这一套服务，不单独拆 API 服务

## 上线建议

推荐先创建 GitHub 仓库，再部署到云主机或支持 Docker 的平台。

典型流程：

```bash
git init
git add .
git commit -m "Initial deployment-ready SDL app"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

服务器部署：

```bash
git clone <your-github-repo-url>
cd ai-self-driving-drug-lab
docker compose up -d --build
```

## 验证

```bash
python3 -m unittest discover -s tests -v
```

## 演示说明

如果你需要一份给项目所有者自己看的演示讲稿和页面解释，见：

- [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md)
