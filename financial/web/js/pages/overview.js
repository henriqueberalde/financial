import { api } from "../api.js";
import { balanceChart, COLORS, flowChart, sectorPalette } from "../charts.js";
import { card, chart, empty, kpi, monthPicker, monthTitle, pageHeader,
         stackedBar, tag } from "../components.js";
import { h } from "../dom.js";
import { brl, change, monthLabel, percent, pointsChange, sectorLabel } from "../format.js";
import { go, link } from "../navigation.js";

export async function render(params, { period, categories }) {
  const month = params.get("month") ?? period.default_month;
  const overview = await api.get("/overview", { month });
  const colorOf = sectorPalette(categories.map((category) => category.sector));
  const flowChartElement = chart("chart tall");
  const balanceElement = chart();
  const spendingOf = (month) => ({ start: month, end: month });

  return {
    content: [
      pageHeader("Visão geral", monthTitle(month),
                 monthPicker(month, period, (next) => go("overview", { month: next }))),
      h("div", { className: "grid kpis" }, indicators(overview)),
      h("div", { className: "grid" },
        card({ title: "Receitas x despesas por mês", span: true,
               hint: "Sem investimentos, viagens e projetos. Clique num mês para ver os gastos dele" },
             flowChartElement),
        card({ title: "Alertas", hint: "O que merece atenção no mês" }, alerts(overview))),
      h("div", { className: "grid" },
        card({ title: "Saldo da conta corrente", hint: "Fim de cada dia, nos últimos 12 meses" },
             overview.balance.length ? balanceElement : empty("Sem saldo no período.")),
        card({ title: "Despesas do mês por setor" },
             overview.sectors.length
               ? stackedBar(overview.sectors.map((sector) => ({
                 label: sectorLabel(sector.sector),
                 value: sector.value,
                 color: colorOf(sector.sector),
                 text: `${percent(sector.share)} · ${brl(sector.value)}`,
                 onClick: () => go("spending", { ...spendingOf(month), sector: sector.sector }),
               })))
               : empty("Sem despesas no mês."))),
    ],
    charts: [
      {
        element: flowChartElement,
        option: flowChart(overview.flow.map((item) => monthLabel(item.month)), overview.flow),
        onAxisClick: (index) => go("spending", spendingOf(overview.flow[index].month)),
      },
      ...(overview.balance.length
        ? [{ element: balanceElement, option: balanceChart(overview.balance) }] : []),
    ],
  };
}

function indicators({ income, expense, result, savings_rate: rate }) {
  const footnote = "vs média dos 12 meses anteriores";
  return [
    kpi({ label: "Receita", value: brl(income.value), footnote,
          change: change(income.value, income.average), trend: income.trend, color: COLORS.income }),
    kpi({ label: "Despesa", value: brl(expense.value), footnote,
          change: change(expense.value, expense.average), trend: expense.trend, color: COLORS.expense }),
    kpi({ label: "Resultado", value: brl(result.value), footnote,
          change: change(result.value, result.average), trend: result.trend, color: COLORS.result }),
    kpi({ label: "Taxa de poupança", value: percent(rate.value), footnote,
          change: pointsChange(rate.value, rate.average), trend: rate.trend, color: COLORS.result }),
  ];
}

const ALERTS = {
  above_average: (alert, month) => ({
    tag: tag("Acima da média", "warning"),
    title: `${alert.subject}: ${brl(alert.value)}`,
    detail: `${change(alert.value, alert.reference)} vs média de ${brl(alert.reference)}`,
    href: link("spending", { start: month, end: month, category: alert.subject }),
  }),
  new: (alert, month) => ({
    tag: tag("Recorrente novo", "info"),
    title: alert.subject,
    detail: `${brl(alert.value)} no mês`,
    href: link("recurring", { month }),
  }),
  price_increase: (alert, month) => ({
    tag: tag("Subiu de preço", "warning"),
    title: alert.subject,
    detail: `${brl(alert.reference)} → ${brl(alert.value)}`,
    href: link("recurring", { month }),
  }),
  uncategorized_share: (alert, month) => ({
    tag: tag("Dados", "neutral"),
    title: `${percent(alert.value)} das despesas sem categoria`,
    detail: `Meta: abaixo de ${percent(alert.reference)}`,
    href: link("data", { month }),
  }),
};

function alerts(overview) {
  if (overview.alerts.length === 0) return empty("Nada fora do normal neste mês.");

  return h("ul", { className: "alerts" }, overview.alerts.map((alert) => {
    const item = ALERTS[alert.kind](alert, overview.month);
    return h("li", {}, item.tag,
      h("a", { href: item.href }, h("strong", {}, item.title),
        h("span", { className: "hint" }, item.detail)));
  }));
}
