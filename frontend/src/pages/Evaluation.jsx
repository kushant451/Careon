import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { Badge, Card, Spinner } from "../components/ui";
import Ring from "../components/Ring";

export default function Evaluation() {
  const navigate = useNavigate();
  const [cur, setCur] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getCurrentEval()
      .then((c) => {
        if (!c) {
          navigate("/mock");
          return;
        }
        setCur(c);
      })
      .catch(() => navigate("/mock"))
      .finally(() => setLoading(false));
  }, [navigate]);

  if (loading) return <Spinner label="Loading evaluation..." />;
  if (!cur) return null;

  const { question, answer, evaluation, idx, total } = cur;
  const score = evaluation.score || 0;
  const color = score >= 7 ? "#10B981" : score >= 5 ? "#F59E0B" : "#EF4444";
  const tone = score >= 7 ? "green" : score >= 5 ? "yellow" : "red";
  const lbl = score >= 7 ? "Good Answer" : score >= 5 ? "Average" : "Needs Work";
  const filled = Math.round(score / 2);
  const stars = "★".repeat(filled) + "☆".repeat(5 - filled);

  const handleNext = async () => {
    if (idx + 1 < total) {
      navigate("/mock");
    } else {
      await api.endInterview();
      navigate("/report");
    }
  };

  const handleEnd = async () => {
    await api.endInterview();
    navigate("/report");
  };

  return (
    <div>
      <h1 className="page-title">AI Evaluation</h1>
      <p className="page-subtitle">
        Question {idx + 1} of {total} · Your answer evaluation and feedback
      </p>

      <div className="row">
        <div style={{ flex: 1, minWidth: 160, display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
          <Ring value={score} max={10} size={100} color={color} sub="/10" />
          <div style={{ color: "var(--yellow)", fontSize: 18, letterSpacing: 2 }}>{stars}</div>
          <Badge tone={tone}>{lbl}</Badge>
        </div>
        <div style={{ flex: 3 }}>
          <Card>
            <div style={{ fontWeight: 600, color: "var(--text)", marginBottom: 8 }}>Detailed Feedback</div>
            <p style={{ fontSize: 15, color: "var(--text)", lineHeight: 1.9 }}>{evaluation.feedback}</p>
          </Card>
        </div>
      </div>

      <div className="row row-2">
        <Card>
          <div className="section-label" style={{ color: "var(--green)" }}>💪 Strengths</div>
          {(evaluation.strengths || []).map((s, i) => (
            <div key={i} className="list-row">
              <span style={{ color: "var(--green)" }}>✓</span> {s}
            </div>
          ))}
        </Card>
        <Card>
          <div className="section-label" style={{ color: "var(--yellow)" }}>📈 Areas to Improve</div>
          {(evaluation.improvements || []).map((im, i) => (
            <div key={i} className="list-row">
              <span style={{ color: "var(--yellow)" }}>↑</span> {im}
            </div>
          ))}
        </Card>
      </div>

      <Card>
        <div className="section-label">Question</div>
        <p style={{ fontWeight: 600, color: "var(--text)", marginBottom: 14 }}>{question.question}</p>
        <div className="section-label">Your Answer</div>
        <p style={{ fontSize: 15, color: "var(--muted)", lineHeight: 1.9 }}>{answer}</p>
      </Card>

      <div className="row row-2">
        <button className="btn btn-primary btn-block" onClick={handleNext}>
          {idx + 1 < total ? "Next Question →" : "📋 View Final Report"}
        </button>
        <button className="btn btn-block" onClick={handleEnd}>
          End & See Report
        </button>
      </div>
    </div>
  );
}
