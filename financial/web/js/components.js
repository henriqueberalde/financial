import { h, s } from "./dom.js";
import { addMonths, monthLong } from "./format.js";

export function card({ title, hint, actions, span = false }, ...children) {
  return h("section", { className: span ? "card span-2" : "card" },
    h("div", { className: "card-header" },
      h("div", {}, h("h2", {}, title), hint ? h("div", { className: "hint" }, hint) : null),
      actions),
    children);
}

export function pageHeader(eyebrow, title, controls) {
  return h("header", { className: "page-header" },
    h("div", {}, h("div", { className: "eyebrow" }, eyebrow), h("h1", {}, title)),
    controls);
}

/** Month input with previous / next buttons, bounded by the data. */
export function monthPicker(month, period, onChange) {
  const step = (count) => {
    const next = addMonths(month, count);
    if (next >= period.first_month && next <= period.last_month) onChange(next);
  };

  return h("div", { className: "filters" },
    h("button", { className: "button", "aria-label": "Mês anterior",
                  disabled: month <= period.first_month, onClick: () => step(-1) }, "‹"),
    h("label", { className: "field" }, h("span", { className: "visually-hidden" }, "Mês"),
      h("input", { type: "month", value: month, min: period.first_month,
                   max: period.last_month,
                   onChange: (event) => event.target.value && onChange(event.target.value) })),
    h("button", { className: "button", "aria-label": "Próximo mês",
                  disabled: month >= period.last_month, onClick: () => step(1) }, "›"));
}

export function monthTitle(month) {
  const text = monthLong(month);
  return text[0].toUpperCase() + text.slice(1);
}

export function segmented(label, options, selected, onSelect) {
  return h("div", { className: "segmented", role: "group", "aria-label": label },
    options.map(([value, text]) => h("button", {
      className: "button", "aria-pressed": String(value === selected),
      onClick: () => onSelect(value),
    }, text)));
}

export function kpi({ label, value, change, footnote, trend, color }) {
  return h("section", { className: "card kpi" },
    h("span", { className: "kpi-label" }, label),
    h("span", { className: "kpi-value" }, value),
    h("div", { className: "kpi-footer" },
      h("span", { className: "kpi-delta" }, change ?? ""),
      trend ? sparkline(trend, color) : null),
    footnote ? h("span", { className: "hint" }, footnote) : null);
}

export function sparkline(values, color, width = 110, height = 30) {
  const known = values.filter((value) => value != null);
  if (known.length < 2) return null;

  const min = Math.min(...known);
  const range = Math.max(...known) - min || 1;
  const step = width / (values.length - 1);
  const points = values
    .map((value, index) => value == null ? null
      : `${(index * step).toFixed(1)},${(height - 3 - (value - min) / range * (height - 6)).toFixed(1)}`)
    .filter(Boolean)
    .join(" ");

  return s("svg", { width, height, viewBox: `0 0 ${width} ${height}`, "aria-hidden": "true" },
    s("polyline", { points, fill: "none", stroke: color, "stroke-width": 2,
                    "stroke-linejoin": "round", "stroke-linecap": "round" }));
}

export function tag(text, tone) {
  return h("span", { className: `tag ${tone}` }, text);
}

/** columns: [{ label, cell: (row) => node | text, className }] */
export function table(columns, rows, { onRowClick, emptyText = "Nada para mostrar." } = {}) {
  if (rows.length === 0) return empty(emptyText);

  return h("div", { className: "table-wrap" },
    h("table", {},
      h("thead", {}, h("tr", {}, columns.map((column) =>
        h("th", { className: column.className }, column.label)))),
      h("tbody", {}, rows.map((row) => h("tr", {
        className: onRowClick ? "clickable" : null,
        onClick: onRowClick ? () => onRowClick(row) : null,
      }, columns.map((column) => h("td", { className: column.className }, column.cell(row))))))));
}

/** Proportional bar with a legend; each item: { label, value, color, text, onClick } */
export function stackedBar(items) {
  const total = items.reduce((sum, item) => sum + item.value, 0);

  return [
    h("div", { className: "stacked", role: "img",
               "aria-label": items.map((item) => `${item.label}: ${item.text}`).join(", ") },
      items.map((item) => h("div", { style: {
        width: `${total ? item.value / total * 100 : 0}%`, background: item.color } }))),
    h("ul", { className: "legend-list" }, items.map((item) => h("li", {},
      h(item.onClick ? "button" : "div", { onClick: item.onClick },
        h("span", { className: "swatch", style: { background: item.color } }),
        h("span", { className: "label" }, item.label),
        h("span", { className: "num muted" }, item.text))))),
  ];
}

export function chart(className = "chart") {
  return h("div", { className });
}

export function empty(text) {
  return h("p", { className: "empty" }, text);
}

export function errorMessage(text) {
  return h("p", { className: "error", role: "alert" }, text);
}
