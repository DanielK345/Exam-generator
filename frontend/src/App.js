import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import ConfigPage from "./pages/ConfigPage";
import ExamPage from "./pages/ExamPage";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="App">
        <header className="app-header">
          <h1>Exam Generator</h1>
        </header>
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
