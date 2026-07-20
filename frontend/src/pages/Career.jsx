import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import { Badge, Card, EmptyState, ProgressBar, Spinner, Tag } from "../components/ui";

export default function Career() {
  const { resume } = useApp();
  const navigate = useNavigate();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!resume) {
    return (
      <div>
        <h1 className="page-title">AI Career Recommendation</h1>
        <p className="page-subtitle">Discover the career paths that best fit your current skills</p>
        <EmptyState
          icon="🧭"
          title="No resume uploaded yet"
          desc="Go to Home and upload a PDF or DOCX resume to get personalised recommendations."
          action={<button className="btn" onClick={() => navigate("/")}>← Back to Home</button>}
        />
      </div>
    );
  }

  const handleRecommend = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await api.recommendCareer();
      setResult(r);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="page-title">AI Career Recommendation</h1>
      <p className="page-subtitle">Discover the career paths that best fit your current skills</p>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="row" style={{ alignItems: "center", marginBottom: 4 }}>
        <p style={{ color: "var(--muted)", fontSize: 15, flex: 3 }}>
          Uses the skills detected in your resume to rank the career paths you are best suited for right now.
        </p>
        <div style={{ flex: 1, minWidth: 200 }}>
          <button className="btn btn-primary btn-block" onClick={handleRecommend} disabled={loading}>
            🧭 Get Recommendations
          </button>
        </div>
      </div>
      {loading && <Spinner label="Analysing your skill profile..." />}

      {!result && !loading && (
        <EmptyState icon="🧭" desc='Click "Get Recommendations" to see your best-fit career paths.' />
      )}

      {result && (result.top_matches || []).length === 0 && (
        <div className="alert alert-info">{result.insight || "No recommendations available."}</div>
      )}

      {result && result.top_matches?.length > 0 && (
        <>
          <Card style={{ background: "rgba(232,137,106,.08)" }}>
            <div className="section-label" style={{ color: "var(--accent)" }}>✨ AI Insight</div>
            <p style={{ fontSize: 15.5, color: "var(--text)", lineHeight: 1.8 }}>{result.insight}</p>
          </Card>

          {result.top_matches.map((path, i) => {
            const pct = path.match_percent;
            const color = pct >= 70 ? "#10B981" : pct >= 40 ? "#E8896A" : "#F59E0B";
            const tone = pct >= 70 ? "green" : pct >= 40 ? "accent" : "yellow";
            return (
              <Card key={path.id || path.title}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, marginBottom: 6 }}>
                  <div>
                    <span style={{ fontSize: 19, fontWeight: 700, color: "var(--text)" }}>{path.title}</span>
                    {i === 0 && <Badge tone="green"> 🏆 Best Match</Badge>}
                    <div style={{ color: "var(--muted)", fontSize: 14, marginTop: 4 }}>{path.description}</div>
                  </div>
                  <div style={{ textAlign: "center", flexShrink: 0 }}>
                    <div style={{ fontSize: 27, fontWeight: 800, color }}>{pct}%</div>
                    <Badge tone={tone}>match</Badge>
                  </div>
                </div>
                <ProgressBar pct={pct} />
                <div style={{ display: "flex", gap: 14, marginTop: 10, flexWrap: "wrap" }}>
                  <Badge>Growth: {path.growth_outlook || "—"}</Badge>
                </div>
                <div style={{ marginTop: 12 }}>
                  <div className="section-label">Skills you have</div>
                  {path.matched_skills?.length ? (
                    path.matched_skills.map((s) => <Tag key={s}>✓ {s}</Tag>)
                  ) : (
                    <span style={{ color: "var(--muted)", fontSize: 13.5 }}>None yet</span>
                  )}
                </div>
                <div style={{ marginTop: 10 }}>
                  <div className="section-label">Skills to build</div>
                  {path.missing_skills?.length ? (
                    path.missing_skills.map((s) => (
                      <Tag key={s} tone="red">
                        {s}
                      </Tag>
                    ))
                  ) : (
                    <span style={{ color: "var(--green)", fontSize: 13.5 }}>All core skills covered 🎉</span>
                  )}
                </div>
              </Card>
            );
          })}

          <button className="btn btn-primary btn-block" onClick={() => navigate("/roadmap")}>
            🗺️ Build a Learning Roadmap for My Top Match
          </button>
        </>
      )}
    </div>
  );
}
