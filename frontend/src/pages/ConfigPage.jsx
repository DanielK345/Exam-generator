import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";

const API_URL = "http://localhost:8000";

function ConfigPage() {
  const { documentId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [config, setConfig] = useState({
    time_limit: 30,
    mcq: 5,
    true_false: 3,
    short_answer: 2,
    difficulty: "medium",
    focus: "",
  });

  const handleChange = (field, value) => {
    setConfig((prev) => ({ ...prev, [field]: value }));
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);

    try {
      const payload = {
        document_id: documentId,
        ...config,
        mcq: parseInt(config.mcq),
        true_false: parseInt(config.true_false),
        short_answer: parseInt(config.short_answer),
        time_limit: parseInt(config.time_limit),
        focus: config.focus || null,
      };

      const response = await axios.post(`${API_URL}/generate`, payload);
      navigate(`/exam/${response.data.exam_id}`);
    } catch (err) {
      const detail = err.response?.data?.detail || "Generation failed. Please try again.";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="config-container">
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>Generating your exam...</p>
          <p style={{ color: "#64748b", fontSize: "0.9rem", marginTop: 8 }}>
            This may take a moment while we analyze your document and create questions.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="config-container">
      <h2>Configure Your Exam</h2>

      <div className="form-row">
        <div className="form-group">
          <label>Time Limit (minutes)</label>
          <input
            type="number"
            min="5"
            max="180"
            value={config.time_limit}
            onChange={(e) => handleChange("time_limit", e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Difficulty</label>
          <select
            value={config.difficulty}
            onChange={(e) => handleChange("difficulty", e.target.value)}
          >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Multiple Choice Questions</label>
          <input
            type="number"
            min="0"
            max="20"
            value={config.mcq}
            onChange={(e) => handleChange("mcq", e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>True / False Questions</label>
          <input
            type="number"
            min="0"
            max="20"
            value={config.true_false}
            onChange={(e) => handleChange("true_false", e.target.value)}
          />
        </div>
      </div>

      <div className="form-group">
        <label>Short Answer Questions</label>
        <input
          type="number"
          min="0"
          max="10"
          value={config.short_answer}
          onChange={(e) => handleChange("short_answer", e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>Focus Area (optional)</label>
        <textarea
          rows="2"
          placeholder="e.g., chapter 2 and 3, machine learning basics..."
          value={config.focus}
          onChange={(e) => handleChange("focus", e.target.value)}
        />
      </div>

      {error && (
        <div className="status-message error">{error}</div>
      )}

      <div style={{ marginTop: 24, textAlign: "center" }}>
        <button className="btn btn-primary" onClick={handleGenerate}>
          Generate Exam
        </button>
      </div>
    </div>
  );
}

export default ConfigPage;
