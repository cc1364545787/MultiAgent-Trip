# 多 Agent 协作的智能行程规划助手

为解决单次大模型调用无法执行多步复杂任务的问题，基于 **LangGraph** 构建可自主规划、调用外部工具、并进行结果校验的智能体应用。

用户输入「我想去日本玩 5 天，预算 1 万」，系统自动完成攻略搜索、天气查询、路线规划，最终生成完整行程方案。

## 架构

```
用户需求
   ↓
规划者 Planner  ──拆解子任务──►  asyncio.Queue
   ↓                              │ 并行 worker
执行者 Executor  ◄──── 搜索 / 天气 / 汇率 / 日历
   ↓
校验者 Validator ──失败且可重试──► 执行者
   ↓ 通过或降级
主控汇总 Aggregator ──SSE──► React 调试面板 + 行程方案
```

- **Agent 工作流编排**：LangGraph「规划者 → 执行者 → 校验者」DAG，校验失败时回边重试，最后汇入主控节点。
- **工具调用**：`search_travel`、`get_weather`、`convert_currency`、`build_calendar`，带 Function Calling Schema；天气走 Open-Meteo，汇率走 Frankfurter。
- **反思与容错**：校验节点做 JSON/必填项/边界值检查，缺参自动补全，工具失败最多重试 3 次。
- **并行一致性**：子任务进入消息队列，多 worker 执行后按 `seq` 去重排序，状态机推进 `planning → executing → validating → aggregating → done`。
- **可视化 + SSE**：前端实时展示 Reasoning Trace、工具参数与返回值，以及「正在搜索攻略 → 正在查询天气 → 正在生成方案」。

未配置 `OPENAI_API_KEY` 时，规划与成稿走规则引擎，**工具调用仍然是真实网络请求**，方便本地演示。配置 Key 后，规划拆解与行程文案改由 OpenAI 兼容接口生成。

## 技术栈

Python · FastAPI · LangGraph · OpenAI Function Calling · React · Vite · TailwindCSS

## 启动

```bash
# 后端
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 可选：填入 OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000

# 前端（另开终端）
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173

## API

- `GET /api/health`
- `POST /api/plan/stream`  body: `{ "query": "我想去日本玩 5 天，预算 1 万" }`  SSE
- `POST /api/plan` 一次性 JSON（便于测试）

## 目录

```
backend/app/
  graph/          LangGraph 状态机与节点
  tools/          搜索 / 天气 / 汇率 / 日历
  services/       LLM、校验、异步协调器
  main.py         FastAPI + SSE
frontend/src/     流程可视化、调试面板、行程视图
```
