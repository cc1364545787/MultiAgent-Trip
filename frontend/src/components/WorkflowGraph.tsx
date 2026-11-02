const NODES = [
  { id: "planner", label: "规划者", hint: "拆解意图" },
  { id: "executor", label: "执行者", hint: "并行工具" },
  { id: "validator", label: "校验者", hint: "格式/边界" },
  { id: "aggregator", label: "主控汇总", hint: "有序合并" },
];

type Props = { activeNode: string | null; done: boolean };

export function WorkflowGraph({ activeNode, done }: Props) {
  return (
    <div className="grid grid-cols-4 gap-3">
      {NODES.map((node, index) => {
        const active = activeNode === node.id;
        const passed =
          done ||
          (activeNode
            ? NODES.findIndex((item) => item.id === activeNode) > index
            : false);
        return (
          <div key={node.id} className="relative">
            <div
              className={`rounded-2xl border px-3 py-3 transition ${
                active
                  ? "border-amber-300 bg-amber-300/10 shadow-[0_0_24px_rgba(252,211,77,0.18)]"
                  : passed
                    ? "border-sky-400/40 bg-sky-400/10"
                    : "border-line bg-panel"
              }`}
            >
              <div className="text-[11px] uppercase tracking-[0.18em] text-slate-400">
                Node {index + 1}
              </div>
              <div className="mt-1 font-semibold">{node.label}</div>
              <div className="text-xs text-slate-400">{node.hint}</div>
            </div>
            {index < NODES.length - 1 && (
              <div className="pointer-events-none absolute -right-2 top-1/2 hidden h-px w-4 bg-slate-600 md:block" />
            )}
          </div>
        );
      })}
    </div>
  );
}
