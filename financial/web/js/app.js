import { api } from "./api.js";
import { disposeAll, mount } from "./charts.js";
import { empty, errorMessage } from "./components.js";
import * as data from "./pages/data.js";
import * as overview from "./pages/overview.js";
import * as recurring from "./pages/recurring.js";
import * as spending from "./pages/spending.js";

const PAGES = { overview, spending, recurring, data };
const main = document.getElementById("page");
const dialog = document.getElementById("dialog");
let context = null;
let rendering = 0;

async function loadContext() {
  const [period, categories] = await Promise.all([api.get("/period"), api.get("/categories")]);
  return { period, categories };
}

async function render() {
  const [path, query] = location.hash.replace(/^#\/?/, "").split("?");
  const name = path in PAGES ? path : "overview";
  const current = ++rendering;

  for (const anchor of document.querySelectorAll(".sidebar a")) {
    if (anchor.dataset.page === name) anchor.setAttribute("aria-current", "page");
    else anchor.removeAttribute("aria-current");
  }

  if (dialog.open) dialog.close();
  main.classList.add("loading");
  try {
    context ??= await loadContext();
    if (context.period.default_month == null) {
      show(current, { content: [empty("Nenhuma transação importada ainda.")] });
      return;
    }
    show(current, await PAGES[name].render(new URLSearchParams(query), context));
  } catch (error) {
    show(current, { content: [errorMessage(`Não foi possível carregar a página: ${error.message}`)] });
  } finally {
    if (current === rendering) main.classList.remove("loading");
  }
}

function show(current, { content, charts = [] }) {
  // A newer navigation started while this page was loading
  if (current !== rendering) return;

  disposeAll();
  main.replaceChildren(...content);
  for (const { element, option, ...handlers } of charts) mount(element, option, handlers);
}

window.addEventListener("hashchange", render);
render();
