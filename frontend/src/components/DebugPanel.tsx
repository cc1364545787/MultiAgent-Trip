import React from 'react';
import type { StreamEvent } from "../types";

const TONE: Record<string, { badge: string; border: string; text: string; icon: string }> = {
  reasoning: { badge: "bg-amber-500/20 text-amber-300 border-amber-500/30", border: "border-amber-500/20", text: "text-amber-200", icon: "🧠" },
  tool_call: { badge: "bg-sky-500/20 text-sky-300 border-sky-500/30", border: "border-sky-500/20", text: "text-sky-200", icon: "⚡" },
  tool_result: { badge: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30", border: "border-emerald-500/20", text: "text-emerald-200", icon: "✨" },
  validation: { badge: "bg-violet-500/20 text-violet-300 border-violet-500/30", border: "border-violet-500/20", text: "text-violet-200", icon: "🛡️" },
  retry: { badge: "bg-orange-500/20 text-orange-300 border-orange-500/30", border: "border-orange-500/20", text: "text-orange-200", icon: "🔄" },
  error: { badge: "bg-rose-500/20 text-rose-300 border-rose-500/30", border: "border-rose-500/20", text: "text-rose-200", icon: "⚠️" },
};

type Props = { events: StreamEvent[] };

export function DebugPanel({ events }: Props) {
  return (
    /* 核心修改：使用 sticky 让其在页面滚动时吸顶，并通过 h-[700px] 固定整体高度 */
    <div className="sticky top-6 flex h-[700px] flex-col rounded-3xl border border-slate-800 bg-slate-950/90 shadow-2xl backdrop-blur-xl">
      <header className="flex items-center justify-between border-b border-slate-800/80 px-5 py-4 shrink-0">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="font-semibold text-slate-100">可视化调试面板</h2>
            <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 font-mono text-[10px] text-emerald-400 border border-emerald-500/20">
              Live Trace
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">Reasoning Trace · Function Calling · 状态同步</p>
        </div>
        <div className="font-mono text-xs text-slate-500 bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800">
          {events.length} events
        </div>
      </header>

      {/* 核心修改：overflow-y-auto 确保只有内部日志区域上下滚动，且有美观的滚动条 */}
      <div className="flex-1 space-y-3 overflow-y-auto p-4 font-mono text-[12px] scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
        {events.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-center py-16 text-slate-500">
            <div className="w-8 h-8 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center mb-2 animate-pulse">
              🔍
            </div>
            <p>等待 Agent 工作流触发…</p>
            <p className="text-[11px] text-slate-600 mt-1">输入出行需求后将实时展示推理链路</p>
          </div>
        )}

        {events.map((event, index) => {
          const style = TONE[event.type] || { badge: "bg-slate-800 text-slate-300 border-slate-700", border: "border-slate-800", text: "text-slate-200", icon: "🔹" };
          return (
            <article 
              key={`${event.type}-${index}`} 
              className={`relative rounded-2xl border ${style.border} bg-slate-900/40 p-3.5 transition-all hover:bg-slate-900/70`}
            >
              <div className="flex items-center justify-between gap-3">
                <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-medium border ${style.badge}`}>
                  <span>{style.icon}</span>
                  <span>{event.type}</span>
                </span>
                <span className="rounded bg-slate-800/80 px-2 py-0.5 text-[11px] text-slate-400 font-mono">
                  @{event.node ?? "graph"}
                </span>
              </div>
              
              <p className={`mt-2 text-slate-300 leading-relaxed ${style.text}`}>
                {event.message}
              </p>

              {event.data && Object.keys(event.data).length > 0 && (
                <div className="mt-2.5 overflow-hidden rounded-xl bg-black/40 border border-slate-800/80 p-2.5">
                  <pre className="max-h-40 overflow-auto text-[11px] text-slate-400 font-mono scrollbar-thin">
                    {JSON.stringify(summarize(event.data), null, 2)}
                  </pre>
                </div>
              )}
            </article>
          );
        })}
      </div>
    </div>
  );
}

function summarize(data: Record<string, unknown>) {
  const clone: Record<string, unknown> = { ...data };
  if (typeof clone.result === "object" && clone.result) {
    clone.result = compact(clone.result);
  }
  if (typeof clone.itinerary === "object") {
    clone.itinerary = "{… itinerary summary …}";
  }
  return clone;
}

function compact(value: unknown) {
  try {
    const text = JSON.stringify(value);
    return text.length ? (text.length > 400 ? `${text.slice(0, 400)}…` : JSON.parse(text)) : value;
  } catch {
    return value;
  }
}