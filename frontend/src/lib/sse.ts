import type { StreamEvent } from "../types";

export async function streamPlan(
  query: string,
  onEvent: (event: StreamEvent) => void,
  signal?: AbortSignal
) {
  const response = await fetch("/api/plan/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({ query }),
    signal,
  });
  if (!response.ok || !response.body) {
    throw new Error(`请求失败 (${response.status})`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() ?? "";
    for (const chunk of chunks) {
      const line = chunk.split("\n").find((item) => item.startsWith("data:"));
      if (!line) continue;
      const payload = line.slice(5).trim();
      if (!payload) continue;
      const event = JSON.parse(payload) as StreamEvent;
      if (event.type === "close") return;
      onEvent(event);
    }
  }
}
