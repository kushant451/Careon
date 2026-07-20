import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, triggerTextDownload } from "../api";
import { Badge, Card, EmptyState, ProgressBar, Spinner } from "../components/ui";

export default function Report() {
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([api.getReport(), api.getQuestions()])
      .then(([r, q]) => {
        setReport(r);
        setQuestions(q.questions || []);
      })
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="alert alert-error">{error}</div>;
  if (!report) return <Spinner label="Loading report..." />;

  if (report.attempted === 0) {
    return (
      <div>
        <h1 className="page-title">Final Interview Report</h1>
        <p className="page-subtitle">Overall performance in the interview</p>
        <EmptyState
          icon="📋"
          title="No interview data yet"
          desc="Complete a mock interview first to generate your report."
          action={
            <button className="btn btn-primary" onClick={() => navigate("/questions")}>
              Start Mock Interview →
            </button>
          }
        />
      </div>
    );
  }

  const os = report.overall_score;
  const lc = os >= 8 ? "#10B981" : os >= 6 ? "#E8896A" : "#F59E0B";

  const handleDownload = async () => {
    try {
      const text = await api.downloadReport();
      triggerTextDownload(text, "interview_report.txt");
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div>
      <h1 className="page-title">Final Interview Report</h1>
      <p className="page-subtitle">Overall performance in the interview</p>

      <Card style={{ textAlign: "center", padding: 36 }}>
        <div style={{ fontSize: 60, fontWeight: 800, color: lc, lineHeight: 1 }}>
          {os}
          <span style={{ fontSize: 25, color: "var(--muted)" }}>/10</span>
        </div>
        <div style={{ color: "var(--yellow)", fontSize: 22, letterSpacing: 2, margin: "8px 0" }}>{report.stars}</div>
        <div style={{ display: "flex", gap: 8, justifyContent: "center", margin: "10px 0" }}>
          <Badge>{report.performance_label}</Badge>
          {report.personalized && <Badge tone="cyan">✨ Personalized</Badge>}
          {report.role && <Badge tone="green">{report.role}</Badge>}
        </div>
        <p style={{ color: "var(--muted)", fontSize: 15, maxWidth: 520, margin: "16px auto 0", lineHeight: 1.9 }}>
          {report.summary}
        </p>
      </Card>

      <div className="row row-4">
        {[
          ["Total Questions", report.total_questions, "📝"],
          ["Attempted", report.attempted, "✏️"],
          ["Correct (≥6)", report.correct, "✅"],
          ["Accuracy", `${report.accuracy}%`, "🎯"],
        ].map(([lbl, val, icon]) => (
          <Card key={lbl} style={{ textAlign: "center" }}>
            <div style={{ fontSize: 25, marginBottom: 6 }}>{icon}</div>
            <div style={{ fontSize: 31, fontWeight: 700, color: "var(--text)" }}>{val}</div>
            <div style={{ fontSize: 13.5, color: "var(--muted)" }}>{lbl}</div>
          </Card>
        ))}
      </div>

      <div className="row row-2">
        <Card>
          <div className="section-label">Score Breakdown</div>
          {Object.entries(report.breakdown || {}).map(([lbl, sc]) => {
            const pc = (sc / 10) * 100;
            const tone = sc >= 7 ? "green" : sc < 5 ? "yellow" : undefined;
            return (
              <div key={lbl} style={{ marginBottom: 14 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
                  <span style={{ fontSize: 15, color: "var(--muted)" }}>{lbl}</span>
                  <span style={{ fontSize: 15, color: "var(--text)", fontWeight: 600 }}>{sc}/10</span>
                </div>
                <ProgressBar pct={pc} tone={tone} />
              </div>
            );
          })}
        </Card>

        <Card>
          <div className="section-label">Resume Performance</div>
          {report.ats_score ? (
            <>
              <div style={{ marginBottom: 14 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
                  <span style={{ fontSize: 15, color: "var(--muted)" }}>ATS Resume Score</span>
                  <span style={{ fontSize: 15, color: "var(--text)", fontWeight: 600 }}>{report.ats_score}/100</span>
                </div>
                <ProgressBar pct={report.ats_score} tone={report.ats_score >= 70 ? "green" : undefined} />
              </div>
              <div style={{ marginBottom: 14 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
                  <span style={{ fontSize: 15, color: "var(--muted)" }}>Interview Score</span>
                  <span style={{ fontSize: 15, color: "var(--text)", fontWeight: 600 }}>{os}/10</span>
                </div>
                <ProgressBar pct={(os / 10) * 100} />
              </div>
              <div className="card-flat" style={{ textAlign: "center" }}>
                <div style={{ fontSize: 13.5, color: "var(--muted)", marginBottom: 4 }}>Combined Readiness</div>
                <div style={{ fontSize: 35, fontWeight: 700, color: "var(--accent)" }}>
                  {Math.round((os / 10) * 0.6 * 100 + (report.ats_score / 100) * 0.4 * 100)}%
                </div>
              </div>
            </>
          ) : (
            <p style={{ color: "var(--muted)", fontSize: 15 }}>Upload a resume to see combined score.</p>
          )}
        </Card>
      </div>

      {questions.length > 0 && (
        <Card>
          <div className="section-label">Q&amp;A Review</div>
          {questions.map((q, i) => {
            const ev = report.evaluations?.[i] ?? null;
            return (
              <div key={i} style={{ padding: "14px 0", borderBottom: "1px solid var(--border)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
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
                    }}
                  >
                    {i + 1}
                  </span>
                  <span style={{ fontWeight: 600, fontSize: 15, color: "var(--text)" }}>{q.question}</span>
                </div>
                <div style={{ display: "flex", gap: 8, alignItems: "center", paddingLeft: 36 }}>
                  {ev ? (
                    <>
                      <Badge tone={ev.score >= 7 ? "green" : ev.score >= 5 ? "yellow" : "red"}>{ev.score}/10</Badge>
                      <span style={{ fontSize: 13.5, color: "var(--muted)" }}>
                        {(ev.feedback || "").slice(0, 100)}…
                      </span>
                    </>
                  ) : (
                    <Badge tone="yellow">Not answered</Badge>
                  )}
                </div>
              </div>
            );
          })}
        </Card>
      )}

      <div className="row row-2">
        <button className="btn btn-primary btn-block" onClick={() => navigate("/questions")}>
          🔄 Practice Again
        </button>
        <button className="btn btn-block" onClick={handleDownload}>
          ⬇️ Download Report
        </button>
      </div>
    </div>
  );
}
