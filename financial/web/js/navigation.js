/** Link to a page with its query parameters, dropping empty ones. */
export function link(page, params = {}) {
  const query = new URLSearchParams(Object.entries(params)
    .filter(([, value]) => value != null && value !== ""));
  return `#/${page}${query.size ? `?${query}` : ""}`;
}

export function go(page, params) {
  location.hash = link(page, params);
}

/** Render the current page again, keeping its parameters. */
export function refresh() {
  window.dispatchEvent(new HashChangeEvent("hashchange"));
}
