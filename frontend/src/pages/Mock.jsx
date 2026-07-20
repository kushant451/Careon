import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import { Badge, Card, Spinner, diffTone } from "../components/ui";

const WAVE_HEIGHTS = [20, 55, 85, 40, 70, 30, 90, 55, 35, 75, 45, 80];

export default function Mock() {
  const { setInterviewStarted } = useApp();
  const navigate = useNavigate();
  const [state, setState] = useState(null);
  const [answer, setAnswer] = useState("");
  const [now, setNow] = useState(Date.now() / 1000);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const tickRef = useRef(null);

  const load = useCallback(async () => {
    try {
      const s = await api.getInterview();
      setState(s);
      setAnswer("");
      if (s.done) {
        await api.endInterview();
        navigate("/report");
      }
    } catch (e) {
      setError(e.message);
    }
  }, [navigate]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    tickRef.current = setInterval(() => setNow(Date.now() / 1000), 1000);
    return () => clearInterval(tickRef.current);
  }, []);

  if (!state) return <Spinner label="Loading interview..." />;

  if (!state.total) {
    return (
      <div>
        <div className="alert alert-warn">No questions loaded. Please generate questions first.</div>
        <button className="btn" onClick={() => navigate("/questions")}>
          ← Go to Question Generator
        </button>
      </div>
    );
  }

  const { index, total, question, role, personalized, q_start_time } = state;
  const prog = Math.round((index / total) * 100);
  const elapsed = Math.max(0, Math.floor(now - (q_start_time || now)));
  const remaining = Math.max(0, 120 - elapsed);
  const mins = String(Math.floor(remaining / 60)).padStart(2, "0");
  const secs = String(remaining % 60).padStart(2, "0");
  const tc = remaining > 30 ? "var(--accent)" : remaining > 10 ? "var(--yellow)" : "var(--red)";

  const handleEnd = async () => {
    setInterviewStarted(true);
    await api.endInterview();
    navigate("/report");
  };

  const handleSubmit = async () => {
    if (!answer.trim()) {
      setError("Please write an answer before submitting.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await api.submitAnswer(index, answer);
      setInterviewStarted(true);
      navigate("/evaluation");
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleSkip = async () => {
    setInterviewStarted(true);
    await api.endInterview();
    navigate("/report");
  };

  return (
    <div>
      <div className="row" style={{ alignItems: "flex-start" }}>
        <div style={{ flex: 3 }}>
          <h1 className="page-title">Mock Interview</h1>
          <p className="page-subtitle">
            {role}
            {personalized ? "  ✨ Personalized" : ""}
          </p>
        </div>
        <div style={{ flex: 1, textAlign: "right" }}>
          <button className="btn" onClick={handleEnd}>
            ⏹ End Interview
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13.5, color: "var(--muted)", marginBottom: 6 }}>
          <span>
            Question {index + 1} of {total}
          </span>
          <span>{prog}% complete</span>
        </div>
        <div className="prog-bar">
          <div className="prog-fill" style={{ width: `${prog}%` }} />
        </div>
      </div>

      <Card>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <div style={{ display: "flex", gap: 8 }}>
            <Badge>{question?.category || "Technical"}</Badge>
            <Badge tone={diffTone(question?.difficulty)}>{question?.difficulty || "Medium"}</Badge>
          </div>
          <div
            style={{
              background: "var(--card-flat)",
              border: "1px solid var(--border-strong)",
              borderRadius: 12,
              padding: "8px 18px",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: 11.5, color: "var(--muted)", textTransform: "uppercase", letterSpacing: ".5px" }}>
              Time Left
            </div>
            <div style={{ fontSize: 27, fontWeight: 700, color: tc }}>
              {mins}:{secs}
            </div>
          </div>
        </div>
        <p style={{ fontSize: 19, fontWeight: 600, color: "var(--text)", lineHeight: 1.5, marginBottom: 12 }}>
          {question?.question}
        </p>
        <div className="waveform">
          {WAVE_HEIGHTS.map((h, i) => (
            <span key={i} style={{ height: `${h}%` }} />
          ))}
        </div>
      </Card>

      <div className="field">
        <label className="field-label">Your Answer</label>
        <textarea
          rows={6}
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Type your answer here. Be clear, concise and specific..."
        />
        <p style={{ fontSize: 13, color: "var(--muted)", marginTop: 6 }}>
          💡 Tip: Structure your answer as — explanation → example → takeaway.
        </p>
      </div>

      <div className="row row-2">
        <button className="btn btn-primary btn-block" onClick={handleSubmit} disabled={submitting}>
          {submitting ? "Evaluating..." : "📤 Submit Answer"}
        </button>
        <button className="btn btn-block" onClick={handleSkip}>
          ⏭ Skip to Report
        </button>
      </div>
      {submitting && <Spinner label="Evaluating your answer..." />}
    </div>
  );
}
