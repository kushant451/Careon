import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, triggerTextDownload } from "../api";
import { useApp } from "../context/AppContext";
import { Badge, Card, EmptyState, Spinner, diffTone } from "../components/ui";

export default function Questions() {
  const { meta, resume, setInterviewStarted } = useApp();
  const navigate = useNavigate();
  const [role, setRole] = useState(resume?.role || meta.roles[0] || "Software Engineer");
  const [difficulty, setDifficulty] = useState("All Levels");
  const [count, setCount] = useState(10);
  const [questions, setQuestions] = useState([]);
  const [personalized, setPersonalized] = useState(false);
  const [loading, setLoading] = useState(null); // "generic" | "personalized" | null
  const [error, setError] = useState(null);

  const generate = async (isPersonalized) => {
    setLoading(isPersonalized ? "personalized" : "generic");
    setError(null);
    try {
      const r = await api.generateQuestions(role, difficulty, count, isPersonalized);
      setQuestions(r.questions);
      setPersonalized(r.personalized);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(null);
    }
  };

  const handleDownload = async () => {
    try {
      const text = await api.downloadQuestions();
      triggerTextDownload(text, "interview_questions.txt");
    } catch (e) {
      setError(e.message);
    }
  };

  const handleStartInterview = async () => {
    try {
      await api.startInterview();
      setInterviewStarted(true);
      navigate("/mock");
    } catch (e) {
      setError(e.message);
    }
  };

  const tech = questions.filter((q) => q.category === "Technical");
  const hr = questions.filter((q) => q.category === "HR");
  const proj = questions.filter((q) => q.category === "Project Based");

  return (
    <div>
      <h1 className="page-title">Question Generator</h1>
      <p className="page-subtitle">Generate interview questions based on your resume</p>

      {error && <div className="alert alert-error">{error}</div>}

      <Card>
        <div className="row row-3">
          <div className="field">
            <label className="field-label">Select Role</label>
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              {meta.roles.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label className="field-label">Difficulty Level</label>
            <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
              {meta.difficulty_levels.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label className="field-label">No. of Questions</label>
            <select value={count} onChange={(e) => setCount(Number(e.target.value))}>
              {[5, 10, 15, 20].map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="row row-2">
          <button className="btn btn-primary btn-block" onClick={() => generate(false)} disabled={loading !== null}>
            🔄 Generate Questions
          </button>
          {resume ? (
            <button className="btn btn-block" onClick={() => generate(true)} disabled={loading !== null}>
              ✨ Personalized from My Resume
            </button>
          ) : (
            <button className="btn btn-block" disabled>
              ✨ Personalized (upload resume first)
            </button>
          )}
        </div>
        {loading && <Spinner label={loading === "personalized" ? "Generating personalized questions..." : "Generating..."} />}
      </Card>

      {questions.length === 0 && !loading && (
        <EmptyState icon="💬" desc="Choose a role and click Generate Questions above." />
      )}

      {questions.length > 0 && (
        <>
          {personalized && (
            <div className="alert alert-info">
              ✨ Questions <strong>personalized from your resume</strong> — tailored to your exact skills and projects.
            </div>
          )}

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 14 }}>
            <Badge>All ({questions.length})</Badge>
            {tech.length > 0 && <Badge tone="cyan">Technical ({tech.length})</Badge>}
            {hr.length > 0 && <Badge tone="yellow">HR ({hr.length})</Badge>}
            {proj.length > 0 && <Badge>Project Based ({proj.length})</Badge>}
          </div>

          <Card>
            {questions.map((q, i) => (
              <div
                key={q.id ?? i}
                style={{ display: "flex", alignItems: "flex-start", gap: 12, padding: "12px 0", borderBottom: "1px solid var(--border)" }}
              >
                <span
                  style={{
                    width: 26,
                    height: 26,
                    borderRadius: "50%",
                    background: "rgba(232,137,106,.2)",
                    color: "var(--accent)",
                    fontSize: 12.5,
                    fontWeight: 700,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                    marginTop: 2,
                  }}
                >
                  {i + 1}
                </span>
                <span>
                  <span style={{ display: "block", fontSize: 15.5, color: "var(--text)", marginBottom: 6 }}>
                    {q.question}
                  </span>
                  <Badge>{q.category}</Badge> <Badge tone={diffTone(q.difficulty)}>{q.difficulty}</Badge>{" "}
                  {q.personalized && <Badge tone="cyan">✨</Badge>}
                </span>
              </div>
            ))}
          </Card>

          <div className="row row-2">
            <button className="btn btn-primary btn-block" onClick={handleStartInterview}>
              ▶️ Start Mock Interview
            </button>
            <button className="btn btn-block" onClick={handleDownload}>
              ⬇️ Download Questions
            </button>
          </div>
        </>
      )}
    </div>
  );
}
