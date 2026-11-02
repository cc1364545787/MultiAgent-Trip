import React from 'react';

const NODES = [
  { 
    id: "planner", 
    label: "规划者 (Planner)", 
    hint: "拆解用户自然语言意图，生成结构化子任务序列。",
    status: "已就绪" 
  },
  { 
    id: "executor", 
    label: "执行者 (Executor)", 
    hint: "并行调用搜索、天气 API、汇率换算与地图工具。",
    status: "等待调度" 
  },
  { 
    id: "validator", 
    label: "校验者 (Verifier)", 
    hint: "JSON 格式检查、边界值判定与自动重试反思。",
    status: "等待调度" 
  },
  { 
    id: "aggregator", 
    label: "主控汇总 (Master)", 
    hint: "有序合并多路数据，生成完整行程与预估预算。",
    status: "等待调度" 
  },
];

type Props = { activeNode: string | null; done: boolean };

export function WorkflowGraph({ activeNode, done }: Props) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/40 p-5 backdrop-blur-xl shadow-2xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono uppercase tracking-[0.2em] text-amber-300">
            ⚡ LANGGRAPH 工作流节点状态 (GRAPH TOPOLOGY)
          </span>
        </div>
        <div className="hidden sm:flex items-center gap-4 text-xs font-mono text-slate-400">
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-emerald-400"></span>规划者</span>
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-sky-400"></span>执行者</span>
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-violet-400"></span>校验者</span>
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-amber-400"></span>主控汇总</span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        {NODES.map((node, index) => {
          const active = activeNode === node.id;
          const passed =
            done ||
            (activeNode
              ? NODES.findIndex((item) => item.id === activeNode) > index
              : false);

          return (
            <div 
              key={node.id} 
              className={`relative rounded-2xl border p-4 transition-all duration-300 ${
                active
                  ? "border-amber-400 bg-amber-500/10 shadow-[0_0_25px_rgba(252,211,77,0.15)] ring-1 ring-amber-400/40"
                  : passed
                    ? "border-emerald-500/40 bg-emerald-500/5"
                    : "border-slate-800 bg-slate-950/60 hover:border-slate-700"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="rounded-md bg-slate-900 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-slate-300 border border-slate-800">
                  NODE {index + 1}
                </span>
                <span className={`text-[11px] font-mono px-2 py-0.5 rounded-full ${
                  active ? "bg-amber-400/20 text-amber-300 border border-amber-400/30" :
                  passed ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" :
                  "bg-slate-900 text-slate-500 border border-slate-800"
                }`}>
                  {active ? "⚡ 运行中" : passed ? "✓ 已完成" : "等待调度"}
                </span>
              </div>

              <div className="mt-3 font-semibold text-slate-100 text-sm flex items-center gap-2">
                {node.label}
              </div>
              <p className="mt-1.5 text-xs text-slate-400 leading-relaxed line-clamp-2">
                {node.hint}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}