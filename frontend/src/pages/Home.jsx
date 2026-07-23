import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import { Card, Spinner } from "../components/ui";

export default function Home() {
  const { meta, refreshResume, refreshProgress } = useApp();
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

      <div style={{ maxWidth: 640, margin: "0 auto" }}>
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
    </div>
  );
}