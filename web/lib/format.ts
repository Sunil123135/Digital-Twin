const CRORE = 10_000_000;
const LAKH = 100_000;

export function formatINR(value: number): string {
  if (!Number.isFinite(value)) return "—";
  const sign = value < 0 ? "-" : "";
  const abs = Math.abs(value);
  if (abs >= CRORE) {
    return `${sign}₹${trim(abs / CRORE)} cr`;
  }
  if (abs >= LAKH) {
    return `${sign}₹${trim(abs / LAKH)} L`;
  }
  return `${sign}₹${new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(abs)}`;
}

export function formatINRExact(value: number): string {
  if (!Number.isFinite(value)) return "—";
  const sign = value < 0 ? "-" : "";
  return `${sign}₹${new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(Math.abs(value))}`;
}

export function formatPct(value: number): string {
  if (!Number.isFinite(value)) return "—";
  const pct = value <= 1 ? value * 100 : value;
  return `${pct.toFixed(1)}%`;
}

export function formatDays(value: number): string {
  if (!Number.isFinite(value)) return "—";
  return `${value.toFixed(0)} days`;
}

function trim(value: number): string {
  return value.toFixed(1).replace(/\.0$/, ".0");
}
