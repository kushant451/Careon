import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import { Badge, Card, EmptyState, Spinner, Tag } from "../components/ui";
import Ring from "../components/Ring";

export default function JobMatch() {
  const { meta, resume } = useApp();
  const navigate = useNavigate();
  const [role, setRole] = useState(resume?.role || meta.roles[0] || "Software Engineer");
  const [jd, setJd] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!resume) {
    return (
      <div>
        <h1 className="page-title">Job Match Analyzer</h1>
        <p className="page-subtitle">Paste a job description to see how well your resume matches</p>
        <EmptyState
          icon="🎯"
          title="No resume uploaded yet"
          desc="Go to Home and upload a PDF or DOCX resume first."
          action={<button className="btn" onClick={() => navigate("/")}>← Back to Home</button>}
        />
      </div>
    );
  }

  const handleAnalyze = async () => {
    if (!jd.trim()) {
      setError("Please paste a job description first.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const r = await api.analyzeJobMatch(role, jd);
      setResult(r);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const pct = result?.match_percent || 0;
  const color = pct >= 75 ? "#10B981" : pct >= 50 ? "#E8896A" : pct >= 25 ? "#F59E0B" : "#EF4444";

  return (
    <div>
      <h1 className="page-title">Job Match Analyzer</h1>
      <p className="page-subtitle">Paste a job description to see how well your resume matches</p>

      {error && <div className="alert alert-error">{error}</div>}

      <Card>
        <div className="field">
          <label className="field-label">Role this job description is for</label>
          <select value={role} onChange={(e) => setRole(e.target.value)}>
            {meta.roles.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label className="field-label">Paste the job description here</label>
          <textarea
            rows={8}
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            placeholder="Paste the full job description text..."
          />
        </div>
        <button className="btn btn-primary btn-block" onClick={handleAnalyze} disabled={loading}>
          🎯 Analyze Match
        </button>
        {loading && <Spinner label="Comparing your resume against the job description..." />}
      </Card>

      {!result && !loading && (
        <EmptyState icon="🎯" desc='Paste a job description above and click "Analyze Match".' />
      )}

      {result && (
        <>
          <div className="row">
            <div style={{ flex: 1, minWidth: 160, display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
              <Ring value={pct} max={100} size={110} color={color} sub="/100" />
              <Badge tone={result.badge?.replace("b-", "") || "accent"}>{result.label}</Badge>
            </div>
            <div style={{ flex: 3 }}>
              <Card>
                <div style={{ fontWeight: 600, color: "var(--text)", marginBottom: 8 }}>Fit Summary</div>
                <p style={{ fontSize: 15, color: "var(--text)", lineHeight: 1.8 }}>{result.summary}</p>
              </Card>
            </div>
          </div>

          <div className="row row-2">
            <Card>
              <div className="section-label" style={{ color: "var(--green)" }}>✅ Matched Keywords</div>
              {result.matched_keywords?.length ? (
                result.matched_keywords.map((k) => <Tag key={k}>{k}</Tag>)
              ) : (
                <p style={{ color: "var(--muted)", fontSize: 15 }}>No overlapping keywords found.</p>
              )}
            </Card>
            <Card>
              <div className="section-label" style={{ color: "var(--red)" }}>❌ Missing Keywords</div>
              {result.missing_keywords?.length ? (
                result.missing_keywords.map((k) => (
                  <Tag key={k} tone="red">
                    {k}
                  </Tag>
                ))
              ) : (
                <p style={{ color: "var(--green)", fontSize: 15 }}>🎉 No missing keywords!</p>
              )}
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
