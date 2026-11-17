import { Fragment, useEffect, useMemo, useState } from "react";
import { CalendarRange, ChevronRight, Info } from "lucide-react";
import * as api from "../api";
import type { Meta, Peers } from "../types";
import { Badge, Card, ErrorNote, Group, Monogram, Segmented, Select, Spinner, cx, hashParams, setHashParams } from "./ui";

const fmtDate = (iso: string) => new Date(iso + "T00:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
const minus = (s: string) => s.replace(/^-/, "−").replace(/\$-/, "−$");
const STATEMENT_ORDER = ["Income statement", "Balance sheet", "Cash flow", "Ratios and derived"];
const WARN_LABEL: Record<string, string> = { restated: "revised since first reported", split_adjusted: "split-adjusted", scope: "broader line item" };

export function PeersView({ meta }: { meta: Meta | null }) {
  const [metric, setMetric] = useState(hashParams().get("m") ?? "operating_margin");
  const [fy, setFy] = useState(hashParams().get("fy") ?? "FY2024");
  const [data, setData] = useState<Peers | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function load(m = metric, y = fy) {
    setBusy(true); setErr(null); setHashParams("/companies", { m, fy: y });
    try { setData(await api.peers({ metric: m, fy: y })); } catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  }
  useEffect(() => { load(); }, []);   // first view

  const groups = useMemo(() => STATEMENT_ORDER.map((g) => [g, (meta?.metrics ?? []).filter((m) => m.statement === g)] as const), [meta]);

  return (
    <div className="mx-auto max-w-[1120px] px-5 pt-10 pb-16">
      <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="text-[13px] font-semibold text-accent">Compare companies</div>
          <h1 className="t-large">{data?.name ?? "…"}</h1>
          {data && <div className="t-callout mt-1">Fiscal {data.fy.slice(2)} at all eight companies{data.formula ? ` · ${data.formula.replace(/_/g, " ")}` : ""}</div>}
        </div>
        <div className="flex items-center gap-2">
          <Select aria-label="Metric" value={metric} className="w-64" onChange={(e) => { setMetric(e.target.value); load(e.target.value, fy); }}>
            {groups.map(([g, ms]) => ms.length ? <optgroup key={g} label={g}>{ms.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}</optgroup> : null)}
          </Select>
          <Segmented value={fy} onChange={(v) => { setFy(v); load(metric, v); }} options={(meta?.years ?? ["FY2023", "FY2024", "FY2025"]).map((y) => ({ value: y, label: y }))} />
        </div>
      </div>

      {err && <div className="mt-8"><ErrorNote>{err}</ErrorNote></div>}
      {!data && busy && <div className="t-callout mt-12 flex items-center gap-2 text-muted"><Spinner />Looking up eight filings</div>}

      {data && (
        <div className={cx("mt-8 space-y-8 transition-opacity", busy && "opacity-40")}>
          {!data.aligned && data.earliest_end && data.latest_end && (
            <Card className="flex gap-3 px-5 py-4">
              <CalendarRange className="mt-0.5 size-5 shrink-0 text-warn" strokeWidth={2} />
              <div>
                <div className="t-callout font-semibold">“{data.fy}” covers different twelve months at each company</div>
                <div className="t-foot mt-0.5">
                  The fiscal years end between {fmtDate(data.earliest_end)} and {fmtDate(data.latest_end)}, {data.gap_days} days apart.
                  Compare with that in mind; the timeline below shows each period.
                </div>
              </div>
            </Card>
          )}
          {!data.comparable && (
            <Card className="flex gap-3 px-5 py-4">
              <Info className="mt-0.5 size-5 shrink-0 text-accent" strokeWidth={2} />
              <div className="t-foot">
                <span className="font-semibold">Shown side by side, not ranked.</span> Per-share figures and share counts depend on each
                company's share count and stock splits, so the engine does not compare them across companies.
              </div>
            </Card>
          )}
          <Values data={data} />
          <Timeline data={data} />
        </div>
      )}
    </div>
  );
}

function Values({ data }: { data: Peers }) {
  const [open, setOpen] = useState<string | null>(null);
  const rows = [...data.rows].sort((a, b) =>
    data.comparable ? (b.value ?? -Infinity) - (a.value ?? -Infinity) : a.company.localeCompare(b.company));
  const vals = rows.map((r) => r.value).filter((v): v is number => v !== null);
  const max = Math.max(0, ...vals), min = Math.min(0, ...vals);
  const span = max - min || 1;
  const zero = (-min / span) * 100;
  return (
    <Group title={data.comparable ? "Ranked by value" : "Values"} aside={`${vals.length} of 8 reported`}>
      {rows.map((r) => (
        <Fragment key={r.ticker}>
          <button onClick={() => setOpen(open === r.ticker ? null : r.ticker)}
            className="relative grid w-full grid-cols-[minmax(0,220px)_1fr_auto] items-center gap-4 px-4 py-3 text-left">
            <span className="flex min-w-0 items-center gap-3">
              <Monogram ticker={r.ticker} size={30} />
              <span className="min-w-0">
                <span className="t-callout block truncate font-semibold">{r.company}</span>
                <span className="t-caption block text-muted">{r.period_end ? `Year ended ${fmtDate(r.period_end)}` : r.ticker}</span>
              </span>
            </span>
            <span className="relative h-2 rounded-full bg-fill">
              {data.comparable && r.value !== null && (
                <>
                  <span className="absolute top-[-3px] h-[14px] w-px bg-line-strong" style={{ left: `${zero}%` }} />
                  <span className={cx("absolute top-0 h-2 rounded-full", r.value < 0 ? "bg-bad/70" : "bg-accent-fill")}
                    style={r.value >= 0 ? { left: `${zero}%`, width: `${(r.value / span) * 100}%` } : { right: `${100 - zero}%`, width: `${(-r.value / span) * 100}%` }} />
                </>
              )}
            </span>
            <span className="flex min-w-[150px] items-center justify-end gap-2">
              {r.weeks53 && <Badge>53 weeks</Badge>}
              {r.warnings.map((w) => <Badge key={w} tone="warn" className="whitespace-nowrap">{WARN_LABEL[w] ?? w.replace(/_/g, " ")}</Badge>)}
              {r.value !== null
                ? <span className="num t-headline">{minus(r.display ?? "")}</span>
                : <span className="t-foot text-muted">{r.outcome === "not_reported" ? "Not reported in XBRL" : r.outcome.replace(/_/g, " ")}</span>}
              <ChevronRight className={cx("size-4 text-subtle transition", open === r.ticker && "rotate-90")} strokeWidth={2.2} />
            </span>
            <span aria-hidden className="row-sep pointer-events-none absolute right-0 bottom-0 left-[60px] h-px bg-line" />
          </button>
          {open === r.ticker && (
            <div className="border-b border-line bg-canvas/60 px-4 py-3">
              {r.facts.length ? (
                <div className="grid gap-2 sm:grid-cols-2">
                  {r.facts.map((f, i) => (
                    <a key={i} href={f.url} target="_blank" rel="noreferrer"
                      className="flex items-center justify-between gap-3 rounded-xl bg-surface px-3 py-2 shadow-[0_0_0_1px_var(--color-line)] hover:shadow-[0_0_0_1px_var(--color-line-strong)]">
                      <span className="min-w-0">
                        <span className="t-foot font-medium">{f.metric.replace(/_/g, " ")}</span>
                        <span className="block truncate font-mono text-[11px] text-muted">{f.concept} · filed {f.filed}</span>
                      </span>
                      <span className="num t-foot shrink-0">{f.value.toLocaleString()} <span className="text-muted">{f.unit}</span></span>
                    </a>
                  ))}
                </div>
              ) : <div className="t-foot">No XBRL fact for this line item in the company's filings; the engine does not guess a substitute.</div>}
            </div>
          )}
        </Fragment>
      ))}
    </Group>
  );
}

function Timeline({ data }: { data: Peers }) {
  const rows = data.rows.filter((r) => r.period_end);
  if (!rows.length) return null;
  const instant = rows.every((r) => !r.period_start);
  const day = (s: string) => new Date(s + "T00:00:00").getTime();
  const starts = rows.map((r) => day(r.period_start ?? r.period_end!));
  const ends = rows.map((r) => day(r.period_end!));
  const lo = new Date(Math.min(...starts)); lo.setDate(1);
  const hi = new Date(Math.max(...ends)); hi.setMonth(hi.getMonth() + 1, 1);
  const span = hi.getTime() - lo.getTime();
  const pos = (t: number) => ((t - lo.getTime()) / span) * 100;
  const ticks: Date[] = [];
  for (const d = new Date(lo); d <= hi; d.setMonth(d.getMonth() + 3)) ticks.push(new Date(d));
  const sorted = [...rows].sort((a, b) => day(a.period_end!) - day(b.period_end!));
  return (
    <Group title={instant ? "Balance-sheet dates" : "Periods covered"} aside={instant ? "values as of each fiscal year end" : "each bar is one fiscal year"}>
      <div className="px-4 pt-4 pb-3">
        <div className="relative ml-[120px] h-5">
          {ticks.map((t) => (
            <span key={t.getTime()} className="t-caption absolute -translate-x-1/2 text-muted" style={{ left: `${pos(t.getTime())}%` }}>
              {t.toLocaleDateString("en-US", { month: "short" })}{t.getMonth() === 0 || t.getTime() === ticks[0].getTime() ? ` ’${String(t.getFullYear()).slice(2)}` : ""}
            </span>
          ))}
        </div>
        <div className="space-y-2">
          {sorted.map((r) => {
            const s = pos(day(r.period_start ?? r.period_end!)), e = pos(day(r.period_end!));
            return (
              <div key={r.ticker} className="flex items-center">
                <span className="t-foot w-[120px] shrink-0 truncate font-medium">{r.company}</span>
                <span className="relative h-5 flex-1">
                  {ticks.map((t) => <span key={t.getTime()} className="absolute top-0 h-5 w-px bg-line" style={{ left: `${pos(t.getTime())}%` }} />)}
                  {instant
                    ? <span className="absolute top-1/2 size-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-accent-fill" style={{ left: `${e}%` }} />
                    : <span className={cx("absolute top-1 h-3 rounded-full", r.weeks53 ? "bg-warn/70" : "bg-accent-fill/70")}
                        style={{ left: `${s}%`, width: `${Math.max(e - s, 0.5)}%` }} title={`${r.period_start} to ${r.period_end}`} />}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </Group>
  );
}


