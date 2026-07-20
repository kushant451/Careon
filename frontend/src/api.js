const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function sessionId() {
  return localStorage.getItem("cp_session_id") || "";
}

export function setSessionId(id) {
  localStorage.setItem("cp_session_id", id);
}

async function request(path, options = {}) {
  const headers = {
    ...(options.body && !(options.body instanceof FormData)
      ? { "Content-Type": "application/json" }
      : {}),
    "X-Session-Id": sessionId(),
    ...(options.headers || {}),
  };

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail);
  }

  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return res.json();
  return res.text();
}

export async function ensureSession() {
  if (sessionId()) return sessionId();
  const { session_id } = await request("/api/session/new", { method: "POST" });
  setSessionId(session_id);
  return session_id;
}

export async function resetSession() {
  await request("/api/session/reset", { method: "POST" });
  localStorage.removeItem("cp_session_id");
  await ensureSession();
}

export const api = {
  meta: () => request("/api/meta"),

  uploadResume: (file, role) => {
    const form = new FormData();
    form.append("file", file);
    form.append("role", role);
    return request("/api/resume/upload", { method: "POST", body: form });
  },
  getResume: () => request("/api/resume"),

  recommendCareer: () => request("/api/career/recommend", { method: "POST" }),
  getCareer: () => request("/api/career"),

  generateRoadmap: (role, weeks) =>
    request("/api/roadmap/generate", {
      method: "POST",
      body: JSON.stringify({ role, weeks }),
    }),
  getRoadmap: () => request("/api/roadmap"),
  downloadRoadmap: () => request("/api/roadmap/download"),

  analyzeJobMatch: (role, job_description) =>
    request("/api/jobmatch/analyze", {
      method: "POST",
      body: JSON.stringify({ role, job_description }),
    }),
  getJobMatch: () => request("/api/jobmatch"),

  generateQuestions: (role, difficulty, count, personalized) =>
    request("/api/questions/generate", {
      method: "POST",
      body: JSON.stringify({ role, difficulty, count, personalized }),
    }),
  getQuestions: () => request("/api/questions"),
  downloadQuestions: () => request("/api/questions/download"),

  startInterview: () => request("/api/interview/start", { method: "POST" }),
  getInterview: () => request("/api/interview"),
  submitAnswer: (index, answer) =>
    request("/api/interview/answer", {
      method: "POST",
      body: JSON.stringify({ index, answer }),
    }),
  getCurrentEval: () => request("/api/interview/current-eval"),
  endInterview: () => request("/api/interview/end", { method: "POST" }),

  getReport: () => request("/api/report"),
  downloadReport: () => request("/api/report/download"),

  getDashboard: () => request("/api/dashboard"),
  getSkillGap: () => request("/api/skillgap"),
};

export function triggerTextDownload(text, filename) {
  const blob = new Blob([text], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export { sessionId };
