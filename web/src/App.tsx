import { useEffect, useState } from "react";
import { BarChart3, GitCompareArrows, Github, MessageSquareText } from "lucide-react";
import { getMeta } from "./api";
import { AskView } from "./components/AskView";
import { CompareView } from "./components/CompareView";
import { PeersView } from "./components/PeersView";
import { cx } from "./components/ui";
import type { Meta } from "./types";

type View = "ask" | "peers" | "compare";
const route = () => location.hash.split("?")[0];
const fromHash = (): View => (route() === "#/compare" ? "compare" : route() === "#/companies" ? "peers" : "ask");

export default function App() {
  const [view, setView] = useState<View>(fromHash());
  const [meta, setMeta] = useState<Meta | null>(null);
  useEffect(() => {
    getMeta().then(setMeta).catch(() => setMeta(null));
    const f = () => { setView(fromHash()); scrollTo(0, 0); };
    addEventListener("hashchange", f);
    return () => removeEventListener("hashchange", f);
  }, []);

  return (
    <div className="flex min-h-full flex-col">
      <header className="material sticky top-0 z-30 border-b border-line/70">
        <div className="mx-auto grid h-12 max-w-[1120px] grid-cols-[1fr_auto_1fr] items-center px-5">
          <a href="#/" className="flex items-center gap-2 justify-self-start">
            <img src={`${import.meta.env.BASE_URL}favicon.svg`} alt="" className="size-[22px]" />
            <span className="text-[15px] font-semibold tracking-[-0.02em]">Filings QA</span>
          </a>
          <nav className="inline-flex h-8 rounded-[9px] bg-fill p-[2px]">
            {([["ask", "Ask", "#/", MessageSquareText], ["peers", "Companies", "#/companies", BarChart3], ["compare", "10-K changes", "#/compare", GitCompareArrows]] as const).map(([v, label, href, Icon]) => (
              <a key={v} href={href}
                className={cx("flex items-center rounded-[7px] px-3.5 text-[13px] font-medium transition-all",
                  view === v ? "bg-surface text-fg shadow-[0_1px_3px_rgba(0,0,0,0.12)]" : "text-muted hover:text-fg")}>
                <Icon className="mr-1.5 size-3.5" strokeWidth={2.2} />{label}
              </a>
            ))}
          </nav>
          <div className="flex items-center gap-4 justify-self-end">
            <span className="t-caption hidden text-muted lg:inline">Data as of {meta?.snapshot ?? "…"}</span>
            <a href="https://github.com/RuyiYan7301/sec-grounded-qa" target="_blank" rel="noreferrer" aria-label="Source on GitHub"
              className="text-muted transition hover:text-fg">
              <Github className="size-[18px]" strokeWidth={1.8} />
            </a>
          </div>
        </div>
      </header>
      <main className="flex-1">{view === "ask" ? <AskView meta={meta} /> : view === "peers" ? <PeersView meta={meta} /> : <CompareView meta={meta} />}</main>
      <footer>
        <div className="mx-auto max-w-[1120px] px-5">
          <div className="t-caption flex flex-wrap gap-x-6 gap-y-1 border-t border-line py-5 text-muted">
            <span>Apple, Microsoft, Nvidia, Oracle, Cisco, Broadcom, Intel and AMD · fiscal 2023–2025 · 28 annual GAAP metrics</span>
            <span>Figures from SEC EDGAR XBRL, narrative from 10-K text, on a local model.</span>
            <span>Not investment advice.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
