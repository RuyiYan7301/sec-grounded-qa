import { type ReactNode, useEffect, useRef, useState } from "react";
import {
  ArrowUp, Ban, BookOpen, CalendarDays, CalendarRange, CalendarX, CheckCircle2, ChevronRight, CircleHelp, Divide, ExternalLink,
  FileText, History, Layers, ListChecks, Quote, ShieldAlert, ShieldCheck, ShieldX, SlidersHorizontal, TriangleAlert, XCircle,
} from "lucide-react";
import * as api from "../api";
import { DemoMiss } from "./DemoMiss";
import type { Answer, Fact, Meta, Status } from "../types";
import { Badge, Card, ErrorNote, Group, IconTile, Monogram, Row, Segmented, Select, Spinner, cx, hashParams, setHashParams } from "./ui";

const EXAMPLE_ICON: Record<string, [typeof Ban, string]> = {
  "Fiscal calendar": [CalendarDays, "blue"], "Period mismatch": [CalendarRange, "orange"], "Restatement": [History, "purple"],
  "Ambiguous year": [CircleHelp, "teal"], "Narrative with citations": [Quote, "indigo"], "Out of range": [CalendarX, "gray"],
  "No advice": [Ban, "red"],
};
const WARNING_ICON: Record<string, typeof Ban> = {
  period_mismatch: CalendarRange, ambiguous_year: CircleHelp, restated: History, superseded_value: History, split_adjusted: Divide,
  scope: Layers, out_of_range: CalendarX,
};

const STATUS: Record<Status, { icon: typeof ShieldCheck; color: string; title: string }> = {
  verified: { icon: ShieldCheck, color: "text-ok", title: "Verified" },
  verified_with_warnings: { icon: ShieldCheck, color: "text-ok", title: "Verified · with notes on the data" },
  traceable: { icon: ShieldAlert, color: "text-warn", title: "Traceable · a check is unresolved" },
  unverified: { icon: ShieldAlert, color: "text-warn", title: "Not verified" },
  withheld: { icon: ShieldX, color: "text-bad", title: "Answer withheld" },
};

export const WARNING_TITLES: Record<string, string> = {
  period_mismatch: "Fiscal years end on different dates",
  ambiguous_year: "“2024” read as fiscal 2024",
  restated: "A later filing revised this figure",
  split_adjusted: "Per-share figures restated for a stock split",
  scope: "Broader line item used",
  superseded_value: "Earlier value superseded",
  alias_interpretation: "Question wording interpreted",
  derived_metric_definition: "Computed metric, defined by this engine",
  ungrounded_numbers: "A number could not be traced",
  out_of_range: "Outside the covered years",
  no_company: "No covered company named",
};

const pretty = (s: string) => s.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());
const clean = (s: string) => s.replace(/\*\*(.+?)\*\*/g, "$1");

