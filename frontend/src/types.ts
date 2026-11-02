export type EventType =
  | "run_started"
  | "status"
  | "node_start"
  | "node_end"
  | "reasoning"
  | "plan"
  | "tool_call"
  | "tool_result"
  | "validation"
  | "retry"
  | "itinerary"
  | "error"
  | "done"
  | "close";

export type StreamEvent = {
  type: EventType;
  node?: string | null;
  message: string;
  data?: Record<string, unknown>;
};

export type Activity = {
  time: string;
  title: string;
  detail: string;
  cost_cny: number;
};

export type DayPlan = {
  day: number;
  date: string;
  city: string;
  theme: string;
  weather: string;
  activities: Activity[];
  estimated_cost_cny: number;
};

export type Itinerary = {
  destination: string;
  days: number;
  budget_cny: number;
  currency_note: string;
  weather_summary: string;
  days_plan: DayPlan[];
  tips: string[];
  total_estimated_cny: number;
  within_budget: boolean;
};

export type SubTask = {
  id: string;
  seq: number;
  type: string;
  title: string;
  tool: string;
  arguments: Record<string, unknown>;
};
