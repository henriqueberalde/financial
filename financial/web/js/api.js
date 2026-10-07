export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

async function request(method, path, { params, body } = {}) {
  const url = new URL(`/api${path}`, location.origin);
  for (const [name, value] of Object.entries(params ?? {})) {
    if (value != null && value !== "") url.searchParams.set(name, value);
  }

  const response = await fetch(url, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const detail = await response.json().then((json) => json.detail, () => null);
    throw new ApiError(response.status,
                       typeof detail === "string" ? detail : response.statusText);
  }

  return response.status === 204 ? null : response.json();
}

export const api = {
  get: (path, params) => request("GET", path, { params }),
  put: (path, body) => request("PUT", path, { body }),
  post: (path, body) => request("POST", path, { body }),
};
