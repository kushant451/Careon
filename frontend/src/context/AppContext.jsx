import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, ensureSession, resetSession } from "../api";

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [ready, setReady] = useState(false);
  const [meta, setMeta] = useState({ roles: [], difficulty_levels: [] });
  const [resume, setResume] = useState(null);
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [evaluationsCount, setEvaluationsCount] = useState(0);
  const [avgScore, setAvgScore] = useState(0);

  const refreshResume = useCallback(async () => {
    try {
      const r = await api.getResume();
      setResume(r || null);
    } catch {
      setResume(null);
    }
  }, []);

  const refreshProgress = useCallback(async () => {
    try {
      const report = await api.getReport();
      setAvgScore(report.overall_score || 0);
      setEvaluationsCount(report.attempted || 0);
      if (report.attempted > 0) setInterviewStarted(true);
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    (async () => {
      await ensureSession();
      const m = await api.meta();
      setMeta(m);
      await refreshResume();
      await refreshProgress();
      setReady(true);
    })();
  }, [refreshResume, refreshProgress]);

  const doReset = useCallback(async () => {
    await resetSession();
    setResume(null);
    setInterviewStarted(false);
    setEvaluationsCount(0);
    setAvgScore(0);
  }, []);

  const value = {
    ready,
    meta,
    resume,
    setResume,
    refreshResume,
    interviewStarted,
    setInterviewStarted,
    evaluationsCount,
    avgScore,
    refreshProgress,
    doReset,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  return useContext(AppContext);
}
