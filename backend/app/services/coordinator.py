from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable

from app.models.plan import SubTask, ToolCallRecord
from app.services.validator import validate_tool_args
from app.tools.registry import execute_tool


class AgentCoordinator:
    """Fan-out subtasks through an asyncio queue, then fold results in seq order."""

    def __init__(self, workers: int = 4):
        self.workers = workers

    async def run(
        self,
        tasks: list[SubTask],
        context: dict[str, Any],
        on_event: Callable[[str, dict[str, Any]], Awaitable[None]] | None = None,
    ) -> list[ToolCallRecord]:
        task_queue: asyncio.Queue[SubTask | None] = asyncio.Queue()
        result_queue: asyncio.Queue[ToolCallRecord] = asyncio.Queue()

        for task in sorted(tasks, key=lambda item: item.seq):
            await task_queue.put(task)

        async def worker(worker_id: int) -> None:
            while True:
                item = await task_queue.get()
                if item is None:
                    task_queue.task_done()
                    break
                record = await self._execute_one(item, context, worker_id, on_event)
                await result_queue.put(record)
                task_queue.task_done()

        worker_jobs = [asyncio.create_task(worker(i)) for i in range(self.workers)]
        for _ in range(self.workers):
            await task_queue.put(None)
        await task_queue.join()
        for job in worker_jobs:
            await job

        collected: list[ToolCallRecord] = []
        while not result_queue.empty():
            collected.append(result_queue.get_nowait())

        collected.sort(key=lambda rec: rec.seq)
        seen: set[str] = set()
        unique: list[ToolCallRecord] = []
        for rec in collected:
            if rec.task_id in seen:
                continue
            seen.add(rec.task_id)
            unique.append(rec)
        return unique

    async def _execute_one(
        self,
        task: SubTask,
        context: dict[str, Any],
        worker_id: int,
        on_event: Callable[[str, dict[str, Any]], Awaitable[None]] | None,
    ) -> ToolCallRecord:
        check = validate_tool_args(task.tool, task.arguments, context)
        args = check.repaired
        retries = 0
        if on_event:
            await on_event(
                "tool_call",
                {
                    "worker": worker_id,
                    "task_id": task.id,
                    "tool": task.tool,
                    "arguments": args,
                    "validation": check.as_dict(),
                },
            )

        if not check.ok:
            return ToolCallRecord(
                task_id=task.id,
                seq=task.seq,
                tool=task.tool,
                arguments=args,
                ok=False,
                error="; ".join(check.errors),
                retries=retries,
            )

        last_error = None
        for attempt in range(3):
            try:
                result = await execute_tool(task.tool, args)
                record = ToolCallRecord(
                    task_id=task.id,
                    seq=task.seq,
                    tool=task.tool,
                    arguments=args,
                    result=result,
                    ok=True,
                    retries=retries,
                )
                if on_event:
                    await on_event(
                        "tool_result",
                        {
                            "worker": worker_id,
                            "task_id": task.id,
                            "tool": task.tool,
                            "ok": True,
                            "result": result,
                            "retries": retries,
                        },
                    )
                return record
            except Exception as exc:  # noqa: BLE001 - tool boundary
                last_error = str(exc)
                retries = attempt + 1
                if on_event:
                    await on_event(
                        "retry",
                        {
                            "task_id": task.id,
                            "tool": task.tool,
                            "attempt": retries,
                            "error": last_error,
                        },
                    )
                await asyncio.sleep(0.15 * retries)

        return ToolCallRecord(
            task_id=task.id,
            seq=task.seq,
            tool=task.tool,
            arguments=args,
            ok=False,
            error=last_error,
            retries=retries,
        )
