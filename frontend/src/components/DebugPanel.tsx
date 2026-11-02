import type { StreamEvent } from "../types";

const TONE: Record<string, string> = {
  reasoning: "text-amber-200",
  tool_call: "text-sky-300",
  tool_result: "text-emerald-300",
  validation: "text-violet-300",
  retry: "text-orange-300",
  error: "text-rose-300",
};

type Props = { events: StreamEvent[] };

export function DebugPanel({ events }: Props) {
  return (
    <section className="flex h-full min-h-[420px] flex-col rounded-3xl border border-line bg-panel/80">
      <header className="border-b border-line px-5 py-4">
        <h2 className="font-semibold">可视化调试面板</h2>
        <p className="text-xs text-slate-400">Reasoning Trace · 工具参数 · 返回值</p>
      </header>
      <div className="flex-1 space-y-3 overflow-auto p-4 font-mono text-[12px]">
        {events.length === 0 && <p className="text-slate-500">等待 Agent 开始推理…</p>}
        {events.map((event, index) => (
          <article key={`${event.type}-${index}`} className="rounded-2xl border border-line/80 bg-black/20 p-3">
            <div className="flex items-center justify-between gap-3">
              <span className={`font-medium ${TONE[event.type] ?? "text-slate-200"}`}>
                {event.type}
              </span>
              <span className="text-slate-500">{event.node ?? "graph"}</span>
            </div>
            <p className="mt-1 text-slate-300">{event.message}</p>
            {event.data && Object.keys(event.data).length > 0 && (
              <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap text-slate-400">
                {JSON.stringify(summarize(event.data), null, 2)}
              </pre>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}

function summarize(data: Record<string, unknown>) {
  const clone: Record<string, unknown> = { ...data };
  if (typeof clone.result === "object" && clone.result) {
    clone.result = compact(clone.result);
  }
  if (typeof clone.itinerary === "object") {
    clone.itinerary = "{… itinerary …}";
  }
  return clone;
}

function compact(value: unknown) {
  try {
    const text = JSON.stringify(value);
    return text.length > 500 ? `${text.slice(0, 500)}…` : JSON.parse(text);
  } catch {
    return value;
  }
}
