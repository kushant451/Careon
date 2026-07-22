import { useState } from "react";
import { HashRouter, Routes, Route } from "react-router-dom";
import { AppProvider, useApp } from "./context/AppContext";
import Sidebar from "./components/Sidebar";
import { Spinner } from "./components/ui";

import Home from "./pages/Home";
import Ats from "./pages/Ats";
import Analysis from "./pages/Analysis";
import Career from "./pages/Career";
import Roadmap from "./pages/Roadmap";
import JobMatch from "./pages/JobMatch";
import Questions from "./pages/Questions";
import Mock from "./pages/Mock";
import Evaluation from "./pages/Evaluation";
import Report from "./pages/Report";
import Dashboard from "./pages/Dashboard";

function Shell() {
  const { ready } = useApp();
  const [navOpen, setNavOpen] = useState(false);

  if (!ready) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh" }}>
        <Spinner label="Starting Careon..." />
      </div>
    );
  }

  return (
    <div className="app-shell">
      <header className="mobile-topbar">
        <button className="mobile-menu-btn" onClick={() => setNavOpen(true)} aria-label="Open menu">
          ☰
        </button>
        <div className="mobile-topbar-title">
          <span className="mobile-topbar-logo">🤖</span> Careon
        </div>
      </header>

      <Sidebar open={navOpen} onClose={() => setNavOpen(false)} />

      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/ats" element={<Ats />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/career" element={<Career />} />
          <Route path="/roadmap" element={<Roadmap />} />
          <Route path="/jobmatch" element={<JobMatch />} />
          <Route path="/questions" element={<Questions />} />
          <Route path="/mock" element={<Mock />} />
          <Route path="/evaluation" element={<Evaluation />} />
          <Route path="/report" element={<Report />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <HashRouter>
      <AppProvider>
        <Shell />
      </AppProvider>
    </HashRouter>
  );
}