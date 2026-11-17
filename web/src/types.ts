export type Fact = {
  ticker: string; concept: string; label: string; period: string; value: number; unit: string; display: string;
  period_end: string; accession: string; form: string; filed: string; filing_fiscal_year: number | null; url: string;
  first_accession: string; first_filed: string; first_filing_fiscal_year: number | null; provenance: string; restated: boolean;
};
export type Source = { citation: string; chunk_id: string; accession: string; url: string; excerpt: string };
export type ToolCall = { tool: string; args: Record<string, unknown>; ok: boolean; summary: string };
export type Warning = { code: string; message: string; mentioned_in_answer: boolean | null };
export type Segment = { text: string; fact?: number };
export type Status = "verified" | "verified_with_warnings" | "traceable" | "unverified" | "withheld";

export type Answer = {
  question: string; answer: string; status: Status; status_label: string; status_text: string; model: string; mode: string;
  facts: Fact[]; sources: Source[]; tool_calls: ToolCall[]; checks: string[]; warnings: Warning[]; draft: string | null;
  latency_s: number; llm_calls: number; tokens: number; segments: Segment[];
};

export type Meta = {
  companies: { ticker: string; name: string }[]; years: string[]; target_years: string[];
  examples: { label: string; question: string }[]; models: string[]; default_model: string; snapshot: string;
};

export type FactRef = {
  fy: string; concept: string; value: number; unit: string; accession: string; filed: string | null; url: string;
  component_of: string | null; metric: string; display?: string;
};
export type MetricRow = {
  id: string; name: string; statement: string; unit: string | null; v1: number | null; v2: number | null;
  v1_display: string; v2_display: string; change_display: string; absolute_change: number | null;
  percent_change: number | null; pp_change: number | null; direction: string | null; size: string; rank: number;
  warnings: string[]; abstain_reason: string | null; facts: FactRef[];
};
export type Revision = {
  metric: string; name: string; period: string; status: string; cause: string | null;
  first: (FactRef & { display: string }) | null; now: (FactRef & { display: string }) | null;
};
export type Para = {
  label: "added" | "removed" | "modified"; reason: string; earlier: string | null; later: string | null;
  diff: { op: "same" | "added" | "removed"; text: string }[] | null;
};
export type Comparison = {
  ticker: string; company: string; from_fy: string; to_fy: string;
  target_filing: { accession: string; filed: string; url: string };
  summary: { large: number; revised: number; item1a: number | null };
  metrics: MetricRow[]; revisions: Revision[]; item1a: Para[] | null; item1a_method: string;
};
