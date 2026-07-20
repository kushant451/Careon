import { useEffect, useState } from "react";
import { api, triggerTextDownload } from "../api";
import { useApp } from "../context/AppContext";
import { Badge, Card, EmptyState, Spinner, Tag } from "../components/ui";

export default function Roadmap() {
  const { meta, resume } = useApp();
  const defaultRole = resume?.role || meta.roles[0] || "Software Engineer";
  const [role, setRole] = useState(defaultRole);
  const [weeks, setWeeks] = useState(8);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getRoadmap().then((r) => r && setResult(r)).catch(() => {});
  }, []);

  const missing = resume?.missing_skills || [];

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await api.generateRoadmap(role, weeks);
      setResult(r);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      const text = await api.downloadRoadmap();
      triggerTextDownload(text, "learning_roadmap.txt");
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div>
      <h1 className="page-title">Learning Roadmap</h1>
      <p className="page-subtitle">A week-by-week plan to close your skill gaps</p>

      {error && <div className="alert alert-error">{error}</div>}

      <Card>
        <div className="row row-2">
          <div className="field">
            <label className="field-label">Target role</label>
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              {meta.roles.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label className="field-label">Roadmap length (weeks): {weeks}</label>
            <input
              type="range"
              min={2}
              max={16}
              value={weeks}
              onChange={(e) => setWeeks(Number(e.target.value))}
              style={{ width: "100%" }}
            />
          </div>
        </div>

        <p style={{ fontSize: 13, color: "var(--muted)", marginBottom: 12 }}>
          {missing.length
            ? `Using ${missing.length} missing skill(s) detected from your resume for the ${role} role.`
            : "No resume on file — the roadmap will use the core skill list for this role instead."}
        </p>

        <button className="btn btn-primary btn-block" onClick={handleGenerate} disabled={loading}>
          🗺️ Generate Roadmap
        </button>
        {loading && <Spinner label="Building your personalised roadmap..." />}
      </Card>

      {!result && !loading && (
        <EmptyState icon="🗺️" desc='Click "Generate Roadmap" to build your learning plan.' />
      )}

      {result && (
        <>
          <div style={{ display: "flex", gap: 10, alignItems: "center", margin: "14px 0" }}>
            <Badge tone="green">{result.weeks} Weeks</Badge>
            <Badge>{result.total_skills} Skills</Badge>
            {result.generated_by_ai ? <Badge tone="cyan">✨ AI Generated</Badge> : <Badge>Curated Plan</Badge>}
          </div>

          {(result.milestones || []).map((m) => (
            <Card key={m.week}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                <span
                  style={{
                    width: 30,
                    height: 30,
                    borderRadius: "50%",
                    background: "rgba(232,137,106,.2)",
                    color: "var(--accent)",
                    fontSize: 13.5,
                    fontWeight: 700,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  {m.week}
                </span>
                <span style={{ fontWeight: 700, fontSize: 16.5, color: "var(--text)" }}>{m.title}</span>
              </div>
              <div style={{ marginBottom: 10 }}>
                {m.skills?.length ? (
                  m.skills.map((s) => <Tag key={s}>{s}</Tag>)
                ) : (
                  <span style={{ color: "var(--muted)", fontSize: 13.5 }}>Review & practice</span>
                )}
              </div>
              {(m.tasks || []).map((t, i) => (
                <div key={i} style={{ padding: "4px 0", fontSize: 14, color: "var(--text)" }}>
                  ☐ {t}
                </div>
              ))}
              <div style={{ marginTop: 10 }}>
                {(m.resources || []).map((r) => (
                  <a key={r.skill} href={r.url} target="_blank" rel="noreferrer" style={{ fontSize: 13, marginRight: 10 }}>
                    🔗 {r.skill}
                  </a>
                ))}
              </div>
            </Card>
          ))}

          <button className="btn btn-block" onClick={handleDownload}>
            ⬇️ Download Roadmap
          </button>
        </>
      )}
    </div>
  );
}
