import { api } from "../api.js";
import { COLORS, shareByYearChart } from "../charts.js";
import { card, chart, empty, errorMessage, kpi, monthPicker, monthTitle, pageHeader, stackedBar,
         table } from "../components.js";
import { h } from "../dom.js";
import { brl, dateLabel, monthLabel, percent, sectorLabel, UNCATEGORIZED } from "../format.js";
import { go, refresh } from "../navigation.js";

export async function render(params, { period, categories }) {
  const month = params.get("month") ?? period.default_month;
  const quality = await api.get("/categorization-quality", { month });
  const byYearElement = chart();
  const { by_user: byUser, by_rule: byRule, uncategorized } = quality.methods;

  return {
    content: [
      pageHeader(`Qualidade da categorização · ${monthLabel(quality.start)} a ${monthLabel(quality.end)}`,
                 monthTitle(month),
                 monthPicker(month, period, (next) => go("data", { month: next }))),
      h("div", { className: "grid kpis" },
        kpi({ label: "Despesas sem categoria", value: percent(quality.share, 1),
              change: quality.share > quality.target ? "acima da meta" : "dentro da meta",
              footnote: `Meta: abaixo de ${percent(quality.target)} nos últimos 12 meses` }),
        kpi({ label: "Transações sem categoria", value: String(quality.uncategorized_count),
              footnote: "despesas dos últimos 12 meses" }),
        kpi({ label: "Conflitos de regras", value: String(quality.conflicts.length),
              footnote: "descrições com regras de mais de uma categoria" }),
        kpi({ label: "Regras sem uso", value: String(quality.unused_rules.length),
              footnote: "não encontram nenhuma transação" })),
      h("div", { className: "grid" },
        card({ title: "Despesas sem categoria por ano", hint: "Participação no total de despesas" },
             quality.by_year.length ? byYearElement : empty("Sem despesas.")),
        card({ title: "Como as despesas foram categorizadas", hint: "Valor nos últimos 12 meses" },
             stackedBar([
               { label: "Por regra", value: byRule, color: COLORS.income, text: brl(byRule) },
               { label: "Manual", value: byUser, color: "#1baf7a", text: brl(byUser) },
               { label: UNCATEGORIZED, value: uncategorized, color: COLORS.neutral,
                 text: brl(uncategorized) },
             ]))),
      card({ title: "Sem categoria que mais pesam",
             hint: "Candidatos a novas regras · nos últimos 12 meses" },
           merchantTable(quality.merchants, categories)),
      h("div", { className: "grid" },
        card({ title: "Conflitos de regras",
             hint: "Ficam sem categoria até uma das regras mudar" },
             conflictTable(quality.conflicts)),
        card({ title: "Regras sem uso" }, unusedRuleTable(quality.unused_rules))),
    ],
    charts: quality.by_year.length
      ? [{ element: byYearElement, option: shareByYearChart(quality.by_year, quality.target) }] : [],
  };
}

function merchantTable(merchants, categories) {
  return table([
    { label: "Estabelecimento", cell: (item) => h("strong", {}, item.merchant) },
    { label: "Exemplo", className: "wrap muted", cell: (item) => item.example },
    { label: "Transações", className: "num", cell: (item) => String(item.count) },
    { label: "Última", className: "num muted", cell: (item) => dateLabel(item.last_date) },
    { label: "Total", className: "num right", cell: (item) => brl(item.total) },
    { label: "", className: "right", cell: (item) => h("button", {
      className: "button small", onClick: () => openRuleDialog(item.merchant, categories),
    }, "Criar regra") },
  ], merchants, { emptyText: "Todas as despesas do período têm categoria." });
}

function conflictTable(conflicts) {
  return table([
    { label: "Descrição", className: "wrap", cell: (conflict) => conflict.description },
    { label: "Categorias", className: "wrap muted", cell: (conflict) => conflict.categories.join(", ") },
    { label: "Transações", className: "num right", cell: (conflict) => String(conflict.count) },
  ], conflicts, { emptyText: "Nenhuma descrição com regras conflitantes." });
}

function unusedRuleTable(rules) {
  return table([
    { label: "Regra", className: "num wrap", cell: (rule) => rule.rule },
    { label: "Categoria", className: "muted", cell: (rule) => rule.category },
  ], rules, { emptyText: "Todas as regras categorizam alguma transação." });
}

function escapeRegex(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function openRuleDialog(merchant, categories) {
  const dialog = document.getElementById("dialog");
  const feedback = h("div", { role: "status" });
  const sectors = Map.groupBy(categories, (category) => category.sector ?? UNCATEGORIZED);

  const form = h("form", {
    method: "dialog",
    onSubmit: async (event) => {
      event.preventDefault();
      const fields = new FormData(form);
      try {
        const result = await api.post("/category-rules", {
          category_id: Number(fields.get("category")), rule: fields.get("rule"),
        });
        if (result.conflicts.length) {
          feedback.replaceChildren(errorMessage(
            `Regra criada. ${result.conflicts.length} transações ficaram sem categoria por conflito.`));
          form.querySelector("[type=submit]").remove();
        } else {
          dialog.close();
        }
        refresh();
      } catch (error) {
        feedback.replaceChildren(errorMessage(error.message));
      }
    },
  },
  h("h2", {}, "Nova regra de categoria"),
  h("label", {}, "Categoria",
    h("select", { name: "category", required: true },
      h("option", { value: "", selected: true, disabled: true }, "Escolha a categoria"),
      [...sectors].map(([sector, items]) => h("optgroup", { label: sectorLabel(sector) },
        items.map((category) => h("option", { value: category.id }, category.name)))))),
  h("label", {}, "Regra (expressão regular, sem diferenciar maiúsculas)",
    h("input", { type: "text", name: "rule", required: true, value: escapeRegex(merchant),
                 className: "num" })),
  feedback,
  h("div", { className: "actions" },
    h("button", { className: "button", type: "button", onClick: () => dialog.close() }, "Fechar"),
    h("button", { className: "button primary", type: "submit" }, "Criar regra")));

  dialog.replaceChildren(form);
  dialog.showModal();
}
