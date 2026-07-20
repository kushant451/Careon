import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import { Badge, Card, EmptyState, ProgressBar, Tag } from "../components/ui";

export default function Analysis() {
  const { resume } = useApp();
  const navigate = useNavigate();
  const [gap, setGap] = useState(null);

  useEffect(() => {
    if (!resume) return;
    api.getSkillGap().then(setGap).catch(() => setGap(null));
  }, [resume]);

  if (!resume) {
    return (
      <div>
        <h1 className="page-title">Resume Analysis</h1>
        <p className="page-subtitle">AI-powered resume analysis and insights</p>
        <EmptyState
          icon="📊"
          title="No resume uploaded"
          action={<button className="btn" onClick={() => navigate("/")}>← Back to Home</button>}
        />
      </div>
    );
  }

  const score10 = Math.round(((resume.ats_score || 0) / 10) * 10) / 10;

  return (
    <div>
      <h1 className="page-title">Resume Analysis</h1>
      <p className="page-subtitle">AI-powered resume analysis and insights</p>

      <div className="row row-2">
        <Card>
          <div className="section-label" style={{ color: "var(--green)" }}>✅ Strengths</div>
          {(resume.strengths || []).map((s, i) => (
            <div key={i} className="list-row" style={{ alignItems: "flex-start" }}>
              <span style={{ color: "var(--green)" }}>✓</span> {s}
            </div>
          ))}
        </Card>
        <Card>
          <div className="section-label" style={{ color: "var(--red)" }}>⚠️ Weaknesses</div>
          {(resume.weaknesses || []).map((w, i) => (
            <div key={i} className="list-row" style={{ alignItems: "flex-start" }}>
              <span style={{ color: "var(--red)" }}>✗</span> {w}
            </div>
          ))}
        </Card>
      </div>

      {(resume.top_skills || []).length > 0 && (
        <Card>
          <div className="section-label">Top Skills Found</div>
          {resume.top_skills.map((s) => (
            <Tag key={s}>⌨ {s}</Tag>
          ))}
        </Card>
      )}

      <Card>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <div className="section-label" style={{ marginBottom: 0 }}>Resume Summary</div>
          <Badge>Overall Score: {score10}/10</Badge>
        </div>
        <p style={{ fontSize: 15, color: "var(--text)", lineHeight: 1.8 }}>{resume.summary}</p>
      </Card>

      {gap && (
        <Card>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
            <div className="section-label" style={{ marginBottom: 0 }}>Skill Gap — {resume.role}</div>
            <Badge tone={gap.coverage_percent >= 70 ? "green" : "yellow"}>{gap.coverage_percent}% coverage</Badge>
          </div>
          <ProgressBar pct={gap.coverage_percent} tone={gap.coverage_percent >= 70 ? "green" : "yellow"} />
          {gap.gaps?.length > 0 && (
            <div style={{ marginTop: 14 }}>
              {gap.gaps.map((g) => (
                <div
                  key={g.skill}
                  style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "6px 0" }}
                >
                  <span>
                    <Badge tone={g.priority === "High" ? "red" : "yellow"}>{g.priority}</Badge>{" "}
                    <span style={{ color: "var(--text)", fontSize: 15, fontWeight: 500 }}>{g.skill}</span>
                  </span>
                  <a href={g.resource} target="_blank" rel="noreferrer" style={{ fontSize: 13.5 }}>
                    Learn →
                  </a>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}

      <div className="row row-2">
        <button className="btn btn-primary btn-block" onClick={() => navigate("/questions")}>
          💬 Generate Questions
        </button>
        <button className="btn btn-block" onClick={() => navigate("/")}>
          ⬆️ Re-upload Resume
        </button>
      </div>
    </div>
  );
}
