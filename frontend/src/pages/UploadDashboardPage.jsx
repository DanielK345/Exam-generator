import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
const ALLOWED_EXTENSIONS = ["pdf", "pptx"];

function formatSize(size) {
  if (size >= 1024 * 1024) {
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  }
  return `${Math.max(1, Math.round(size / 1024))} KB`;
}

function UploadDashboardPage() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [folderMode, setFolderMode] = useState(false);
  const [slowNotice, setSlowNotice] = useState(false);
  const fileInputRef = useRef(null);
  const folderInputRef = useRef(null);
  const navigate = useNavigate();

  const isValidFile = (name) => {
    const ext = name.split(".").pop().toLowerCase();
    return ALLOWED_EXTENSIONS.includes(ext);
  };

  const addFiles = (newFiles) => {
    const fileArray = Array.from(newFiles);
    const valid = fileArray.filter((file) => isValidFile(file.name));
    const rejected = fileArray.length - valid.length;

    if (valid.length === 0) {
      setMessage({ type: "error", text: "Only PDF and PPTX files are supported for exam generation." });
      return;
    }

    setFiles((prev) => {
      const existing = new Set(prev.map((file) => `${file.name}_${file.size}`));
      const unique = valid.filter((file) => !existing.has(`${file.name}_${file.size}`));
      return [...prev, ...unique];
    });

    if (rejected > 0) {
      setMessage({
        type: "error",
        text: `${rejected} file(s) were skipped because they are not PDF or PPTX documents.`,
      });
    } else {
      setMessage(null);
    }
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, fileIndex) => fileIndex !== index));
  };

  const clearFiles = () => {
    setFiles([]);
    setMessage(null);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragging(false);
    if (event.dataTransfer.files.length > 0) {
      addFiles(event.dataTransfer.files);
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setMessage(null);
    setSlowNotice(false);

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    const slowTimer = setTimeout(() => setSlowNotice(true), 5000);

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 120000,
      });

      setMessage({ type: "success", text: response.data.message });
      setTimeout(() => {
        navigate(`/config/${response.data.document_id}`);
      }, 700);
    } catch (error) {
      if (error.code === "ECONNABORTED") {
        setMessage({ type: "error", text: "Upload timed out while the backend was waking up. Please try again." });
      } else if (!error.response) {
        setMessage({ type: "error", text: "The backend is unreachable right now. Give it a moment and retry." });
      } else {
        setMessage({ type: "error", text: error.response?.data?.detail || "Upload failed. Please try again." });
      }
    } finally {
      clearTimeout(slowTimer);
      setUploading(false);
      setSlowNotice(false);
    }
  };

  const openPicker = () => {
    if (folderMode) {
      folderInputRef.current?.click();
    } else {
      fileInputRef.current?.click();
    }
  };

  return (
    <div className="dashboard-layout">
      <aside className="dashboard-sidebar">
        <div className="sidebar-card sidebar-card-primary">
          <p className="eyebrow">Document Workflow</p>
          <h2>Welcome back, Curator.</h2>
          <p>
            Turn lecture slides, review packets, and reading notes into a polished exam flow with
            guided question generation and grading.
          </p>
        </div>

        <div className="sidebar-card">
          <div className="sidebar-stat-row">
            <div>
              <span className="sidebar-stat-label">Accepted types</span>
              <strong>PDF, PPTX</strong>
            </div>
            <div>
              <span className="sidebar-stat-label">Current queue</span>
              <strong>{files.length} files</strong>
            </div>
          </div>
          <div className="mini-chip-row">
            <span className="mini-chip">Lecture decks</span>
            <span className="mini-chip">Syllabi</span>
            <span className="mini-chip">Study guides</span>
          </div>
        </div>

        <div className="sidebar-card sidebar-note">
          <p className="sidebar-note-title">Recent Context Cards</p>
          <div className="context-card-grid">
            <div className="context-card">
              <strong>Auto chunking</strong>
              <span>Splits course content into retrieval-ready passages.</span>
            </div>
            <div className="context-card">
              <strong>Hybrid grading</strong>
              <span>Supports exact-match and LLM-evaluated short answers.</span>
            </div>
            <div className="context-card">
              <strong>Focus prompts</strong>
              <span>Target specific chapters or concept clusters.</span>
            </div>
          </div>
        </div>
      </aside>

      <section className="dashboard-main">
        <div className="hero-card">
          <div>
            <p className="eyebrow">Exam Builder</p>
            <h1>Configure your source material</h1>
            <p className="hero-copy">
              Upload one or more files, then tune the exam structure in the next step. The layout
              mirrors the Figma dashboard while preserving your current backend workflow.
            </p>
          </div>

          <div className="hero-actions">
            <button
              className={`mode-toggle ${!folderMode ? "active" : ""}`}
              onClick={() => setFolderMode(false)}
              type="button"
            >
              Select Files
            </button>
            <button
              className={`mode-toggle ${folderMode ? "active" : ""}`}
              onClick={() => setFolderMode(true)}
              type="button"
            >
              Select Folder
            </button>
          </div>
        </div>

        <div className="upload-board">
          <div
            className={`upload-dropzone ${dragging ? "dragging" : ""}`}
            onClick={openPicker}
            onDragLeave={() => setDragging(false)}
            onDragOver={(event) => {
              event.preventDefault();
              setDragging(true);
            }}
            onDrop={handleDrop}
            role="button"
            tabIndex={0}
          >
            <input
              accept=".pdf,.pptx"
              multiple
              onChange={(event) => {
                if (event.target.files.length > 0) addFiles(event.target.files);
                event.target.value = "";
              }}
              ref={fileInputRef}
              type="file"
            />
            <input
              accept=".pdf,.pptx"
              onChange={(event) => {
                if (event.target.files.length > 0) addFiles(event.target.files);
                event.target.value = "";
              }}
              ref={folderInputRef}
              type="file"
              // eslint-disable-next-line react/no-unknown-property
              webkitdirectory=""
            />

            <div className="upload-dropzone-icon">+</div>
            <h3>Drag and drop your study material</h3>
            <p>{`Click to ${folderMode ? "select a folder" : "browse files"} or drop documents here.`}</p>
            <span>Best results come from lecture decks, reading notes, and revision packs.</span>
          </div>

          <div className="upload-summary-row">
            <div className="summary-metric">
              <span>Queued</span>
              <strong>{files.length}</strong>
            </div>
            <div className="summary-metric">
              <span>Mode</span>
              <strong>{folderMode ? "Folder import" : "Multi-file import"}</strong>
            </div>
            <div className="summary-metric">
              <span>Status</span>
              <strong>{uploading ? "Uploading..." : "Ready"}</strong>
            </div>
          </div>
        </div>

        {files.length > 0 && (
          <div className="file-panel">
            <div className="file-panel-header">
              <div>
                <h3>Selected resources</h3>
                <p>Review and trim your upload queue before generating the exam configuration.</p>
              </div>
              <button className="text-action" onClick={clearFiles} type="button">
                Clear all
              </button>
            </div>

            <div className="file-grid">
              {files.map((file, index) => (
                <div className="file-card" key={`${file.name}_${file.size}`}>
                  <div>
                    <strong>{file.name}</strong>
                    <span>{formatSize(file.size)}</span>
                  </div>
                  <button onClick={() => removeFile(index)} type="button">
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="action-row">
          <button
            className="primary-pill-button"
            disabled={files.length === 0 || uploading}
            onClick={handleUpload}
            type="button"
          >
            {uploading ? "Uploading resources..." : "Continue to exam setup"}
          </button>
        </div>

        {uploading && slowNotice && (
          <div className="feedback-banner info">
            The server is waking up. The first request can take a little longer than usual.
          </div>
        )}

        {message && <div className={`feedback-banner ${message.type}`}>{message.text}</div>}
      </section>
    </div>
  );
}

export default UploadDashboardPage;
