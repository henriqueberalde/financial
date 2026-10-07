const MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun",
                "jul", "ago", "set", "out", "nov", "dez"];
const MONTHS_LONG = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
                     "agosto", "setembro", "outubro", "novembro", "dezembro"];

const currency = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const compact = new Intl.NumberFormat("pt-BR", { notation: "compact", maximumFractionDigits: 1 });

export const UNCATEGORIZED = "Sem categoria";

export function brl(value) {
  return value == null ? "—" : currency.format(value);
}

export function brlCompact(value) {
  return value == null ? "—" : `R$ ${compact.format(value)}`;
}

export function percent(value, digits = 0) {
  if (value == null) return "—";
  return new Intl.NumberFormat("pt-BR", {
    style: "percent", maximumFractionDigits: digits,
  }).format(value);
}

/** "2026-10" → "out/26" */
export function monthLabel(month) {
  const [year, number] = month.split("-");
  return `${MONTHS[Number(number) - 1]}/${year.slice(2)}`;
}

/** "2026-10" → "outubro de 2026" */
export function monthLong(month) {
  const [year, number] = month.split("-");
  return `${MONTHS_LONG[Number(number) - 1]} de ${year}`;
}

export function calendarMonth(number) {
  return MONTHS[number - 1];
}

/** "2026-10-05" → "05/10/2026" */
export function dateLabel(date) {
  return date.split("-").reverse().join("/");
}

/** Sectors are named with an ordering prefix, as in "1 Essencial". */
export function sectorLabel(sector) {
  return sector.replace(/^\d+\s+/, "");
}

/** "2026-01" plus -2 months → "2025-11" */
export function addMonths(month, count) {
  const [year, number] = month.split("-").map(Number);
  const index = year * 12 + number - 1 + count;
  return `${Math.floor(index / 12)}-${String(index % 12 + 1).padStart(2, "0")}`;
}

/** Relative change of a value against its average, as "▲ 12%". */
export function change(value, average) {
  if (value == null || !average) return null;
  const ratio = value / average - 1;
  return `${ratio >= 0 ? "▲" : "▼"} ${percent(Math.abs(ratio))}`;
}

/** Difference of two rates in percentage points, as "▲ 6 p.p.". */
export function pointsChange(value, average) {
  if (value == null || average == null) return null;
  const points = Math.round((value - average) * 100);
  return `${points >= 0 ? "▲" : "▼"} ${Math.abs(points)} p.p.`;
}

/** For the chart tooltips, which are rendered as HTML. */
export function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (char) => `&#${char.charCodeAt(0)};`);
}
