import type { Answer, Comparison, Meta, Peers } from "./types";

/** VITE_STATIC=1: a static build that reads JSON exported by `secqa export-static` instead of calling the server. */
const STATIC = import.meta.env.VITE_STATIC === "1";

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

async function file<T>(path: string): Promise<T> {
  const r = await fetch(`${import.meta.env.BASE_URL}${path}`);
  if (!r.ok) throw new Error(`Not available in this demo (${r.status}).`);
  return r.json();
}

const norm = (q: string) => q.toLowerCase().replace(/’/g, "'").split(/\s+/).join(" ").replace(/[?. ]+$/, "");
let answers: Promise<{ answers: Answer[] }> | null = null;

export const getMeta = () => (STATIC ? file<Meta>("api/meta.json") : call<Meta>("/api/meta"));

export async function ask(b: { question: string; company?: string; fiscal_year?: string; engine: string; mode: string; model?: string }) {
  if (!STATIC) return call<Answer>("/api/ask", b);
  answers ??= file("api/answers.json");
  const hit = (await answers).answers.find((a) => norm(a.question) === norm(b.question));
  if (!hit) throw new Error("This public demo answers the listed questions, computed in advance with the same engine and model. Run it locally (see the README) to ask your own.");
  return { ...hit, precomputed: true };
}

export const compare = (b: { ticker: string; to_fy: string; item1a: "cached" | "run" | "off" }) =>
  STATIC ? file<Comparison>(`api/compare/${b.ticker}_${b.to_fy}.json`) : call<Comparison>("/api/compare", b);

export const peers = (b: { metric: string; fy: string }) =>
  STATIC ? file<Peers>(`api/peers/${b.metric}_${b.fy}.json`) : call<Peers>("/api/peers", b);
