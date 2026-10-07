import { brl, brlCompact, escapeHtml, UNCATEGORIZED } from "./format.js";

export const COLORS = {
  income: "#2a78d6",
  expense: "#eb6834",
  result: "#0b0b0b",
  neutral: "#b5b3ad",
  axis: "#d9d8d3",
  grid: "#ecebe7",
  ink: "#52514e",
};

// Validated categorical order (fixed, never cycled); one hue per sector
const CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"];

const mounted = new Set();

/** Sector colors follow the sector, not its rank in the current data. */
export function sectorPalette(sectors) {
  const named = [...new Set(sectors)].filter((sector) => sector !== UNCATEGORIZED).sort();
  const palette = new Map(named.map((sector, index) =>
    [sector, CATEGORICAL[index] ?? COLORS.neutral]));
  palette.set(UNCATEGORIZED, COLORS.neutral);
  return (sector) => palette.get(sector) ?? COLORS.neutral;
}

/**
 * onClick receives the clicked mark; onAxisClick the index of the clicked
 * category column, so a click anywhere in the column counts, not only on
 * its bar.
 */
export function mount(element, option, { onClick, onAxisClick } = {}) {
  const chart = echarts.init(element, null, { renderer: "svg", locale: "PT-br" });
  chart.setOption({ ...BASE, ...option });
  if (onClick) chart.on("click", onClick);
  if (onAxisClick) {
    chart.getZr().on("click", ({ offsetX, offsetY }) => {
      if (!chart.containPixel("grid", [offsetX, offsetY])) return;
      const [index] = chart.convertFromPixel({ seriesIndex: 0 }, [offsetX, offsetY]);
      if (index >= 0) onAxisClick(index);
    });
  }

  const observer = new ResizeObserver(() => chart.resize());
  observer.observe(element);
  mounted.add({ chart, observer });
}

export function disposeAll() {
  for (const { chart, observer } of mounted) {
    observer.disconnect();
    chart.dispose();
  }
  mounted.clear();
}

const BASE = {
  textStyle: { fontFamily: "IBM Plex Sans, system-ui, sans-serif", color: COLORS.ink },
  grid: { left: 8, right: 16, top: 16, bottom: 8, containLabel: true },
  tooltip: {
    trigger: "axis",
    valueFormatter: brl,
    axisPointer: { type: "shadow", shadowStyle: { color: "rgba(11,11,11,0.04)" } },
  },
  animationDuration: 300,
};

const valueAxis = {
  type: "value",
  axisLabel: { formatter: brlCompact, color: COLORS.ink },
  splitLine: { lineStyle: { color: COLORS.grid } },
};

function categoryAxis(labels) {
  return {
    type: "category",
    data: labels,
    axisLine: { lineStyle: { color: COLORS.axis } },
    axisTick: { show: false },
    axisLabel: { color: COLORS.ink },
  };
}

function bar(name, values, color, extra = {}) {
  return {
    type: "bar",
    name,
    data: values,
    itemStyle: { color, borderRadius: [4, 4, 0, 0] },
    barMaxWidth: 18,
    emphasis: { focus: "none", itemStyle: { opacity: 0.85 } },
    ...extra,
  };
}

function averageLine(value, label) {
  return {
    silent: true,
    symbol: "none",
    lineStyle: { color: COLORS.ink, type: "dashed", width: 1.5 },
    label: { formatter: label, position: "insideEndTop", color: COLORS.ink },
    data: [{ yAxis: value }],
  };
}

export function flowChart(labels, flow) {
  return {
    legend: { top: 0, left: 0, icon: "roundRect", itemWidth: 12, itemHeight: 8 },
    grid: { ...BASE.grid, top: 36 },
    xAxis: categoryAxis(labels),
    yAxis: valueAxis,
    series: [
      bar("Receita", flow.map((month) => month.income), COLORS.income),
      bar("Despesa", flow.map((month) => month.expense), COLORS.expense),
      {
        type: "line",
        name: "Resultado",
        data: flow.map((month) => month.result),
        lineStyle: { color: COLORS.result, width: 2 },
        itemStyle: { color: COLORS.result },
        symbolSize: 8,
      },
    ],
  };
}

