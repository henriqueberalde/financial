import { api } from "../api.js";
import { COLORS, sectorPalette, timelineChart, treemapChart } from "../charts.js";
import { card, categoryOptions, chart, empty, errorMessage, pageHeader, segmented,
         table } from "../components.js";
import { h } from "../dom.js";
import { addMonths, brl, dateLabel, monthLabel, sectorLabel, UNCATEGORIZED } from "../format.js";
import { go, refresh } from "../navigation.js";

const DRILL = ["sector", "category", "merchant"];
const KEYS = ["start", "end", "source", ...DRILL, "granularity", "search", "page"];
const PAGE_SIZE = 20;
const SOURCES = [["", "Conta e cartão"], ["account", "Conta"], ["card", "Cartão"]];
const GRANULARITIES = [["year", "Ano"], ["month", "Mês"], ["day", "Dia"]];

export async function render(params, { period, categories }) {
  const state = Object.fromEntries(KEYS.map((key) => [key, params.get(key)]));
  if (state.category && !state.sector) state.sector = sectorOf(state.category, categories);
  state.end ??= period.default_month;
  state.start ??= addMonths(state.end, -11);
  state.granularity ??= "month";
  const page = Number(state.page ?? 0);

  const filter = { start: state.start, end: state.end, source: state.source,
                   sector: state.sector, category: state.category, merchant: state.merchant };
  const [tree, timeline, merchants, transactions] = await Promise.all([
    api.get("/spending/tree", filter),
    api.get("/spending/timeline", { ...filter, granularity: state.granularity }),
    api.get("/spending/merchants", filter),
    api.get("/transactions", { ...filter, search: state.search, limit: PAGE_SIZE,
                               offset: page * PAGE_SIZE }),
  ]);

  const update = (changes) => go("spending", { ...state, page: null, ...changes });
  const drillTo = (path) => update(Object.fromEntries(
    DRILL.map((key, index) => [key, path[index] ?? null])));
  const levels = DRILL.map((key) => state[key]);
  const depth = state.sector ? (state.category ? 2 : 1) : 0;
  const colorOf = sectorPalette(categories.map((category) => category.sector));

  const treeElement = chart("chart tall");
  const timelineElement = chart();
  const visible = visibleNodes(tree, levels.slice(0, depth), colorOf);
  const title = state.merchant ?? state.category ?? (state.sector && sectorLabel(state.sector))
    ?? "Todas as despesas";

  return {
    content: [
      pageHeader(`Gastos · ${monthLabel(state.start)} a ${monthLabel(state.end)}`,
                 [title, " ", h("span", { className: "num muted" }, brl(transactions.amount))]),
      filters(state, period, update),
      breadcrumb(levels, drillTo),
      h("div", { className: "grid" },
        card({ title: "Despesas por setor, categoria e estabelecimento", span: true,
               hint: "Clique para descer um nível" },
             visible.length ? treeElement : empty("Sem despesas no período.")),
        card({ title: "Estabelecimentos" }, merchantBars(merchants, update))),
      card({ title: "Ao longo do tempo",
             hint: `Média ${brl(timeline.average)} · clique numa barra para detalhar`,
             actions: segmented("Granularidade", GRANULARITIES, state.granularity,
                                (granularity) => update({ granularity })) },
           timelineElement),
      card({ title: "Transações", hint: `${transactions.total} despesas`,
             actions: searchBox(state.search, (search) => update({ search })) },
           transactionTable(transactions.items, categories),
           pager(page, transactions.total, (next) => go("spending", { ...state, page: next }))),
    ],
    charts: [
      ...(visible.length ? [{
        element: treeElement,
        option: treemapChart(visible),
        onClick: (event) => {
          const path = event.treePathInfo.slice(1).map((node) => node.name);
          if (!event.data.other) drillTo([...levels.slice(0, depth), ...path].slice(0, 3));
        },
      }] : []),
      {
        element: timelineElement,
        option: timelineChart(timeline.points.map((point) => periodLabel(point.period)),
                              timeline.points.map((point) => point.value), timeline.average,
                              state.sector ? colorOf(state.sector) : COLORS.expense),
        onAxisClick: (index) => drillTime(timeline.points[index].period, update),
      },
    ],
  };
}

function sectorOf(category, categories) {
  return categories.find((candidate) => candidate.name === category)?.sector ?? UNCATEGORIZED;
}

/** The tree below the drilled sector and category, two levels deep. */
function visibleNodes(tree, path, colorOf) {
  let nodes = tree;
  let sector = null;
  for (const name of path) {
    const node = nodes.find((candidate) => candidate.name === name);
    sector ??= node?.name;
    nodes = node?.children ?? [];
  }

  return nodes.map((node) => ({
    name: node.name,
    value: node.value,
    other: node.other,
    itemStyle: { color: colorOf(sector ?? node.name) },
    children: node.children.map((child) => ({ name: child.name, value: child.value,
                                              other: child.other })),
  }));
}

