import { api } from "../api.js";
import { COLORS, divergingChart, seasonalityChart } from "../charts.js";
import { card, chart, empty, kpi, monthPicker, monthTitle, pageHeader, sparkline, table,
         tag } from "../components.js";
import { h } from "../dom.js";
import { addMonths, brl, calendarMonth, dateLabel, monthLabel, percent } from "../format.js";
import { go } from "../navigation.js";

const VARIANCE_ITEMS = 12;
const LARGEST_ITEMS = 10;
const STATUS = {
  new: () => tag("Novo", "info"),
  price_increase: () => tag("Subiu de preço", "warning"),
};

export async function render(params, { period }) {
  const month = params.get("month") ?? period.default_month;
  const start = addMonths(month, -11);
  const [recurring, variance, seasonality, largest] = await Promise.all([
    api.get("/recurring", { month }),
    api.get("/category-variance", { month }),
    api.get("/seasonality"),
    api.get("/largest-expenses", { start, end: month, limit: LARGEST_ITEMS }),
  ]);

  const varianceItems = variance.filter((item) => item.difference !== 0).slice(0, VARIANCE_ITEMS);
  const varianceElement = chart("chart tall");
  const seasonalityElement = chart("chart short");
  const count = (status) => recurring.items.filter((item) => item.status === status).length;

  return {
    content: [
      pageHeader(`Recorrentes e anomalias · ${monthLabel(start)} a ${monthLabel(month)}`,
                 monthTitle(month),
                 monthPicker(month, period, (next) => go("recurring", { month: next }))),
      h("div", { className: "grid kpis" },
        kpi({ label: "Custo recorrente mensal", value: brl(recurring.monthly_cost),
              footnote: `${percent(recurring.income_share)} da receita média` }),
        kpi({ label: "Gastos recorrentes", value: String(recurring.items.length),
              footnote: "em pelo menos 6 dos últimos 12 meses" }),
        kpi({ label: "Recorrentes novos", value: String(count("new")),
              footnote: "em todos os últimos 3 meses, e só neles" }),
        kpi({ label: "Aumentos de preço", value: String(count("price_increase")),
              footnote: "valor estável que subiu no último mês" })),
      card({ title: "Gastos recorrentes", hint: "Clique para ver as transações" },
           recurringTable(recurring, start, month)),
      h("div", { className: "grid" },
        card({ title: "Este mês vs média por categoria",
               hint: "Maiores diferenças primeiro · laranja gastou mais, azul gastou menos" },
             varianceItems.length ? varianceElement : empty("Sem despesas para comparar.")),
        card({ title: "Maiores despesas", hint: "Nos últimos 12 meses" }, largestTable(largest))),
      card({ title: "Sazonalidade",
             hint: "Despesa média de cada mês do ano, só nos meses com dados" },
           seasonalityElement),
    ],
    charts: [
      ...(varianceItems.length ? [{
        element: varianceElement,
        option: divergingChart(varianceItems),
        onClick: (event) => go("spending", {
          start: month, end: month, category: varianceItems.at(-1 - event.dataIndex).category,
        }),
      }] : []),
      {
        element: seasonalityElement,
        option: seasonalityChart(seasonality.map((item) => calendarMonth(item.month)), seasonality),
      },
    ],
  };
}

function recurringTable(recurring, start, end) {
  return table([
    { label: "Estabelecimento", cell: (item) => h("strong", {}, item.merchant) },
    { label: "Categoria", className: "muted", cell: (item) => item.category },
    { label: "Meses", className: "num", cell: (item) => `${item.months}/12` },
    { label: `${monthLabel(recurring.months[0])} a ${monthLabel(recurring.months.at(-1))}`,
      cell: (item) => sparkline(item.monthly, COLORS.income, 96, 24) },
    { label: "Média/mês", className: "num right", cell: (item) => brl(item.average) },
    { label: "Último mês", className: "num right", cell: (item) => brl(item.last) },
    { label: "", cell: (item) => STATUS[item.status]?.() },
  ], recurring.items, {
    emptyText: "Nenhum gasto recorrente no período.",
    onRowClick: (item) => go("spending", {
      start, end, category: item.category, merchant: item.merchant,
    }),
  });
}

function largestTable(expenses) {
  return table([
    { label: "Data", className: "num muted", cell: (expense) => dateLabel(expense.date) },
    { label: "Descrição", className: "wrap", cell: (expense) => expense.description },
    { label: "Categoria", className: "muted", cell: (expense) => expense.category },
    { label: "Valor", className: "num right", cell: (expense) => brl(expense.amount) },
  ], expenses);
}
