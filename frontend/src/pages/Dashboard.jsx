import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { Badge, Card, ProgressBar, Spinner } from "../components/ui";
import Ring from "../components/Ring";

export default function Dashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getDashboard().then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="alert alert-error">{error}</div>;
  if (!data) return <Spinner label="Loading dashboard..." />;

  const rColor = data.readiness >= 70 ? "#10B981" : data.readiness >= 40 ? "#F59E0B" : "#EF4444";

  return (
    <div>
      <h1 className="page-title">Career Dashboard</h1>
      <p className="page-subtitle">Your overall placement readiness at a glance</p>

      <Card style={{ textAlign: "center", padding: 32 }}>
        <div className="section-label" style={{ justifyContent: "center" }}>Placement Readiness</div>
        <Ring value={data.readiness} max={100} size={150} color={rColor} sub="%" />
        <p style={{ fontSize: 12, color: "var(--muted)", marginTop: 8 }}>
          Calculated as: 25% Resume (ATS) + 35% Mock Interview + 20% Career Fit + 20% Job Match
        </p>
      </Card>

      <div className="row row-3">
        <Card>
          <div className="section-label">ATS Score</div>
          <div style={{ fontSize: 27, fontWeight: 700, color: "var(--text)" }}>{data.ats_score}/100</div>
          <ProgressBar pct={data.ats_score} tone={data.ats_score >= 70 ? "green" : undefined} />
          {!data.ats_score && (
            <button className="btn" style={{ marginTop: 8 }} onClick={() => navigate("/")}>
              Upload Resume →
            </button>
          )}
        </Card>

        <Card>
          <div className="section-label">Mock Interview Avg</div>
          <div style={{ fontSize: 27, fontWeight: 700, color: "var(--text)" }}>{data.mock_avg}/10</div>
          <ProgressBar pct={(data.mock_avg / 10) * 100} />
          {!data.mock_attempted && (
            <button className="btn" style={{ marginTop: 8 }} onClick={() => navigate("/questions")}>
              Start Interview →
            </button>
          )}
        </Card>

        <Card>
          <div className="section-label">Job Match</div>
          <div style={{ fontSize: 27, fontWeight: 700, color: "var(--text)" }}>
            {data.job_match_percent != null ? `${data.job_match_percent}%` : "—"}
          </div>
          <ProgressBar pct={data.job_match_percent || 0} />
          {data.job_match_percent == null && (
            <button className="btn" style={{ marginTop: 8 }} onClick={() => navigate("/jobmatch")}>
              Analyze a JD →
            </button>
          )}
        </Card>
      </div>

      <div className="row row-2">
        <Card>
          <div className="section-label">Best-Fit Career Path</div>
          {data.top_career ? (
            <>
              <div style={{ fontSize: 20, fontWeight: 700, color: "var(--text)" }}>{data.top_career.title}</div>
              <Badge tone="green">{data.top_career.match_percent}% match</Badge>
              {data.top_career_matches?.slice(1).map((m) => (
                <div key={m.title} className="list-row">
                  {m.title} <Badge>{m.match_percent}%</Badge>
                </div>
              ))}
            </>
          ) : (
            <>
              <p style={{ color: "var(--muted)", fontSize: 15 }}>No career recommendation generated yet.</p>
              <button className="btn" onClick={() => navigate("/career")}>
                Get Recommendations →
              </button>
            </>
          )}
        </Card>

        <Card>
          <div className="section-label">Learning Roadmap</div>
          {data.roadmap_summary ? (
            <>
              <div style={{ fontSize: 20, fontWeight: 700, color: "var(--text)" }}>{data.roadmap_summary.role}</div>
              <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
                <Badge>{data.roadmap_summary.weeks} weeks</Badge>
                <Badge>{data.roadmap_summary.total_skills} skills</Badge>
                <Badge>{data.roadmap_summary.milestones} milestones</Badge>
              </div>
              <button className="btn" style={{ marginTop: 12 }} onClick={() => navigate("/roadmap")}>
                View Roadmap →
              </button>
            </>
          ) : (
            <>
              <p style={{ color: "var(--muted)", fontSize: 15 }}>No roadmap generated yet.</p>
              <button className="btn" onClick={() => navigate("/roadmap")}>
                Build Roadmap →
              </button>
            </>
          )}
        </Card>
      </div>
    </div>
  );
}