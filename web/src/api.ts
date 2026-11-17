import type { Answer, Comparison, Meta } from "./types";

async function call<T>(path: string, body?: unknown): Promise<T> {
  const r = await fetch(path, body === undefined ? undefined : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  if (!r.ok) {
    let msg = `${r.status} ${r.statusText}`;
    try { msg = (await r.json()).detail ?? msg; } catch { /* not JSON */ }
    throw new Error(msg);
  }
  return r.json();
}

export const getMeta = () => call<Meta>("/api/meta");
export const ask = (b: { question: string; company?: string; fiscal_year?: string; engine: string; mode: string; model?: string }) =>
  call<Answer>("/api/ask", b);
export const compare = (b: { ticker: string; to_fy: string; item1a: "cached" | "run" | "off" }) =>
  call<Comparison>("/api/compare", b);
