export function Card({ children, style, className = "" }) {
  return (
    <div className={`card ${className}`} style={style}>
      {children}
    </div>
  );
}

export function EmptyState({ icon, title, desc, action }) {
  return (
    <div className="card empty-state">
      <div className="icon">{icon}</div>
      <div className="title">{title}</div>
      {desc && <div className="desc">{desc}</div>}
      {action && <div style={{ marginTop: 16 }}>{action}</div>}
    </div>
  );
}

export function Badge({ tone = "accent", children }) {
  return <span className={`badge b-${tone}`}>{children}</span>;
}

export function Tag({ children, tone }) {
  return <span className={`tag ${tone === "red" ? "tag-red" : ""}`}>{children}</span>;
}

export function ProgressBar({ pct, tone }) {
  const fillClass = tone ? `p-${tone}` : "";
  return (
    <div className="prog-bar">
      <div className={`prog-fill ${fillClass}`} style={{ width: `${Math.max(0, Math.min(100, pct))}%` }} />
    </div>
  );
}

export function Spinner({ label = "Working..." }) {
  return (
    <div className="spinner-wrap">
      <span className="spinner" /> {label}
    </div>
  );
}

export function Alert({ tone = "info", children }) {
  return <div className={`alert alert-${tone}`}>{children}</div>;
}

export function diffTone(difficulty) {
  return { Easy: "green", Medium: "yellow", Hard: "red" }[difficulty] || "accent";
}
