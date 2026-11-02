import React from 'react';
import type { Itinerary } from "../types";

type Props = { itinerary: Itinerary | null; running: boolean };

export function ItineraryView({ itinerary, running }: Props) {
  if (!itinerary) {
    return (
      <section className="flex flex-col items-center justify-center rounded-3xl border border-dashed border-slate-800 bg-slate-900/30 p-12 text-center text-slate-400">
        {running ? (
          <div className="space-y-3">
            <div className="inline-block h-6 w-6 animate-spin rounded-full border-2 border-amber-400 border-t-transparent" />
            <p className="text-sm font-medium text-amber-200">多 Agent 正在协同生成完整行程方案…</p>
          </div>
        ) : (
          <p className="text-sm">提交需求后，这里将以结构化卡片展示逐日行程、动态预算与气象数据。</p>
        )}
      </section>
    );
  }

  return (
    <section className="space-y-4">
      {/* 头部总览卡片 */}
      <div className="relative overflow-hidden rounded-3xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900/90 to-slate-950 p-6 shadow-xl">
        <div className="absolute right-0 top-0 -mt-4 -mr-4 h-32 w-32 rounded-full bg-amber-500/10 blur-2xl pointer-events-none" />
        
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded-full bg-amber-400/10 px-2.5 py-0.5 text-xs font-mono uppercase tracking-[0.2em] text-amber-300 border border-amber-400/20">
                Complete Plan
              </span>
            </div>
            <h2 className="mt-2 text-2xl font-bold tracking-tight text-slate-100">
              {itinerary.destination} · {itinerary.days} 日深度行程
            </h2>
          </div>
          
          <div className={`flex items-center gap-2 rounded-2xl px-4 py-2 text-sm font-medium border shadow-inner ${
            itinerary.within_budget 
              ? "bg-emerald-500/10 text-emerald-300 border-emerald-500/30" 
              : "bg-rose-500/10 text-rose-300 border-rose-500/30"
          }`}>
            <span>预估 ¥{itinerary.total_estimated_cny}</span>
            <span className="text-slate-500">/</span>
            <span className="text-slate-400">预算 ¥{itinerary.budget_cny}</span>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2 pt-4 border-t border-slate-800/80 text-sm">
          <div className="flex items-center gap-2 text-slate-300">
            <span>🌤️</span>
            <span>{itinerary.weather_summary}</span>
          </div>
          <div className="flex items-center gap-2 text-slate-400">
            <span>💱</span>
            <span>{itinerary.currency_note}</span>
          </div>
        </div>
      </div>

      {/* 逐日行程列表 */}
      <div className="space-y-4">
        {itinerary.days_plan.map((day) => (
          <article key={day.day} className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 shadow-lg backdrop-blur transition hover:border-slate-700">
            <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-slate-800/60 pb-3">
              <div className="flex items-center gap-3">
                <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-amber-400/10 font-mono text-xs font-bold text-amber-300 border border-amber-400/20">
                  D{day.day}
                </span>
                <h3 className="text-lg font-semibold text-slate-100">
                  {day.city} · {day.theme}
                </h3>
              </div>
              <div className="flex items-center gap-3 text-sm font-mono text-slate-400">
                <span>{day.date}</span>
                <span className="text-slate-600">|</span>
                <span className="text-amber-300 font-medium">¥{day.estimated_cost_cny}</span>
              </div>
            </div>

            <p className="mt-3 text-xs text-sky-300/90 font-mono flex items-center gap-1.5">
              <span>⛅</span> {day.weather}
            </p>

            <ul className="mt-4 space-y-3">
              {day.activities.map((activity, index) => (
                <li key={`${day.day}-${index}`} className="grid grid-cols-[72px_1fr_auto] items-start gap-4 text-sm rounded-2xl p-2.5 transition hover:bg-slate-800/40">
                  <span className="font-mono text-xs font-semibold text-amber-300/90 pt-0.5">
                    {activity.time}
                  </span>
                  <div>
                    <span className="font-medium text-slate-200">{activity.title}</span>
                    <span className="mt-0.5 block text-xs text-slate-400 leading-relaxed">{activity.detail}</span>
                  </div>
                  <span className="font-mono text-xs text-slate-400 pt-0.5">
                    ¥{activity.cost_cny}
                  </span>
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>

      {/* 实用提示 */}
      {itinerary.tips.length > 0 && (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/40 p-6">
          <h3 className="font-semibold text-slate-200 flex items-center gap-2">
            <span>💡</span> 智能出行提示
          </h3>
          <ul className="mt-3 space-y-2 text-sm text-slate-300">
            {itinerary.tips.map((tip) => (
              <li key={tip} className="flex items-start gap-2 text-slate-400">
                <span className="text-amber-400 mt-1">▪</span>
                <span>{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}