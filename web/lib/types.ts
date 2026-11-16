export type Pct = { p10: number; p50: number; p90: number };

export type MoneyBlock = {
  revenue_at_risk: Pct;
  margin_impact: Pct;
  working_capital: Pct;
  write_off: Pct;
  penalty: Pct;
  extra_cost: Pct;
};

export type ServiceBlock = {
  fill_rate: Pct;
  critical_fill_rate: Pct;
  stockout_days: Pct;
  days_to_first_stockout: Pct;
  days_to_recover: Pct;
  unmet_critical_units: Pct;
  unmet_essential_units: Pct;
  unmet_other_units: Pct;
  expedite_units: Pct;
};

export type Summary = {
  money: MoneyBlock;
  service: ServiceBlock;
  daily_fill_p50: number[];
  daily_fill_p90: number[];
  stockouts_by_hospital: {
    site_id: number;
    name: string;
    region: string;
    critical: boolean;
    stockout_days: Pct;
  }[];
};

export type Plan = {
  id?: number;
  kind: string;
  levers: Record<string, number>;
  cost: number;
  recommended: boolean;
  explanation: {
    top_levers: { name: string; intensity: number }[];
    binding_constraints: string[];
    sensitivity: string;
  };
  summary: Summary;
  loss_avoided?: number;
  roi?: number;
};

export type TemplateParam = {
  name: string;
  label: string;
  unit: string;
  default: number | string;
  minimum?: number | null;
  maximum?: number | null;
  step?: number | null;
  is_live_slider?: boolean;
  choices?: string[] | null;
};

export type Template = {
  id: string;
  name: string;
  description: string;
  category: string;
  status: "live" | "coming_in_pilot";
  params: TemplateParam[];
  headline: string;
};

export type Site = {
  id: number;
  code: string;
  name: string;
  type: string;
  region: string;
  state: string;
  lat: number;
  lon: number;
  storage_classes: string[];
  recovery_days: number;
  is_critical_care: boolean;
  risk: "critical" | "high" | "medium" | "low";
  tts?: number | null;
  ttr?: number | null;
  exposure?: number | null;
};
