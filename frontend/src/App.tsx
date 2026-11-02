import { FormEvent, useMemo, useState } from "react";
import { DebugPanel } from "./components/DebugPanel";
import { ItineraryView } from "./components/ItineraryView";
import { WorkflowGraph } from "./components/WorkflowGraph";
import { streamPlan } from "./lib/sse";
import type { Itinerary, StreamEvent, SubTask } from "./types";

const EXAMPLES = [
  "我想去日本玩 5 天，预算 1 万",
  "首尔 4 天，预算 6000，想吃烤肉看夜景",
  "泰国曼谷 6 天自由行，预算 8000",
];

export default function App() {
  const [query, setQuery] = useState(EXAMPLES[1]);
  const [running, setRunning] = useState(false);
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeNode, setActiveNode] = useState<string | null>(null);
  const [status, setStatus] = useState("等待输入");
  const [tasks, setTasks] = useState<SubTask[]>([]);

  const progress = useMemo(() => {
    const reasoning = [...events].reverse().find((item) => item.type === "reasoning" && item.node === "executor");
    return reasoning?.message || status;
  }, [events, status]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const text = query.trim();
    if (!text || running) return;
    setRunning(true);
    setEvents([]);
    setItinerary(null);
    setError(null);
    setActiveNode("planner");
    setStatus("正在规划…");
    setTasks([]);

    try {
      await streamPlan(text, (incoming) => {
        setEvents((prev) => [...prev, incoming]);
        if (incoming.node) setActiveNode(incoming.node);
        if (incoming.type === "status" || incoming.type === "reasoning") setStatus(incoming.message);
        if (incoming.type === "plan") setTasks((incoming.data?.tasks as SubTask[]) ?? []);
        if (incoming.type === "itinerary") setItinerary(incoming.data?.itinerary as Itinerary);
        if (incoming.type === "error") setError(incoming.message);
      });
      setStatus("方案已生成");
      setActiveNode("aggregator");
    } catch (err) {
      setError(err instanceof Error ? err.message : "未知错误");
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="mx-auto min-h-screen max-w-7xl px-4 py-8 md:px-8 text-slate-100 bg-slate-950 selection:bg-amber-400 selection:text-slate-950">
      {/* 顶部标题区 */}
      <header className="mb-8 flex flex-wrap items-end justify-between gap-4 border-b border-slate-900 pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-amber-400/10 px-3 py-1 font-mono text-xs text-amber-300 border border-amber-400/20">
              LangGraph · FastAPI · SSE
            </span>
          </div>
          <h1 className="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
            多 Agent 协作的智能行程规划助手
          </h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-400 leading-relaxed">
            规划者拆解意图，执行者并行调用搜索 / 天气 / 汇率 / 日历，校验者检查 JSON 与边界值，主控节点按序汇总并生成完整方案。
          </p>
        </div>
        <div className={`flex items-center gap-2 rounded-2xl border px-4 py-2.5 text-sm font-medium transition-all ${
          running 
            ? "border-amber-400/40 bg-amber-400/10 text-amber-300 shadow-[0_0_15px_rgba(252,211,77,0.15)]" 
            : "border-slate-800 bg-slate-900/80 text-slate-300"
        }`}>
          <span className={`h-2 w-2 rounded-full ${running ? "bg-amber-400 animate-ping" : "bg-emerald-400"}`} />
          <span>{running ? "Agent 运行中…" : "系统空闲"}</span>
        </div>
      </header>

      {/* 工作流节点可视化图 */}
      <WorkflowGraph activeNode={activeNode} done={Boolean(itinerary) && !running} />

      {/* 输入与表单区 */}
      <form onSubmit={onSubmit} className="mt-6 rounded-3xl border border-slate-800/80 bg-slate-900/60 p-5 md:p-6 shadow-xl backdrop-blur-xl">
        <label className="block text-xs font-mono uppercase tracking-wider text-slate-400 mb-2">
          描述你的旅行需求
        </label>
        <div className="flex flex-col gap-3 md:flex-row">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 rounded-2xl border border-slate-700 bg-slate-950/80 px-4 py-3.5 text-slate-100 placeholder-slate-500 outline-none transition focus:border-amber-400 focus:ring-2 focus:ring-amber-400/20"
            placeholder="例如：首尔 4 天，预算 6000，想吃烤肉看夜景"
          />
          <button
            type="submit"
            disabled={running}
            className="rounded-2xl bg-amber-400 px-6 py-3.5 font-semibold text-slate-950 shadow-lg shadow-amber-400/20 transition hover:bg-amber-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {running ? "规划中…" : "开始规划"}
          </button>
        </div>

        {/* 快捷示例标签 */}
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-500 font-mono">💡 猜你想搜：</span>
          {EXAMPLES.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setQuery(item)}
              className="rounded-full border border-slate-800 bg-slate-900/80 px-3.5 py-1.5 text-xs text-slate-300 transition hover:border-amber-400/50 hover:text-amber-200 hover:bg-slate-800"
            >
              {item}
            </button>
          ))}
        </div>
      </form>

      {/* 实时进度提示条 */}
      <div className="mt-4 flex items-center gap-3 rounded-2xl border border-sky-500/20 bg-sky-500/10 px-4 py-3 text-sm text-sky-200 shadow-sm">
        <span className="animate-pulse">⚡</span>
        <span className="font-mono text-xs">{progress}</span>
      </div>

      {/* 拆解的子任务标签列表 */}
      {tasks.length > 0 && (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-500 font-mono">DAG 任务流：</span>
          {tasks.map((task) => (
            <span key={task.id} className="rounded-xl border border-slate-800 bg-slate-900/80 px-3 py-1 text-xs text-slate-300 font-mono">
              <span className="text-amber-400 mr-1">#{task.seq}</span> {task.title}
            </span>
          ))}
        </div>
      )}

      {/* 错误提示 */}
      {error && (
        <div className="mt-4 rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
          ⚠️ {error}
        </div>
      )}

      {/* 主体双栏区域：左侧行程单（占 7 列） + 右侧调试面板（占 5 列） */}
      <div className="mt-6 grid gap-6 lg:grid-cols-12">
        <div className="lg:col-span-7 w-full">
          <ItineraryView itinerary={itinerary} running={running} />
        </div>
        <div className="lg:col-span-5 w-full">
          <DebugPanel events={events} />
        </div>
      </div>
    </div>
  );
}