import { useNavigate } from "react-router-dom";
import { useApp } from "../context/AppContext";
import { Badge, Card, EmptyState, Tag } from "../components/ui";
import Ring from "../components/Ring";

export default function Ats() {
  const { resume } = useApp();
  const navigate = useNavigate();

  if (!resume) {
    return (
      <div>
        <h1 className="page-title">ATS Resume Checker</h1>
        <p className="page-subtitle">Check how well your resume performs in ATS</p>
        <EmptyState
          icon="📄"
          title="No resume uploaded yet"
          desc="Go to Home and upload a PDF or DOCX resume."
          action={<button className="btn" onClick={() => navigate("/")}>← Back to Home</button>}
        />
      </div>
    );
  }

  const pct = resume.ats_score || 0;
  const color = pct >= 70 ? "#10B981" : pct >= 50 ? "#F59E0B" : "#EF4444";
  const tone = pct >= 70 ? "green" : pct >= 50 ? "yellow" : "red";
  const missing = resume.missing_skills || [];
  const hint = missing.length
    ? `Keywords like ${missing.slice(0, 3).join(", ")} are missing — adding them would push your score higher.`
    : "Great keyword coverage! Focus on measurable achievements.";

  return (
    <div>
      <h1 className="page-title">ATS Resume Checker</h1>
      <p className="page-subtitle">Check how well your resume performs in ATS</p>

      <div className="row">
        <div style={{ flex: 1, minWidth: 160, display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
          <Ring value={pct} max={100} size={110} color={color} sub="/100" />
          <Badge tone={tone}>{resume.score_label}</Badge>
        </div>
        <div style={{ flex: 3 }}>
          <Card>
            <div style={{ fontWeight: 600, color: "var(--text)", marginBottom: 8 }}>Score Explanation</div>
            <p style={{ fontSize: 15, color: "var(--muted)", lineHeight: 1.8 }}>
              Your resume scores <strong style={{ color: "var(--text)" }}>{pct}/100</strong> for ATS compatibility.{" "}
              {hint}
            </p>
          </Card>
        </div>
      </div>

      <div className="row row-3">
        <Card>
          <div className="section-label">Section Analysis</div>
          {Object.entries(resume.sections || {}).map(([sec, ok]) => (
            <div key={sec} className="list-row" style={{ color: ok ? "var(--text)" : "var(--muted)" }}>
              {ok ? "✅" : "❌"} {sec}
            </div>
          ))}
        </Card>

        <Card>
          <div className="section-label">Missing Keywords</div>
          {missing.length ? (
            missing.map((sk) => (
              <div key={sk} className="list-row">
                <span style={{ color: "var(--red)" }}>✗</span> {sk}
              </div>
            ))
          ) : (
            <p style={{ color: "var(--green)", fontSize: 15 }}>🎉 All key skills found!</p>
          )}
        </Card>

        <Card>
          <div className="section-label">Suggestions</div>
          {(resume.suggestions || []).map((tip, i) => (
            <div key={i} className="list-row" style={{ alignItems: "flex-start", fontSize: 13.5 }}>
              <span style={{ color: "var(--yellow)", flexShrink: 0 }}>●</span> {tip}
            </div>
          ))}
        </Card>
      </div>

      {(resume.found_skills || []).length > 0 && (
        <Card>
          <div className="section-label">Keywords found in your resume</div>
          {resume.found_skills.map((s) => (
            <Tag key={s}>{s}</Tag>
          ))}
        </Card>
      )}
    </div>
  );
}