function filters(state, period, update) {
  const year = state.end.slice(0, 4);
  const presets = [
    [`${addMonths(period.default_month, -11)}|${period.default_month}`, "12 meses"],
    [`${year}-01|${year}-12`, `Ano ${year}`],
    [`${year - 1}-01|${year - 1}-12`, `Ano ${year - 1}`],
  ];
  const monthInput = (label, key) => h("label", { className: "field" }, label,
    h("input", { type: "month", value: state[key], min: period.first_month,
                 max: period.last_month,
                 onChange: (event) => event.target.value && update({ [key]: event.target.value }) }));

  return h("div", { className: "filters", role: "group", "aria-label": "Filtros" },
    segmented("Período", presets, `${state.start}|${state.end}`, (value) => {
      const [start, end] = value.split("|");
      update({ start, end });
    }),
    monthInput("De", "start"),
    monthInput("Até", "end"),
    h("label", { className: "field" }, "Origem",
      h("select", { onChange: (event) => update({ source: event.target.value || null }) },
        SOURCES.map(([value, text]) => h("option", { value, selected: (state.source ?? "") === value },
                                         text)))));
}

function breadcrumb(levels, drillTo) {
  const items = [{ label: "Todas as despesas", path: [] }];
  levels.forEach((name, index) => {
    if (name) items.push({ label: index === 0 ? sectorLabel(name) : name,
                           path: levels.slice(0, index + 1) });
  });

  return h("nav", { className: "breadcrumb", "aria-label": "Caminho do detalhamento" },
    items.map((item, index) => {
      const element = index === items.length - 1
        ? h("span", { className: "current", "aria-current": "location" }, item.label)
        : h("button", { onClick: () => drillTo(item.path) }, item.label);
      return index ? [h("span", { className: "muted" }, "›"), element] : element;
    }));
}

function merchantBars(merchants, update) {
  if (merchants.length === 0) return empty("Sem despesas no período.");

  const top = merchants[0].total;
  return h("ul", { className: "bars" }, merchants.map((merchant) => h("li", {},
    h("button", { onClick: () => update({ merchant: merchant.name }) },
      h("span", { className: "row" },
        h("span", {}, merchant.name, h("span", { className: "muted" }, ` · ${merchant.count}x`)),
        h("span", { className: "num" }, brl(merchant.total))),
      h("span", { className: "track" },
        h("span", { className: "fill", style: { display: "block",
                                                width: `${merchant.total / top * 100}%` } }))))));
}

function periodLabel(period) {
  if (period.length === 7) return monthLabel(period);
  if (period.length === 10) return period.slice(8);
  return period;
}

/** Year → its months; month → its days. */
function drillTime(period, update) {
  if (period.length === 4) update({ start: `${period}-01`, end: `${period}-12`, granularity: "month" });
  if (period.length === 7) update({ start: period, end: period, granularity: "day" });
}

function searchBox(search, onSearch) {
  return h("form", { className: "filters", role: "search",
                     onSubmit: (event) => {
                       event.preventDefault();
                       onSearch(new FormData(event.target).get("search") || null);
                     } },
    h("label", { className: "field" }, h("span", { className: "visually-hidden" }, "Buscar"),
      h("input", { type: "search", name: "search", value: search ?? "",
                   placeholder: "Buscar na descrição" })),
    h("button", { className: "button", type: "submit" }, "Buscar"));
}

function transactionTable(items, categories) {
  return table([
    { label: "Data", className: "num muted", cell: (row) => dateLabel(row.date) },
    { label: "Descrição", className: "wrap", cell: (row) => row.description },
    { label: "Origem", className: "muted", cell: (row) => row.source === "card" ? "Cartão" : "Conta" },
    { label: "Categoria", cell: (row) => categorySelect(row, categories) },
    { label: "Valor", className: "num right", cell: (row) => brl(row.amount) },
  ], items, { emptyText: "Nenhuma despesa encontrada." });
}

function categorySelect(row, categories) {
  const status = h("span", { className: "visually-hidden", role: "status" });

  const select = h("select", {
    "aria-label": `Categoria de ${row.description}`,
    onChange: async (event) => {
      select.disabled = true;
      try {
        await api.put(`/transactions/${row.id}/category`, { category_id: Number(event.target.value) });
        refresh();
      } catch (error) {
        select.disabled = false;
        status.replaceWith(errorMessage(error.message));
      }
    },
  },
  row.category_id == null ? h("option", { value: "", selected: true, disabled: true }, UNCATEGORIZED) : null,
  categoryOptions(categories, row.category_id));

  return [select, status];
}

function pager(page, total, onPage) {
  const pages = Math.ceil(total / PAGE_SIZE);
  if (pages <= 1) return null;

  return h("div", { className: "pager" },
    h("button", { className: "button small", disabled: page === 0, onClick: () => onPage(page - 1) },
      "Anterior"),
    h("span", { className: "muted" }, `Página ${page + 1} de ${pages}`),
    h("button", { className: "button small", disabled: page >= pages - 1,
                  onClick: () => onPage(page + 1) }, "Próxima"));
}
