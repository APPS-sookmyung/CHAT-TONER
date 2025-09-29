// src/lib/api.ts
const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

export async function apiGet<T>(path: string, init: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    credentials: "include", // When using cookies/sessions
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
    ...init,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return (await res.json()) as T;
}
