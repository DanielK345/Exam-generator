import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import axios from "axios";
import UploadPage from "./pages/UploadPage";
import ConfigPage from "./pages/ConfigPage";
import ExamPage from "./pages/ExamPage";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [connStatus, setConnStatus] = useState("connecting"); // "connecting" | "connected" | "failed"
  const [allowedOrigins, setAllowedOrigins] = useState(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await axios.get(`${API_URL}/health`, { timeout: 120000 });
        if (response.data?.status === "ok") {
          setConnStatus("connected");
          setAllowedOrigins(response.data.allowed_origins || null);
        } else {
          setConnStatus("failed");
        }
      } catch {
        setConnStatus("failed");
      }
    };
    checkBackend();
  }, []);

  return (
    <Router>
      <div className="App">
        <header className="app-header">
          <h1>Exam Generator</h1>
        </header>
        {!dismissed && (
          <div className={`conn-banner conn-${connStatus}`}>
            <span>
              {connStatus === "connecting" && `Connecting to backend: ${API_URL} ...`}
              {connStatus === "connected" && `Connected to backend: ${API_URL}`}
              {connStatus === "failed" && `Failed to connect to backend: ${API_URL}`}
            </span>
            {connStatus === "connected" && allowedOrigins && (
              <span className="conn-origins">
                Allowed origins: {Array.isArray(allowedOrigins) ? allowedOrigins.join(", ") : allowedOrigins}
              </span>
            )}
            {connStatus !== "connecting" && (
              <button className="conn-dismiss" onClick={() => setDismissed(true)}>&times;</button>
            )}
          </div>
        )}
        <main className="app-main">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/config/:documentId" element={<ConfigPage />} />
            <Route path="/exam/:examId" element={<ExamPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
