import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import Ring from "../components/Ring";
import { Badge, Card, Spinner } from "../components/ui";

export default function Home() {
  const { meta, resume, refreshResume, refreshProgress, interviewStarted, avgScore } = useApp();
  const [role, setRole] = useState(meta.roles[0] || "Software Engineer");
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const fileRef = useRef(null);
  const navigate = useNavigate();

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a PDF or DOCX file first.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      await api.uploadResume(file, role);
      await refreshResume();
      await refreshProgress();
      navigate("/ats");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const ats = resume?.ats_score || 0;
  let progressPct = 0;
  if (resume) {
    progressPct = 50;
    if (interviewStarted) progressPct += 30;
    if (avgScore > 0) progressPct += 20;
  }

  const atsColor = ats >= 70 ? "#10B981" : ats >= 50 ? "#F59E0B" : "#EF4444";
  const atsTone = ats >= 70 ? "green" : ats >= 50 ? "yellow" : "red";

  return (
    <div>
      <div style={{ textAlign: "center", padding: "18px 0 32px" }}>
        <div style={{ fontSize: 52, marginBottom: 8 }}>👋</div>
        <h1 style={{ color: "var(--text)", fontSize: 48, fontWeight: 800, margin: "0 0 10px" }}>
          Welcome back
        </h1>
        <p style={{ color: "var(--muted)", fontSize: 20, margin: 0 }}>Let&apos;s crack your dream job!</p>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="row" style={{ alignItems: "stretch" }}>
        <div style={{ flex: 3 }}>
          <Card>
            <div style={{ fontSize: 28, fontWeight: 700, color: "var(--text)", marginBottom: 6 }}>
              🎯 Your AI Interview Coach
            </div>
            <p style={{ color: "var(--muted)", fontSize: 20, marginBottom: 16 }}>
              Upload your resume, check ATS score, practice interviews and improve your skills.
            </p>

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
              <label className="field-label">Resume (PDF / DOCX)</label>
              <div className="upload-drop" onClick={() => fileRef.current?.click()}>
                <input
                  ref={fileRef}
                  type="file"
                  accept=".pdf,.docx"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                />
                {file ? `📎 ${file.name}` : "Click to choose a PDF or DOCX resume"}
              </div>
            </div>

            <button className="btn btn-primary btn-block" onClick={handleUpload} disabled={loading}>
              {loading ? "Analysing..." : "⬆️ Upload & Analyse Resume"}
            </button>
            {loading && <Spinner label="Analysing your resume..." />}
          </Card>
        </div>

        <div style={{ flex: 1, minWidth: 220 }}>
          <div className="card-flat" style={{ textAlign: "center", marginTop: 6 }}>
            <div
              style={{
                fontSize: 11.5,
                color: "var(--muted)",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: ".4px",
                marginBottom: 10,
              }}
            >
              Overall Progress
            </div>
            <Ring value={progressPct} max={100} size={90} color="#E8896A" sub="%" />
            <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 5 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12.5, color: "var(--muted)" }}>
                <span>● ATS</span>
                <span style={{ color: "var(--text)", fontWeight: 600 }}>{ats}/100</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12.5, color: "var(--muted)" }}>
                <span>● Score</span>
                <span style={{ color: "var(--text)", fontWeight: 600 }}>{avgScore}/10</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="divider" />

      <div className="row row-3">
        <Card>
          <div className="section-label">ATS Score</div>
          <div style={{ fontSize: 31, fontWeight: 700, color: atsColor, marginBottom: 8 }}>
            {ats}
            <span style={{ fontSize: 15, color: "var(--muted)" }}>/100</span>
          </div>
          <Badge tone={atsTone}>{resume?.score_label || "Upload resume first"}</Badge>
          <div style={{ marginTop: 12 }}>
            {resume && (
              <button className="btn" onClick={() => navigate("/ats")}>
                View ATS Details →
              </button>
            )}
          </div>
        </Card>

        <Card>
          <div className="section-label">Mock Score</div>
          <div style={{ fontSize: 31, fontWeight: 700, color: "var(--accent)", marginBottom: 8 }}>
            {avgScore}
            <span style={{ fontSize: 15, color: "var(--muted)" }}>/10</span>
          </div>
          <Badge tone={interviewStarted ? "green" : "yellow"}>
            {interviewStarted ? "Completed" : "Not started"}
          </Badge>
          <div style={{ marginTop: 12 }}>
            {interviewStarted ? (
              <button className="btn" onClick={() => navigate("/report")}>
                View Report →
              </button>
            ) : (
              <button className="btn" onClick={() => navigate("/questions")}>
                Start Now →
              </button>
            )}
          </div>
        </Card>

        <Card>
          <div className="section-label">Quick Actions</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <button className="btn btn-block" onClick={() => navigate("/ats")}>📄 ATS Checker</button>
            <button className="btn btn-block" onClick={() => navigate("/questions")}>💬 Question Generator</button>
            <button className="btn btn-block" onClick={() => navigate("/mock")}>🎤 Mock Interview</button>
          </div>
        </Card>
      </div>
    </div>
  );
}
