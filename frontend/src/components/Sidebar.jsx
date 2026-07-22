import { NavLink, useNavigate } from "react-router-dom";
import { useApp } from "../context/AppContext";

const NAV = [
  { to: "/", icon: "🏠", label: "Home" },
  { to: "/ats", icon: "📄", label: "ATS Checker" },
  { to: "/analysis", icon: "📊", label: "Resume Analysis" },
  { to: "/career", icon: "🧭", label: "Career Recommendation" },
  { to: "/roadmap", icon: "🗺️", label: "Learning Roadmap" },
  { to: "/jobmatch", icon: "🎯", label: "Job Match Analyzer" },
  { to: "/questions", icon: "💬", label: "Question Generator" },
  { to: "/mock", icon: "🎤", label: "Mock Interview" },
  { to: "/report", icon: "📋", label: "Final Report" },
  { to: "/dashboard", icon: "📈", label: "Career Dashboard" },
];

export default function Sidebar({ open, onClose }) {
  const { doReset } = useApp();
  const navigate = useNavigate();

  const handleReset = async () => {
    await doReset();
    onClose?.();
    navigate("/");
  };

  return (
    <>
      {open && <div className="sidebar-overlay" onClick={onClose} />}

      <aside className={`sidebar${open ? " sidebar-open" : ""}`}>
        <div className="sidebar-brand">
          <div className="sidebar-logo">🤖</div>
          <div>
            <div className="sidebar-title">Careon</div>
            <div className="sidebar-subtitle">AI Career Assistant</div>
          </div>
          <button className="sidebar-close" onClick={onClose} aria-label="Close menu">
            ✕
          </button>
        </div>

        <nav className="nav-list">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              onClick={onClose}
              className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-pro">
          <div className="sidebar-pro-title">⭐ Pro Features</div>
          <div className="sidebar-pro-body">Unlimited mock interviews, AI feedback &amp; analytics.</div>
        </div>

        <button className="btn-reset" onClick={handleReset}>
          🔄 New Session
        </button>
      </aside>
    </>
  );
}