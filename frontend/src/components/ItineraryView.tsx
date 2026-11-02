import type { Itinerary } from "../types";

type Props = { itinerary: Itinerary | null; running: boolean };

export function ItineraryView({ itinerary, running }: Props) {
  if (!itinerary) {
    return (
      <section className="rounded-3xl border border-dashed border-line bg-panel/40 p-8 text-slate-400">
        {running ? "正在生成完整行程方案…" : "提交需求后，这里会展示逐日行程、花费与天气。"}
      </section>
    );
  }

  return (
    <section className="space-y-4">
      <div className="rounded-3xl border border-line bg-panel/80 p-5">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-amber-200">Complete Plan</p>
            <h2 className="mt-1 text-2xl font-semibold">
              {itinerary.destination} · {itinerary.days} 日行程
            </h2>
          </div>
          <div className={`rounded-full px-3 py-1 text-sm ${itinerary.within_budget ? "bg-emerald-400/15 text-emerald-200" : "bg-rose-400/15 text-rose-200"}`}>
            预估 ¥{itinerary.total_estimated_cny} / 预算 ¥{itinerary.budget_cny}
          </div>
        </div>
        <p className="mt-3 text-sm text-slate-300">{itinerary.weather_summary}</p>
        <p className="mt-1 text-sm text-slate-400">{itinerary.currency_note}</p>
      </div>

      <div className="space-y-3">
        {itinerary.days_plan.map((day) => (
          <article key={day.day} className="rounded-3xl border border-line bg-panel/70 p-5">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h3 className="text-lg font-semibold">
                D{day.day} {day.city} · {day.theme}
              </h3>
              <span className="text-sm text-slate-400">
                {day.date} · ¥{day.estimated_cost_cny}
              </span>
            </div>
            <p className="mt-1 text-sm text-sky-200/80">{day.weather}</p>
            <ul className="mt-3 space-y-2">
              {day.activities.map((activity, index) => (
                <li key={`${day.day}-${index}`} className="grid grid-cols-[64px_1fr_auto] gap-3 text-sm">
                  <span className="text-amber-200">{activity.time}</span>
                  <span>
                    <span className="font-medium">{activity.title}</span>
                    <span className="block text-slate-400">{activity.detail}</span>
                  </span>
                  <span className="text-slate-500">¥{activity.cost_cny}</span>
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>

      {itinerary.tips.length > 0 && (
        <div className="rounded-3xl border border-line bg-panel/70 p-5">
          <h3 className="font-semibold">实用提示</h3>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-300">
            {itinerary.tips.map((tip) => (
              <li key={tip}>{tip}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
