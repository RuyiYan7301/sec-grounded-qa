import { ArrowRight, BarChart3, Terminal } from "lucide-react";
import type { Meta } from "../types";
import { Card, Group, IconTile, Row } from "./ui";

/** Words people use for each metric (lower case); the metric's own display name is added automatically. */
const ALIASES: Record<string, string[]> = {
  revenue: ["revenue", "revenues", "sales", "net sales", "top line"],
  operating_income: ["operating income", "operating profit", "income from operations"],
  net_income: ["net income", "net profit", "net earnings", "profit"],
  gross_profit: ["gross profit"],
  cost_of_revenue: ["cost of revenue", "cost of sales", "cogs"],
  research_and_development: ["r&d", "research and development", "research & development"],
  selling_general_administrative: ["sg&a", "selling, general", "selling general"],
  operating_expenses: ["operating expenses", "opex"],
  income_tax_expense: ["income tax", "tax expense"],
  eps_diluted: ["diluted eps", "eps", "earnings per share"],
  eps_basic: ["basic eps"],
  total_assets: ["total assets", "assets"],
  total_liabilities: ["total liabilities", "liabilities"],
  stockholders_equity: ["equity", "stockholders' equity", "shareholders' equity"],
  cash_and_equivalents: ["cash and cash equivalents", "cash"],
  inventory: ["inventory", "inventories"],
  goodwill: ["goodwill"],
  long_term_debt: ["long-term debt", "long term debt", "debt"],
  operating_cash_flow: ["operating cash flow", "cash from operations", "cash flow from operations"],
  capital_expenditures: ["capital expenditures", "capex", "capital expenditure"],
  share_based_compensation: ["stock-based compensation", "share-based compensation", "stock compensation"],
  free_cash_flow: ["free cash flow", "fcf"],
  gross_margin: ["gross margin"],
  operating_margin: ["operating margin"],
  net_margin: ["net margin", "profit margin"],
  rd_intensity: ["r&d intensity", "r&d as a share", "r&d as a percentage"],
};

function detect(q: string, meta: Meta) {
  const s = ` ${q.toLowerCase().replace(/’/g, "'")} `;
  const companies = meta.companies.filter((c) =>
    s.includes(c.name.toLowerCase()) || new RegExp(`\\b${c.ticker.toLowerCase()}\\b`).test(s));
  let metric: string | null = null, best = 0;
  for (const m of meta.metrics) {
    for (const a of [...(ALIASES[m.id] ?? []), m.name.toLowerCase()]) {
      if (s.includes(a) && a.length > best) { metric = m.id; best = a.length; }
    }
  }
  const y = s.match(/(?:fy|fiscal(?: year)?)\s*'?(20)?(2[3-5])\b/) ?? s.match(/\b20(2[3-5])\b/);
  const fy = y ? `FY20${y[y.length - 1]}` : null;
  return { companies, metric, fy };
}

function closest(q: string, pool: string[], n = 3) {
  const words = (t: string) => new Set(t.toLowerCase().match(/[a-z0-9&']+/g) ?? []);
  const a = words(q);
  return pool.map((p) => {
    const b = words(p);
    const inter = [...a].filter((w) => b.has(w) && w.length > 2).length;
    return { p, score: inter / Math.sqrt(a.size * b.size || 1) };
  }).sort((x, y) => y.score - x.score).slice(0, n).filter((x) => x.score > 0).map((x) => x.p);
}

export function DemoMiss({ question, meta, onAsk }: { question: string; meta: Meta; onAsk: (q: string) => void }) {
  const { companies, metric, fy } = detect(question, meta);
  const m = meta.metrics.find((x) => x.id === metric);
  const near = closest(question, meta.demo_questions);
  return (
    <div className="space-y-6">
      <Card className="px-6 py-5">
        <div className="t-headline">This question was not answered in advance</div>
        <p className="t-callout mt-2">
          The public demo runs without a model, so the Ask page shows answers computed in advance by the same engine.
          {m ? " The figures you asked about are on the Companies page, computed by the engine for all eight companies." : ""}
        </p>
        {m && (
          <a href={`#/companies?m=${m.id}&fy=${fy ?? "FY2025"}`}
            className="mt-4 flex items-center gap-3 rounded-xl bg-canvas px-4 py-3 transition hover:brightness-[0.98]">
            <IconTile icon={BarChart3} color="blue" size={30} />
            <span className="min-w-0 flex-1">
              <span className="t-callout block font-semibold">{m.name}, {fy ?? "FY2025"}, all eight companies</span>
              <span className="t-foot mt-0.5 flex items-center gap-1.5">
                {companies.length ? `including ${companies.map((c) => c.name).join(" and ")}, with each company's fiscal period` : "ranked, with each company's fiscal period"}
                {!fy && <span className="text-muted">· no fiscal year found in the question, showing FY2025</span>}
              </span>
            </span>
            <ArrowRight className="size-4 text-accent" strokeWidth={2.2} />
          </a>
        )}
        <div className="t-foot mt-4 flex items-start gap-2 text-muted">
          <Terminal className="mt-0.5 size-3.5 shrink-0" />
          <span>To ask your own questions, run it locally: <code className="font-mono text-[12px]">secqa web</code> with Ollama (see the README on GitHub).</span>
        </div>
      </Card>
      {near.length > 0 && (
        <Group title="Closest questions answered in advance">
          {near.map((q) => (
            <Row key={q} onClick={() => onAsk(q)} className="group">
              <div className="flex items-center gap-3 px-4 py-3">
                <span className="t-callout min-w-0 flex-1">{q}</span>
                <ArrowRight className="size-4 shrink-0 text-subtle transition group-hover:translate-x-0.5" strokeWidth={2.2} />
              </div>
            </Row>
          ))}
        </Group>
      )}
    </div>
  );
}
