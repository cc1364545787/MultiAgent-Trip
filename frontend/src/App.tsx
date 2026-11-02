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
  const [query, setQuery] = useState(EXAMPLES[0]);
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
    <div className="mx-auto min-h-screen max-w-7xl px-4 py-8 md:px-8">
      <header className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-sky-300">LangGraph · FastAPI · SSE</p>
          <h1 className="mt-2 text-3xl font-semibold md:text-4xl">多 Agent 协作的智能行程规划助手</h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-400">
            规划者拆解意图，执行者并行调用搜索 / 天气 / 汇率 / 日历，校验者检查 JSON 与边界值，主控节点按序汇总并生成完整方案。
          </p>
        </div>
        <div className="rounded-2xl border border-line bg-panel px-4 py-3 text-sm text-slate-300">
          {running ? "Agent 运行中" : "空闲"}
        </div>
      </header>

      <WorkflowGraph activeNode={activeNode} done={Boolean(itinerary) && !running} />

      <form onSubmit={onSubmit} className="mt-6 rounded-3xl border border-line bg-panel/80 p-4 md:p-5">
        <label className="text-sm text-slate-400">描述你的旅行需求</label>
        <div className="mt-2 flex flex-col gap-3 md:flex-row">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 rounded-2xl border border-line bg-ink px-4 py-3 outline-none ring-amber-300/40 focus:ring"
            placeholder="我想去日本玩 5 天，预算 1 万"
          />
          <button
            type="submit"
            disabled={running}
            className="rounded-2xl bg-amber-300 px-5 py-3 font-semibold text-ink disabled:opacity-60"
          >
            {running ? "规划中…" : "开始规划"}
          </button>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {EXAMPLES.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setQuery(item)}
              className="rounded-full border border-line px-3 py-1 text-xs text-slate-300 hover:border-amber-300/50"
            >
              {item}
            </button>
          ))}
        </div>
      </form>

      <div className="mt-4 rounded-2xl border border-sky-400/20 bg-sky-400/10 px-4 py-3 text-sm text-sky-100">
        {progress}
      </div>

      {tasks.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {tasks.map((task) => (
            <span key={task.id} className="rounded-full border border-line bg-panel px-3 py-1 text-xs text-slate-300">
              {task.seq}. {task.title}
            </span>
          ))}
        </div>
      )}

      {error && <p className="mt-4 text-sm text-rose-300">{error}</p>}

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <ItineraryView itinerary={itinerary} running={running} />
        <DebugPanel events={events} />
      </div>
    </div>
  );
}
