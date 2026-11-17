import type { ReactNode, SelectHTMLAttributes } from "react";
import { ChevronDown, Loader2 } from "lucide-react";

export const cx = (...c: (string | false | null | undefined)[]) => c.filter(Boolean).join(" ");

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cx("card", className)}>{children}</div>;
}

/** A titled group of rows, like a grouped inset list. */
export function Group({ title, aside, children, className }: { title?: ReactNode; aside?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={className}>
      {(title || aside) && (
        <div className="mb-2 flex items-baseline justify-between px-1">
          <h3 className="section-label">{title}</h3>
          {aside && <div className="t-foot text-muted">{aside}</div>}
        </div>
      )}
      <div className="card overflow-hidden">{children}</div>
    </section>
  );
}

/** A row inside a Group; hairline separator inset from the leading edge. */
export function Row({ children, className, onClick, inset = 16 }: { children: ReactNode; className?: string; onClick?: () => void; inset?: number }) {
  const C = onClick ? "button" : "div";
  return (
    <C onClick={onClick} className={cx("relative block w-full text-left", onClick && "transition active:bg-fill", className)}>
      {children}
      <span aria-hidden className="row-sep pointer-events-none absolute right-0 bottom-0 h-px bg-line" style={{ left: inset }} />
    </C>
  );
}

type Tone = "neutral" | "accent" | "warn" | "ok" | "bad" | "add" | "del";
const TONES: Record<Tone, string> = {
  neutral: "bg-fill text-muted",
  accent: "bg-accent-soft text-accent",
  warn: "bg-warn-soft text-warn",
  ok: "bg-ok-soft text-ok",
  bad: "bg-bad-soft text-bad",
  add: "bg-add-soft text-add",
  del: "bg-del-soft text-del",
};
export function Badge({ tone = "neutral", children, className }: { tone?: Tone; children: ReactNode; className?: string }) {
  return (
    <span className={cx("inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[12px] leading-4 font-medium", TONES[tone], className)}>
      {children}
    </span>
  );
}

export function Select({ label, children, className, ...p }: SelectHTMLAttributes<HTMLSelectElement> & { label?: string }) {
  return (
    <label className={cx("flex flex-col gap-1.5", className)}>
      {label && <span className="t-caption font-medium text-muted">{label}</span>}
      <span className="relative">
        <select {...p}
          className="h-9 w-full appearance-none rounded-[10px] bg-fill pl-3 pr-8 text-[14px] text-fg outline-none transition focus:ring-4 focus:ring-accent/20">
          {children}
        </select>
        <ChevronDown className="pointer-events-none absolute right-2.5 top-2.5 size-4 text-muted" strokeWidth={2.2} />
      </span>
    </label>
  );
}

export function Segmented<T extends string>({ label, value, options, onChange, size = "md" }: {
  label?: string; value: T; options: { value: T; label: ReactNode; hint?: string }[]; onChange: (v: T) => void; size?: "sm" | "md";
}) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <span className="t-caption font-medium text-muted">{label}</span>}
      <div className={cx("inline-flex rounded-[9px] bg-fill p-[2px]", size === "sm" ? "h-8" : "h-9")}>
        {options.map((o) => (
          <button key={o.value} type="button" title={o.hint} onClick={() => onChange(o.value)}
            className={cx("rounded-[7px] px-3 text-[13px] font-medium transition-all",
              value === o.value ? "bg-surface text-fg shadow-[0_1px_3px_rgba(0,0,0,0.12),0_0_0_0.5px_rgba(0,0,0,0.04)]" : "text-muted hover:text-fg")}>
            {o.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export function Button({ children, onClick, disabled, variant = "primary", className, type = "button" }: {
  children: ReactNode; onClick?: () => void; disabled?: boolean; variant?: "primary" | "secondary" | "plain";
  className?: string; type?: "button" | "submit";
}) {
  const v = {
    primary: "bg-accent-fill text-white hover:brightness-110 active:brightness-95",
    secondary: "bg-fill text-fg hover:brightness-95",
    plain: "text-accent hover:underline",
  }[variant];
  return (
    <button type={type} onClick={onClick} disabled={disabled}
      className={cx("inline-flex h-9 items-center justify-center gap-1.5 rounded-full px-[18px] text-[14px] font-medium transition disabled:cursor-not-allowed disabled:opacity-40", v, className)}>
      {children}
    </button>
  );
}

export const Spinner = ({ className }: { className?: string }) => <Loader2 className={cx("size-4 animate-spin", className)} />;

export function ErrorNote({ children }: { children: ReactNode }) {
  return <div className="card px-5 py-4 text-[14px] text-bad">{children}</div>;
}