export function balanceChart(points) {
  return {
    tooltip: { ...BASE.tooltip, axisPointer: { type: "line" } },
    xAxis: { type: "time", axisLine: { lineStyle: { color: COLORS.axis } },
             splitLine: { show: false }, axisLabel: { color: COLORS.ink } },
    yAxis: valueAxis,
    series: [{
      type: "line",
      name: "Saldo",
      data: points.map((point) => [point.date, point.balance]),
      showSymbol: false,
      lineStyle: { color: COLORS.income, width: 2 },
      itemStyle: { color: COLORS.income },
      areaStyle: { color: COLORS.income, opacity: 0.08 },
    }],
  };
}

export function timelineChart(labels, values, average, color) {
  return {
    xAxis: categoryAxis(labels),
    yAxis: valueAxis,
    series: [bar("Despesa", values, color, {
      barMaxWidth: 28,
      markLine: averageLine(average, "média"),
    })],
  };
}

export function treemapChart(nodes) {
  return {
    tooltip: {
      trigger: "item",
      formatter: (item) => escapeHtml(item.treePathInfo.slice(1).map((node) => node.name).join(" › "))
        + `<br><strong>${brl(item.value)}</strong>`,
    },
    series: [{
      type: "treemap",
      data: nodes,
      nodeClick: false,
      roam: false,
      breadcrumb: { show: false },
      width: "100%",
      height: "100%",
      // Dark text keeps contrast over every sector hue and the neutral gray
      label: { color: COLORS.result, fontSize: 12, lineHeight: 16, overflow: "truncate",
               formatter: (item) => `${item.name}\n${brlCompact(item.value)}` },
      upperLabel: { show: true, height: 22, color: COLORS.result, fontWeight: 600 },
      levels: [
        { itemStyle: { borderColor: "#fff", borderWidth: 0, gapWidth: 2 },
          upperLabel: { show: false } },
        { itemStyle: { borderColor: "#fff", borderWidth: 2, gapWidth: 2 } },
        { itemStyle: { borderColor: "#fff", borderWidth: 1, gapWidth: 1 } },
      ],
    }],
  };
}

export function divergingChart(items) {
  const ordered = [...items].reverse();
  return {
    tooltip: {
      trigger: "item",
      formatter: (item) => {
        const variance = ordered[item.dataIndex];
        return `${escapeHtml(variance.category)}<br><strong>${brl(variance.value)}</strong>`
          + ` no mês<br>média ${brl(variance.average)}`;
      },
    },
    xAxis: { ...valueAxis, splitLine: { show: false } },
    yAxis: { ...categoryAxis(ordered.map((item) => item.category)),
             axisLine: { lineStyle: { color: COLORS.ink } } },
    series: [{
      type: "bar",
      data: ordered.map((item) => ({
        value: item.difference,
        itemStyle: {
          color: item.difference >= 0 ? COLORS.expense : COLORS.income,
          borderRadius: item.difference >= 0 ? [0, 4, 4, 0] : [4, 0, 0, 4],
        },
      })),
      barMaxWidth: 16,
    }],
  };
}

export function seasonalityChart(labels, months) {
  return {
    tooltip: {
      trigger: "item",
      formatter: (item) => `${labels[item.dataIndex]}<br><strong>${brl(item.value)}</strong>`
        + `<br>média de ${months[item.dataIndex].samples} meses`,
    },
    xAxis: categoryAxis(labels),
    yAxis: valueAxis,
    series: [bar("Média", months.map((month) => month.average), COLORS.expense,
                 { barMaxWidth: 28 })],
  };
}

export function shareByYearChart(years, target) {
  return {
    tooltip: {
      trigger: "item",
      formatter: (item) => {
        const year = years[item.dataIndex];
        return `${year.year}<br><strong>${Math.round(year.share * 100)}%</strong>`
          + ` sem categoria<br>${brl(year.uncategorized)} de ${brl(year.expenses)}`;
      },
    },
    xAxis: categoryAxis(years.map((year) => String(year.year))),
    yAxis: { type: "value", max: 1, axisLabel: { formatter: (value) => `${value * 100}%` },
             splitLine: { lineStyle: { color: COLORS.grid } } },
    series: [{
      type: "bar",
      data: years.map((year) => ({
        value: year.share,
        itemStyle: { color: year.share > target ? COLORS.expense : COLORS.income,
                     borderRadius: [4, 4, 0, 0] },
      })),
      barMaxWidth: 28,
      markLine: averageLine(target, "meta"),
    }],
  };
}
