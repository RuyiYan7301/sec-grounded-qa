import { Fragment, useEffect, useState } from "react";
import { ArrowLeftRight, ArrowRight, ArrowUpRight, ChevronRight, FileDiff, History, Info, Landmark, Percent, Play, Receipt, TrendingUp } from "lucide-react";
import * as api from "../api";
import type { Comparison, Meta, MetricRow, Para } from "../types";
import { Badge, Button, Card, ErrorNote, Group, IconTile, Monogram, Row, Segmented, Select, Spinner, cx } from "./ui";

const GROUP_ICON: Record<string, typeof Receipt> = {
  "Income statement": Receipt, "Balance sheet": Landmark, "Cash flow": ArrowLeftRight, "Ratios and derived": Percent,
};

type Tab = "figures" | "revised" | "risk";

const longDate = (iso: string) => new Date(iso + "T00:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });

export function CompareView({ meta }: { meta: Meta | null }) {
  const [ticker, setTicker] = useState("NVDA");
  const [fy, setFy] = useState("FY2025");
  const [data, setData] = useState<Comparison | null>(null);
  const [busy, setBusy] = useState<"" | "figures" | "item1a">("");
  const [err, setErr] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("figures");

  async function load(item1a: "cached" | "run" = "cached", t = ticker, y = fy) {
    setBusy(item1a === "run" ? "item1a" : "figures"); setErr(null);
    try {
      setData(await api.compare({ ticker: t, to_fy: y, item1a }));
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy("");
    }
  }
  useEffect(() => { load(); }, []);   // first view: Nvidia FY2025

  return (
    <div className="mx-auto max-w-[1120px] px-5 pt-10 pb-16">
      <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
        <div className="flex items-center gap-4">
          <Monogram ticker={data?.ticker ?? ticker} size={56} />
          <div>
            <div className="text-[13px] font-semibold text-accent">Compare 10-Ks</div>
            <h1 className="t-large">{data?.company ?? meta?.companies.find((c) => c.ticker === ticker)?.name ?? ticker}</h1>
            {data && (
              <div className="t-callout mt-1 flex flex-wrap items-center gap-x-2">
                <span>{data.to_fy} 10-K compared with {data.from_fy}</span>
                <span className="text-subtle">·</span>
                <a href={data.target_filing.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-accent hover:underline">
                  Filed {longDate(data.target_filing.filed)}<ArrowUpRight className="size-3.5" />
                </a>
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Select aria-label="Company" value={ticker} className="w-52"
            onChange={(e) => { setTicker(e.target.value); load("cached", e.target.value, fy); }}>
            {meta?.companies.map((c) => <option key={c.ticker} value={c.ticker}>{c.name} ({c.ticker})</option>)}
          </Select>
          <Segmented value={fy} onChange={(v) => { setFy(v); load("cached", ticker, v); }}
            options={(meta?.target_years ?? ["FY2024", "FY2025"]).map((y) => ({ value: y, label: y }))} />
        </div>
      </div>

      {err && <div className="mt-8"><ErrorNote>{err}</ErrorNote></div>}
      {!data && busy && <div className="t-callout mt-12 flex items-center gap-2 text-muted"><Spinner />Building the comparison</div>}

      {data && (
        <div className={cx("mt-8 transition-opacity", busy === "figures" && "opacity-40")}>
          <div className="mt-5 grid gap-4 sm:grid-cols-3">
            <Stat icon={TrendingUp} color="blue" label="Changed materially" n={data.summary.large} unit={`of ${data.metrics.length} metrics`} note="10% or more; 5 pp for ratios" />
            <Stat icon={History} color="orange" label="Revised earlier figures" n={data.summary.revised} unit={data.from_fy} note="changed since first reported" tint={data.summary.revised ? "text-warn" : undefined} />
            <Stat icon={FileDiff} color="purple" label="Risk factors changed" n={data.summary.item1a} unit="paragraphs" note={data.summary.item1a === null ? "not compared yet" : "flagged by the model"} />
          </div>

          <div className="mt-10 mb-4 flex justify-center">
            <Segmented value={tab} onChange={setTab} options={[
              { value: "figures", label: "Figures" },
              { value: "revised", label: <>Revised <span className="num text-muted">{data.summary.revised}</span></> },
              { value: "risk", label: "Risk factors" }]} />
          </div>
          {tab === "figures" && <Figures data={data} />}
          {tab === "revised" && <Revised data={data} />}
          {tab === "risk" && <Risk data={data} busy={busy === "item1a"} onRun={() => load("run")} />}
        </div>
      )}
    </div>
  );
}

function Stat({ icon, color, label, n, unit, note, tint }: { icon: typeof Receipt; color: string; label: string; n: number | null; unit: string; note: string; tint?: string }) {
  return (
    <Card className="px-5 py-4">
      <div className="flex items-center gap-2.5"><IconTile icon={icon} color={color} size={26} /><span className="t-callout font-semibold">{label}</span></div>
      <div className="mt-2 flex items-baseline gap-1.5">
        <span className={cx("num font-[family-name:var(--font-display)] text-[40px] leading-none font-semibold tracking-[-0.03em]", tint)}>{n ?? "—"}</span>
        <span className="t-foot text-muted">{unit}</span>
      </div>
      <div className="t-foot mt-2 text-muted">{note}</div>
    </Card>
  );
}

const minus = (s: string) => s.replace(/^-/, "−").replace(/\(-/, "(−").replace(/ -/g, " −");

/** A small diverging bar: right for an increase, left for a decrease, length = size of the change
 * (percent change capped at 100%; a percentage-point change is scaled x10 so 5 pp reads like 50%). */
function ChangeBar({ m }: { m: MetricRow }) {
  const v = m.pp_change !== null ? m.pp_change * 10 : m.percent_change;
  if (v === null || v === undefined) return <span className="inline-block w-[72px]" />;
  const w = Math.max(2, Math.min(Math.abs(v), 100) / 100 * 34);
  return (
    <span className="relative inline-block h-2 w-[72px] rounded-full bg-fill align-middle" aria-hidden>
      <span className="absolute top-[-2px] left-1/2 h-3 w-px bg-line-strong" />
      <span className={cx("absolute top-0 h-2 rounded-full", m.size === "large" ? "bg-accent-fill" : "bg-subtle/60")}
        style={v >= 0 ? { left: "50%", width: w } : { right: "50%", width: w }} />
    </span>
  );
}

function Delta({ m }: { m: MetricRow }) {
  const d = m.pp_change ?? m.absolute_change;
  const [abs, pct] = m.change_display.replace(/^\+/, "").split(" (");
  if (d === null || d === undefined) return <span className="text-muted">{m.change_display}</span>;
  const rel = m.pp_change !== null ? minus(abs) : pct ? minus(pct.replace(")", "").replace(/^\+/, "")) : "";
  return (
    <span className="inline-flex items-center justify-end gap-3">
      <span>{m.pp_change !== null ? "" : minus(abs)}</span>
      <span className={cx("min-w-[64px] text-right font-medium", m.size !== "large" && "text-muted")}>{rel}</span>
      <ChangeBar m={m} />
    </span>
  );
}

function Figures({ data }: { data: Comparison }) {
  const [onlyLarge, setOnlyLarge] = useState(false);
  const [open, setOpen] = useState<string | null>(null);
  const groups = ["Income statement", "Balance sheet", "Cash flow", "Ratios and derived"];
  const rows = data.metrics.filter((m) => !onlyLarge || m.size === "large");
  return (
    <div className="space-y-8">
      <div className="-mb-4 flex justify-end px-1">
        <label className="t-foot flex cursor-pointer items-center gap-2 text-muted">
          <input type="checkbox" checked={onlyLarge} onChange={(e) => setOnlyLarge(e.target.checked)} className="size-4 accent-[var(--color-accent-fill)]" />
          Only material changes
        </label>
      </div>
      {groups.map((g) => {
        const rs = rows.filter((r) => r.statement === g);
        if (!rs.length) return null;
        return (
          <Group key={g} title={(() => { const I = GROUP_ICON[g]; return <span className="inline-flex items-center gap-1.5">{I && <I className="size-4" strokeWidth={2} />}{g}</span>; })()}>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[680px] text-[14px]">
                <thead>
                  <tr className="t-caption border-b border-line text-left text-muted">
                    <th className="py-2 pr-4 pl-5 font-medium">Metric</th>
                    <th className="px-4 py-2 text-right font-medium">{data.from_fy}</th>
                    <th className="px-4 py-2 text-right font-medium">{data.to_fy}</th>
                    <th className="py-2 pr-5 pl-4 text-right font-medium">Change</th>
                  </tr>
                </thead>
                <tbody>
                  {rs.map((m) => (
                    <Fragment key={m.id}>
                      <tr onClick={() => setOpen(open === m.id ? null : m.id)}
                        className="cursor-pointer border-b border-line last:border-0 [&:last-child]:border-0">
                        <td className="py-2.5 pr-4 pl-5">
                          <span className="inline-flex items-center gap-2">
                            <ChevronRight className={cx("size-3.5 text-subtle transition", open === m.id && "rotate-90")} strokeWidth={2.4} />
                            {m.name}
                            {m.warnings.map((w) => <Badge key={w} tone="warn" className="whitespace-nowrap">{w === "superseded_value" ? "revised earlier value" : w.replace(/_/g, " ")}</Badge>)}
                          </span>
                        </td>
                        <td className="num whitespace-nowrap px-4 py-2.5 text-right">{minus(m.v1_display)}</td>
                        <td className="num whitespace-nowrap px-4 py-2.5 text-right font-medium">{minus(m.v2_display)}</td>
                        <td className="num whitespace-nowrap py-2.5 pr-5 pl-4 text-right"><Delta m={m} /></td>
                      </tr>
                      {open === m.id && (
                        <tr className="border-b border-line bg-canvas/60">
                          <td colSpan={4} className="px-5 py-3">
                            <div className="t-caption mb-2 font-medium text-muted">XBRL facts behind this row</div>
                            <div className="grid gap-2 sm:grid-cols-2">
                              {m.facts.map((f, i) => (
                                <a key={i} href={f.url} target="_blank" rel="noreferrer"
                                  className="flex items-center justify-between gap-3 rounded-xl bg-surface px-3 py-2 shadow-[0_0_0_1px_var(--color-line)] hover:shadow-[0_0_0_1px_var(--color-line-strong)]">
                                  <span className="min-w-0">
                                    <span className="t-foot font-medium">{f.fy}</span>
                                    {f.component_of && <span className="t-foot text-muted"> · {f.metric.replace(/_/g, " ")}</span>}
                                    <span className="block truncate font-mono text-[11px] text-muted">{f.concept} · {f.accession}</span>
                                  </span>
                                  <span className="num t-foot shrink-0">{f.value.toLocaleString()} <span className="text-muted">{f.unit}</span></span>
                                </a>
                              ))}
                            </div>
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </Group>
        );
      })}
    </div>
  );
}

function Revised({ data }: { data: Comparison }) {
  const revised = data.revisions.filter((r) => r.status === "revised");
  const other = data.revisions.length - revised.length;
  return (
    <div className="mx-auto max-w-[760px] space-y-3">
      {revised.length === 0 ? (
        <Card className="t-callout px-6 py-10 text-center">The {data.to_fy} 10-K shows every {data.from_fy} figure as first reported.</Card>
      ) : (
        <Group title={`${data.from_fy} figures the ${data.to_fy} 10-K presents differently`}>
          {revised.map((r) => (
            <Row key={r.metric}>
              <div className="flex flex-wrap items-center gap-x-6 gap-y-2 px-5 py-4">
                <div className="min-w-[220px] flex-1">
                  <div className="t-callout font-medium">{r.name}</div>
                  <div className="t-caption mt-0.5 text-warn">Restated{r.cause ? ` · ${r.cause}` : ""}</div>
                </div>
                <div className="flex items-center gap-3">
                  {r.first && (
                    <a href={r.first.url} target="_blank" rel="noreferrer" className="group text-right">
                      <div className="num t-callout text-muted line-through">{minus(r.first.display)}</div>
                      <div className="t-caption text-muted group-hover:text-accent">first reported {r.first.filed}</div>
                    </a>
                  )}
                  <ArrowRight className="size-4 text-subtle" />
                  {r.now && (
                    <a href={r.now.url} target="_blank" rel="noreferrer" className="group">
                      <div className="num t-headline">{minus(r.now.display)}</div>
                      <div className="t-caption text-muted group-hover:text-accent">in the {data.to_fy} 10-K</div>
                    </a>
                  )}
                </div>
              </div>
            </Row>
          ))}
        </Group>
      )}
      {other > 0 && <p className="t-foot px-1 text-muted">{other} other {data.from_fy} figures are unchanged or had no earlier filing to compare with.</p>}
    </div>
  );
}

const LABEL: Record<Para["label"], { text: string; tone: "add" | "del" | "accent" }> = {
  added: { text: "Added", tone: "add" }, removed: { text: "Removed", tone: "del" }, modified: { text: "Modified", tone: "accent" },
};

function Risk({ data, busy, onRun }: { data: Comparison; busy: boolean; onRun: () => void }) {
  const [filter, setFilter] = useState<"all" | Para["label"]>("all");
  if (data.item1a === null) {
    return (
      <Card className="mx-auto flex max-w-[640px] flex-col items-center gap-4 px-8 py-12 text-center">
        <FileDiff className="size-8 text-subtle" strokeWidth={1.5} />
        <div className="t-headline">Risk factors not compared yet</div>
        <p className="t-foot max-w-[440px]">
          Code lines up the Item 1A paragraphs of the two filings, and the local model labels each changed one. This takes a few minutes;
          the result is saved for next time.
        </p>
        <Button onClick={onRun} disabled={busy}>{busy ? <Spinner /> : <Play className="size-3.5" fill="currentColor" />}{busy ? "Comparing…" : "Compare risk factors"}</Button>
      </Card>
    );
  }
  const counts: Record<string, number> = { all: data.item1a.length, added: 0, removed: 0, modified: 0 };
  data.item1a.forEach((p) => counts[p.label]++);
  const shown = data.item1a.filter((p) => filter === "all" || p.label === filter);
  return (
    <div className="mx-auto max-w-[860px] space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Segmented size="sm" value={filter} onChange={setFilter} options={(["all", "added", "removed", "modified"] as const).map((k) => ({
          value: k, label: <>{k === "all" ? "All" : LABEL[k].text} <span className="num text-muted">{counts[k]}</span></> }))} />
      </div>
      <div className="t-foot flex gap-2 px-1 text-muted">
        <Info className="mt-0.5 size-3.5 shrink-0" />
        <span>Labels come from a local model. On companies held out from development it still flagged about a quarter of wording-only
          edits as material, so read the paragraph before relying on a label.</span>
      </div>
      {shown.map((p, i) => <ParaCard key={i} p={p} />)}
    </div>
  );
}

function ParaCard({ p }: { p: Para }) {
  const [side, setSide] = useState(false);
  const l = LABEL[p.label];
  return (
    <Card className="px-5 py-4">
      <div className="flex items-start gap-3">
        <Badge tone={l.tone} className="mt-0.5">{l.text}</Badge>
        <p className="t-callout flex-1">{p.reason}</p>
        {p.label === "modified" && p.diff && (
          <button onClick={() => setSide((s) => !s)} className="t-foot shrink-0 text-accent hover:underline">{side ? "Inline" : "Side by side"}</button>
        )}
      </div>
      <div className="mt-3 text-[14px] leading-[1.6]">
        {p.label === "added" && <p className="rounded-xl bg-add-soft/50 px-4 py-3">{p.later}</p>}
        {p.label === "removed" && <p className="rounded-xl bg-del-soft/50 px-4 py-3 line-through decoration-del/50">{p.earlier}</p>}
        {p.label === "modified" && !side && p.diff && (
          <p className="rounded-xl bg-canvas px-4 py-3">
            {p.diff.map((s, i) => s.op === "same" ? <span key={i}>{s.text}</span>
              : s.op === "added" ? <ins key={i} className="rounded bg-add-soft text-add no-underline">{s.text}</ins>
              : <del key={i} className="rounded bg-del-soft text-del decoration-del/50">{s.text}</del>)}
          </p>
        )}
        {p.label === "modified" && !p.diff && (
          <>
            <p className="rounded-xl bg-canvas px-4 py-3">{p.later ?? p.earlier}</p>
            <p className="t-caption mt-1.5 px-1 text-muted">No single matching paragraph in the earlier 10-K; the text was likely moved or merged.</p>
          </>
        )}
        {p.label === "modified" && side && p.diff && (
          <div className="grid gap-3 md:grid-cols-2">
            <div><div className="t-caption mb-1 font-medium text-muted">Earlier 10-K</div><p className="rounded-xl bg-canvas px-4 py-3">{p.earlier}</p></div>
            <div><div className="t-caption mb-1 font-medium text-muted">Later 10-K</div><p className="rounded-xl bg-canvas px-4 py-3">{p.later}</p></div>
          </div>
        )}
      </div>
    </Card>
  );
}