export function AskView({ meta }: { meta: Meta | null }) {
  const [q, setQ] = useState("");
  const [company, setCompany] = useState("");
  const [year, setYear] = useState("");
  const [engine, setEngine] = useState<"auto" | "typed" | "agent">("auto");
  const [mode, setMode] = useState<"verify" | "single">("verify");
  const [model, setModel] = useState("");
  const [showSettings, setShowSettings] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [res, setRes] = useState<Answer | null>(null);
  const [sel, setSel] = useState<number | null>(null);
  const started = useRef(0);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!busy) return;
    const t = setInterval(() => setElapsed(Math.round((Date.now() - started.current) / 1000)), 500);
    return () => clearInterval(t);
  }, [busy]);

  useEffect(() => {   // a shared link: #/?q=...
    const shared = hashParams().get("q");
    if (shared) run(shared);
  }, []);   // eslint-disable-line react-hooks/exhaustive-deps

  async function run(question = q) {
    if (!question.trim() || busy) return;
    setHashParams("/", { q: question });
    setQ(question); setBusy(true); setErr(null); setSel(null); started.current = Date.now(); setElapsed(0);
    try {
      setRes(await api.ask({ question, company: company || undefined, fiscal_year: year || undefined, engine, mode, model: model || undefined }));
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const options = [company, year, engine !== "auto" ? `${engine} engine` : ""].filter(Boolean).join(" · ");
  const composer = (
    <form onSubmit={(e) => { e.preventDefault(); run(); }} className="card transition focus-within:shadow-[0_2px_4px_rgba(0,0,0,0.04),0_12px_32px_rgba(0,0,0,0.08)]">
      <textarea value={q} onChange={(e) => setQ(e.target.value)} rows={res || busy ? 1 : 2}
        placeholder="Ask about revenue, margins, cash flow, restatements or risk factors"
        onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); run(); } }}
        className="t-body block w-full resize-none bg-transparent px-5 pt-4 pb-1 outline-none placeholder:text-subtle" />
      <div className="flex items-center justify-between gap-2 px-3 pb-3">
        {meta?.demo ? <span className="t-caption px-2 text-muted">Public demo: pick a question below, or run it locally to ask your own</span> :
        <button type="button" onClick={() => setShowSettings((s) => !s)}
          className={cx("inline-flex h-8 items-center gap-1.5 rounded-full px-3 text-[13px] transition",
            showSettings || options ? "bg-fill text-fg" : "text-muted hover:bg-fill hover:text-fg")}>
          <SlidersHorizontal className="size-3.5" strokeWidth={2} />{options || "Options"}
        </button>}
        <button type="submit" disabled={!q.trim() || busy} aria-label="Ask"
          className="inline-flex size-8 items-center justify-center rounded-full bg-accent-fill text-white transition hover:brightness-110 disabled:bg-fill disabled:text-subtle">
          {busy ? <Spinner /> : <ArrowUp className="size-[18px]" strokeWidth={2.4} />}
        </button>
      </div>
      {showSettings && meta && !meta.demo && (
        <div className="grid grid-cols-2 gap-4 border-t border-line px-5 py-4 sm:grid-cols-3">
          <Select label="Company" value={company} onChange={(e) => setCompany(e.target.value)}>
            <option value="">Any</option>
            {meta.companies.map((c) => <option key={c.ticker} value={c.ticker}>{c.name} ({c.ticker})</option>)}
          </Select>
          <Select label="Fiscal year" value={year} onChange={(e) => setYear(e.target.value)}>
            <option value="">Any</option>
            {meta.years.map((y) => <option key={y}>{y}</option>)}
          </Select>
          <Select label="Model" value={model || meta.default_model} onChange={(e) => setModel(e.target.value)}>
            {meta.models.map((m) => <option key={m}>{m}</option>)}
          </Select>
          <Segmented label="Engine" value={engine} onChange={setEngine} options={[
            { value: "auto", label: "Auto", hint: "Figures go to the typed engine, filing-text questions to the agent" },
            { value: "typed", label: "Typed", hint: "Plan + code; figures only" },
            { value: "agent", label: "Agent", hint: "Tool-calling agent with filing search" }]} />
          <Segmented label="Agent mode" value={mode} onChange={setMode} options={[
            { value: "verify", label: "Verify", hint: "Check the draft and revise or withhold it" },
            { value: "single", label: "Single", hint: "One pass" }]} />
        </div>
      )}
    </form>
  );

  if (!res && !busy && !err) {
    return (
      <div className="mx-auto max-w-[760px] px-5 pt-[9vh] pb-20">
        <div className="mb-10 text-center">
          <h1 className="t-hero">Ask the 10-Ks.</h1>
          <p className="t-body mx-auto mt-4 max-w-[560px]">
            Figures are computed by code from XBRL, and each one links to the filing it came from. When the data has a catch, the answer says so.
          </p>
        </div>
        {composer}
        <Group title="Questions with a catch" className="mt-12">
          {meta?.examples.map((ex) => (
            <Row key={ex.label} onClick={() => run(ex.question)} className="group">
              <div className="flex items-center gap-3.5 px-4 py-3">
                <IconTile icon={(EXAMPLE_ICON[ex.label] ?? [FileText])[0]} color={(EXAMPLE_ICON[ex.label] ?? [FileText, "blue"])[1]} size={30} />
                <div className="min-w-0 flex-1">
                  <div className="t-callout">{ex.question}</div>
                  <div className="t-caption mt-0.5 text-muted">{ex.label}</div>
                </div>
                <ChevronRight className="size-4 shrink-0 text-subtle transition group-hover:translate-x-0.5" strokeWidth={2.2} />
              </div>
            </Row>
          ))}
        </Group>
        {meta?.demo && (
          <Group title="More questions" className="mt-8">
            {meta.demo_questions.filter((q) => !meta.examples.some((e) => e.question === q)).map((q) => (
              <Row key={q} onClick={() => run(q)} className="group">
                <div className="flex items-center gap-3.5 px-4 py-3">
                  <span className="t-callout min-w-0 flex-1">{q}</span>
                  <ChevronRight className="size-4 shrink-0 text-subtle transition group-hover:translate-x-0.5" strokeWidth={2.2} />
                </div>
              </Row>
            ))}
          </Group>
        )}
        {meta?.demo && (
          <p className="t-foot mt-6 px-1 text-muted">
            These answers were computed in advance by the same engine and local model and are shown unchanged. The Companies and
            10-K changes pages run live.
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[1120px] px-5 pt-6 pb-16">
      <div className="grid gap-x-8 gap-y-6 lg:grid-cols-[minmax(0,1fr)_380px]">
        <div className="min-w-0 space-y-6">
          {composer}
          {err && (meta?.demo ? <DemoMiss question={q} meta={meta} onAsk={run} /> : <ErrorNote>{err}</ErrorNote>)}
          {busy && <Working elapsed={elapsed} />}
          {res && !busy && <AnswerBlock a={res} sel={sel} onSel={setSel} />}
        </div>
        <aside className="min-w-0">
          <div className="lg:sticky lg:top-[72px]">{res && !busy && <Evidence a={res} sel={sel} onSel={setSel} />}</div>
        </aside>
      </div>
    </div>
  );
}

function Working({ elapsed }: { elapsed: number }) {
  return (
    <Card className="p-6">
      <div className="flex items-center gap-3">
        <Spinner className="text-accent" />
        <span className="t-callout font-medium">Planning, looking up the facts and writing the answer</span>
        <span className="num t-foot ml-auto text-muted">{elapsed}s</span>
      </div>
      <p className="t-foot mt-2 text-muted">A local 8B model usually takes 10–40 seconds; narrative questions with verification take longer.</p>
      <div className="mt-5 space-y-2.5">
        {[94, 82, 60].map((w) => <div key={w} className="h-3.5 animate-pulse rounded-full bg-fill" style={{ width: `${w}%` }} />)}
      </div>
    </Card>
  );
}

function AnswerBlock({ a, sel, onSel }: { a: Answer; sel: number | null; onSel: (i: number | null) => void }) {
  const s = STATUS[a.status];
  const Icon = s.icon;
  return (
    <div className="space-y-6">
      <Card className="px-6 pt-5 pb-4">
        <div className={cx("flex items-center gap-1.5 text-[13px] font-semibold", s.color)}>
          <Icon className="size-4" strokeWidth={2.2} />{s.title}
        </div>
        <div className="t-body mt-3 space-y-3">
          {splitParas(a).map((para, k) => (
            <p key={k}>
              {para.map((seg, j) => seg.fact === undefined ? <span key={j}>{clean(seg.text)}</span> : (
                <FigureChip key={j} text={seg.text} fact={a.facts[seg.fact]} active={sel === seg.fact}
                  onClick={() => onSel(sel === seg.fact ? null : seg.fact!)} />
              ))}
            </p>
          ))}
        </div>
        {a.status !== "verified" && a.status !== "verified_with_warnings" && <p className="t-foot mt-4">{a.status_text}</p>}
        <div className="t-caption mt-4 flex flex-wrap gap-x-3 gap-y-1 border-t border-line pt-3 text-muted">
          <span>{a.mode === "typed" ? "Typed engine (plan + code)" : `Agent, ${a.mode} mode`}</span>
          <span>{a.model}</span>
          {a.precomputed && <span>computed in advance</span>}
          <span className="num">{a.latency_s} s</span>
          <span className="num">{a.llm_calls} model calls</span>
          <span className="num">{a.tokens.toLocaleString()} tokens</span>
        </div>
      </Card>
      {a.warnings.length > 0 && (
        <Group title="Notes on the data">
          {a.warnings.map((w, i) => (
            <Row key={i} inset={48}>
              <div className="flex gap-3 px-4 py-3">
                {(() => { const I = WARNING_ICON[w.code] ?? TriangleAlert; return <I className={cx("mt-0.5 size-[18px] shrink-0", w.mentioned_in_answer === false ? "text-bad" : "text-warn")} strokeWidth={2} />; })()}
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="t-callout font-semibold">{WARNING_TITLES[w.code] ?? pretty(w.code)}</span>
                    {w.mentioned_in_answer === false && <Badge tone="bad">not mentioned in the answer</Badge>}
                  </div>
                  <div className="t-foot mt-0.5">{w.message.charAt(0).toUpperCase() + w.message.slice(1)}</div>
                </div>
              </div>
            </Row>
          ))}
        </Group>
      )}
      <Trace a={a} />
    </div>
  );
}

function splitParas(a: Answer) {
  const out: { text: string; fact?: number }[][] = [[]];
  for (const seg of a.segments) {
    if (seg.fact !== undefined) { out[out.length - 1].push(seg); continue; }
    seg.text.split(/\n{2,}/).forEach((part, i) => {
      if (i > 0) out.push([]);
      if (part) out[out.length - 1].push({ text: part });
    });
  }
  return out.filter((p) => p.length);
}

function FigureChip({ text, fact, active, onClick }: { text: string; fact: Fact; active: boolean; onClick: () => void }) {
  return (
    <span className="group relative inline-block">
      <button onClick={onClick}
        className={cx("num -mx-0.5 rounded-md px-1 font-medium transition",
          active ? "bg-accent-fill text-white" : "bg-accent-soft text-accent hover:brightness-95")}>
        {text}
      </button>
      <span className="card pointer-events-none absolute bottom-full left-1/2 z-20 mb-2 hidden w-72 -translate-x-1/2 p-3 text-left group-hover:block">
        <span className="t-foot block font-semibold text-fg">{fact.ticker} · {pretty(fact.label)} · {fact.period}</span>
        <span className="block font-mono text-[11px] text-muted">{fact.concept}</span>
        <span className="t-caption mt-1 block text-muted">From the {fact.filing_fiscal_year ? `FY${fact.filing_fiscal_year} ` : ""}{fact.form}, filed {fact.filed}. Click to see it.</span>
      </span>
    </span>
  );
}

function Evidence({ a, sel, onSel }: { a: Answer; sel: number | null; onSel: (i: number | null) => void }) {
  const [tab, setTab] = useState<"facts" | "passages">(a.facts.length || !a.sources.length ? "facts" : "passages");
  const refs = useRef<(HTMLDivElement | null)[]>([]);
  useEffect(() => { if (sel !== null) { setTab("facts"); refs.current[sel]?.scrollIntoView({ block: "nearest", behavior: "smooth" }); } }, [sel]);
  return (
    <div>
      <div className="mb-3 flex items-center justify-between px-1">
        <h2 className="t-headline">Sources</h2>
        <Segmented size="sm" value={tab} onChange={setTab} options={[
          { value: "facts", label: <>Figures <span className="num text-muted">{a.facts.length}</span></> },
          { value: "passages", label: <>Passages <span className="num text-muted">{a.sources.length}</span></> }]} />
      </div>
      <div className="max-h-[calc(100vh-9rem)] space-y-3 overflow-y-auto pb-1">
        {tab === "facts" && (a.facts.length ? a.facts.map((f, i) => (
          <div key={i} ref={(el) => { refs.current[i] = el; }} onClick={() => onSel(sel === i ? null : i)}
            className={cx("card cursor-pointer p-4 transition", sel === i ? "ring-2 ring-accent-fill" : "hover:shadow-[0_2px_4px_rgba(0,0,0,0.04),0_8px_24px_rgba(0,0,0,0.06)]")}>
            <div className="flex items-center gap-3">
              <Monogram ticker={f.ticker} size={32} />
              <div className="min-w-0 flex-1">
                <div className="t-callout truncate font-semibold">{pretty(f.label)}</div>
                <div className="t-caption text-muted">{f.ticker} · {f.period} · ended {f.period_end}</div>
              </div>
              <span className="num t-headline shrink-0">{f.display.split(" (=")[0]}</span>
            </div>
            <div className="mt-3 font-mono text-[11px] text-muted">{f.concept}</div>
            <a href={f.url} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()}
              className="t-foot mt-2 inline-flex items-center gap-1 text-accent hover:underline">
              {f.filing_fiscal_year ? `FY${f.filing_fiscal_year} ` : ""}{f.form}, filed {f.filed}<ExternalLink className="size-3" />
            </a>
            {f.restated && <Badge tone="warn" className="ml-2">earlier reported</Badge>}
            <p className="t-foot mt-2">{f.provenance}</p>
          </div>
        )) : <Empty>No XBRL figures were used for this answer.</Empty>)}
        {tab === "passages" && (a.sources.length ? a.sources.map((s, i) => (
          <div key={i} className="card p-4">
            <div className="flex items-center justify-between gap-2">
              <span className="t-foot inline-flex items-center gap-1.5 font-semibold"><BookOpen className="size-3.5 text-muted" />{s.citation}</span>
              {s.url && <a href={s.url} target="_blank" rel="noreferrer" className="text-accent"><ExternalLink className="size-3.5" /></a>}
            </div>
            <p className="t-foot mt-2 line-clamp-[10] border-l-2 border-accent-fill/40 pl-3">{s.excerpt}</p>
          </div>
        )) : <Empty>No filing passages: the figures come from XBRL facts.</Empty>)}
      </div>
    </div>
  );
}

function Trace({ a }: { a: Answer }) {
  const [open, setOpen] = useState(a.tool_calls.some((t) => !t.ok) || a.checks.length > 0);
  return (
    <Card>
      <button onClick={() => setOpen((o) => !o)} className="flex w-full items-center gap-2 px-5 py-3.5 text-left">
        <ListChecks className="size-[18px] text-muted" strokeWidth={2} /><span className="t-callout font-semibold">How this answer was checked</span>
        <span className="t-foot text-muted">{a.tool_calls.length} steps{a.checks.length ? `, ${a.checks.length} findings` : ""}</span>
        <ChevronRight className={cx("ml-auto size-4 text-subtle transition", open && "rotate-90")} strokeWidth={2.2} />
      </button>
      {open && (
        <div className="border-t border-line px-5 py-4">
          <ol className="space-y-4">
            {a.tool_calls.map((t, i) => (
              <li key={i} className="flex gap-3">
                {t.ok ? <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-ok" strokeWidth={2.2} /> : <XCircle className="mt-0.5 size-4 shrink-0 text-bad" strokeWidth={2.2} />}
                <div className="min-w-0">
                  <div className="t-foot font-semibold">{pretty(t.tool)}
                    {Object.keys(t.args).length > 0 && <span className="ml-2 font-mono text-[11px] font-normal text-muted">{JSON.stringify(t.args)}</span>}
                  </div>
                  <div className="t-foot mt-0.5 break-words">{t.summary}</div>
                </div>
              </li>
            ))}
          </ol>
          {a.checks.length > 0 && (
            <div className="mt-5">
              <div className="section-label mb-1.5">Findings</div>
              <ul className="t-foot space-y-1">{a.checks.map((c, i) => <li key={i}>{c}</li>)}</ul>
            </div>
          )}
          {a.draft && (
            <div className="mt-5">
              <div className="section-label mb-1.5">Rejected draft, not shown as the answer</div>
              <p className="t-foot rounded-xl bg-fill p-3">{a.draft}</p>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}

const Empty = ({ children }: { children: ReactNode }) => <div className="card t-foot px-4 py-8 text-center text-muted">{children}</div>;
