import { useEffect, useState, useRef } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [memories, setMemories] = useState([]);
  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState("");
  const [selectedMemory, setSelectedMemory] = useState(null);
  
  // Selection and Context Pack States
  const [selectedMemoryIds, setSelectedMemoryIds] = useState([]);
  const [contextPackText, setContextPackText] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoadingContextPack, setIsLoadingContextPack] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [copyFeedback, setCopyFeedback] = useState(false);

  // Background Capture & sensitive content states
  const [captureStatus, setCaptureStatus] = useState({ is_active: true, last_capture_time: null });
  const [pendingMemories, setPendingMemories] = useState([]);

  // Sensitive Content Confirmation Modal States (for manual captures)
  const [isSensitiveModalOpen, setIsSensitiveModalOpen] = useState(false);
  const [sensitiveReasonText, setSensitiveReasonText] = useState("");
  const [sensitiveMemoryId, setSensitiveMemoryId] = useState(null);

  // QA Modal Chat States
  const [isQaModalOpen, setIsQaModalOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    {
      role: "ai",
      content: "Hi! I am your Totem QA Assistant. Ask me anything about your captured desktop memories! (e.g. 'What was I working on recently?' or 'Which bugs did I solve?')"
    }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);

  // Ref to scroll chat messages container
  const chatMessagesEndRef = useRef(null);

  // Importance States
  const [importanceFilter, setImportanceFilter] = useState("all");
  const [animatingStarId, setAnimatingStarId] = useState(null);

  // Edit Memory States
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingMemory, setEditingMemory] = useState(null);
  const [editTitle, setEditTitle] = useState("");
  const [editSummary, setEditSummary] = useState("");
  const [isSavingEdit, setIsSavingEdit] = useState(false);
  const [editError, setEditError] = useState("");
  const [editSuccess, setEditSuccess] = useState("");

  // Navigation & Session States
  const [currentView, setCurrentView] = useState("dashboard"); // "dashboard", "sessions", "session-detail"
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [activeSessionDetail, setActiveSessionDetail] = useState(null);
  const [isLoadingSessionDetail, setIsLoadingSessionDetail] = useState(false);
  const [sessionSearch, setSessionSearch] = useState("");

  const API = "http://127.0.0.1:8000";

  // Load all memories
  const loadAllMemories = () => {
    axios
      .get(`${API}/memories`)
      .then((res) => {
        setMemories(res.data);
      })
      .catch((err) => console.log(err));
  };

  // Load background capture status
  const loadCaptureStatus = () => {
    axios
      .get(`${API}/capture/status`)
      .then((res) => {
        setCaptureStatus(res.data);
      })
      .catch((err) => console.log("Error loading capture status:", err));
  };

  // Load pending sensitive memories
  const loadPendingMemories = () => {
    axios
      .get(`${API}/memories/pending`)
      .then((res) => {
        setPendingMemories(res.data);
      })
      .catch((err) => console.log("Error loading pending memories:", err));
  };

  // Fetch sessions
  const loadSessions = () => {
    axios
      .get(`${API}/sessions`)
      .then((res) => {
        setSessions(res.data);
      })
      .catch((err) => console.error("Error fetching sessions:", err));
  };

  // Fetch session detail
  const viewSessionDetail = (id) => {
    setActiveSessionId(id);
    setIsLoadingSessionDetail(true);
    setCurrentView("session-detail");
    setActiveSessionDetail(null);
    setSessionSearch("");

    axios
      .get(`${API}/sessions/${id}`)
      .then((res) => {
        setActiveSessionDetail(res.data);
        setIsLoadingSessionDetail(false);
      })
      .catch((err) => {
        console.error("Error fetching session detail:", err);
        setIsLoadingSessionDetail(false);
      });
  };

  useEffect(() => {
    loadAllMemories();
    loadCaptureStatus();
    loadPendingMemories();

    // Poll capture status and pending memories every 10 seconds
    const interval = setInterval(() => {
      loadCaptureStatus();
      loadPendingMemories();
      loadAllMemories(); // Refresh main list for new background captures
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (currentView === "sessions") {
      loadSessions();
    }
  }, [currentView]);

  // Auto-scroll to bottom of QA chat messages
  useEffect(() => {
    if (isQaModalOpen) {
      chatMessagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages, isChatLoading, isQaModalOpen]);

  // Toggle Important Handler
  const handleToggleImportant = (e, id, currentStatus) => {
    e.stopPropagation();
    setAnimatingStarId(id);
    setTimeout(() => setAnimatingStarId(null), 300);

    const endpoint = currentStatus ? `${API}/memories/${id}/unimportant` : `${API}/memories/${id}/important`;
    axios
      .post(endpoint)
      .then(() => {
        setMemories((prev) =>
          prev.map((m) => (m.id === id ? { ...m, isImportant: !currentStatus } : m))
        );
        setActiveSessionDetail((prev) => {
          if (!prev) return null;
          return {
            ...prev,
            importantMemories: prev.importantMemories + (currentStatus ? -1 : 1),
            memories: prev.memories.map((m) => (m.id === id ? { ...m, isImportant: !currentStatus } : m))
          };
        });
      })
      .catch((err) => console.error("Error toggling important status:", err));
  };

  // Open Edit Dialog
  const handleOpenEdit = (memory) => {
    setEditingMemory(memory);
    setEditTitle(memory.title || "");
    setEditSummary(memory.summary || "");
    setEditError("");
    setEditSuccess("");
    setIsEditModalOpen(true);
  };

  // Save Edit Dialog
  const handleSaveEdit = () => {
    if (!editingMemory) return;
    setIsSavingEdit(true);
    setEditError("");
    setEditSuccess("");

    axios
      .put(`${API}/memories/${editingMemory.id}`, {
        title: editTitle,
        summary: editSummary,
      })
      .then((res) => {
        setEditSuccess("Memory updated successfully!");
        setMemories((prev) =>
          prev.map((m) => (m.id === editingMemory.id ? res.data : m))
        );
        setActiveSessionDetail((prev) => {
          if (!prev) return null;
          return {
            ...prev,
            memories: prev.memories.map((m) => (m.id === editingMemory.id ? res.data : m))
          };
        });
        setTimeout(() => {
          setIsEditModalOpen(false);
          setEditingMemory(null);
        }, 1000);
      })
      .catch((err) => {
        console.error(err);
        setEditError(err.response?.data?.message || "Failed to update memory.");
      })
      .finally(() => {
        setIsSavingEdit(false);
      });
  };

  // Search
  const handleSearch = () => {
    axios
      .get(`${API}/search?q=${search}`)
      .then((res) => setMemories(res.data))
      .catch((err) => console.log(err));
  };

  // Filter by type
  const handleFilter = () => {
    axios
      .get(`${API}/filter/${filterType}`)
      .then((res) => setMemories(res.data))
      .catch((err) => console.log(err));
  };

  // Get single memory
  const getMemory = (id) => {
    axios
      .get(`${API}/memory/${id}`)
      .then((res) => setSelectedMemory(res.data))
      .catch((err) => console.log(err));
  };

  // Delete memory
  const deleteMemory = (id) => {
    if (confirm("Are you sure you want to delete this memory?")) {
      axios
        .delete(`${API}/memory/${id}`)
        .then(() => {
          loadAllMemories();
          loadPendingMemories();
          setSelectedMemoryIds(prev => prev.filter(item => item !== id));
          if (selectedMemory && selectedMemory.id === id) {
            setSelectedMemory(null);
          }
        })
        .catch((err) => console.log(err));
    }
  };

  // Capture
  const captureMemory = () => {
    setIsCapturing(true);
    axios
      .post(`${API}/capture`)
      .then((res) => {
        setIsCapturing(false);
        if (res.data.status === "skipped") {
          alert(res.data.message);
          return;
        }
        
        if (res.data.pending_confirmation === 1) {
          // Sensitive data detected! Show confirmation popup
          setSensitiveReasonText(res.data.sensitivity_reason);
          setSensitiveMemoryId(res.data.id);
          setIsSensitiveModalOpen(true);
        } else {
          loadAllMemories();
          loadPendingMemories();
        }
      })
      .catch((err) => {
        console.log(err);
        setIsCapturing(false);
      });
  };

  // Pause / Resume background capture
  const handlePauseCapture = () => {
    axios
      .post(`${API}/capture/pause`)
      .then((res) => setCaptureStatus(res.data))
      .catch((err) => console.log(err));
  };

  const handleResumeCapture = () => {
    axios
      .post(`${API}/capture/resume`)
      .then((res) => setCaptureStatus(res.data))
      .catch((err) => console.log(err));
  };

  // Confirm pending memories
  const handleConfirmMemory = (id) => {
    axios
      .post(`${API}/memory/${id}/confirm`)
      .then(() => {
        loadPendingMemories();
        loadAllMemories();
      })
      .catch((err) => console.log("Error confirming memory:", err));
  };

  const handleDiscardPendingMemory = (id) => {
    axios
      .delete(`${API}/memory/${id}`)
      .then(() => {
        loadPendingMemories();
        loadAllMemories();
      })
      .catch((err) => console.log("Error discarding memory:", err));
  };

  // Confirm/Cancel from the Sensitive Confirmation Modal
  const handleConfirmSensitiveSave = () => {
    if (sensitiveMemoryId) {
      axios
        .post(`${API}/memory/${sensitiveMemoryId}/confirm`)
        .then(() => {
          setIsSensitiveModalOpen(false);
          setSensitiveMemoryId(null);
          setSensitiveReasonText("");
          loadPendingMemories();
          loadAllMemories();
        })
        .catch((err) => console.log("Error confirming sensitive memory:", err));
    }
  };

  const handleCancelSensitiveSave = () => {
    if (sensitiveMemoryId) {
      axios
        .delete(`${API}/memory/${sensitiveMemoryId}`)
        .then(() => {
          setIsSensitiveModalOpen(false);
          setSensitiveMemoryId(null);
          setSensitiveReasonText("");
          loadPendingMemories();
          loadAllMemories();
        })
        .catch((err) => console.log("Error discarding sensitive memory:", err));
    }
  };

  // Send QA message
  const handleSendChatMessage = (textToSubmit) => {
    const query = textToSubmit || chatInput;
    if (!query.trim()) return;

    setChatMessages((prev) => [...prev, { role: "user", content: query }]);
    setChatInput("");
    setIsChatLoading(true);

    axios
      .post(`${API}/ask`, { question: query })
      .then((res) => {
        setChatMessages((prev) => [...prev, { role: "ai", content: res.data.answer }]);
        setIsChatLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setChatMessages((prev) => [
          ...prev,
          { role: "ai", content: "Sorry, I ran into an error communicating with the QA backend: " + err.message }
        ]);
        setIsChatLoading(false);
      });
  };

  // Multi-select actions
  const handleToggleSelect = (id) => {
    setSelectedMemoryIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleSelectAll = () => {
    if (selectedMemoryIds.length === memories.length) {
      setSelectedMemoryIds([]);
    } else {
      setSelectedMemoryIds(memories.map((m) => m.id));
    }
  };

  // Context Pack Modal trigger
  const openContextPackModal = (ids) => {
    setIsModalOpen(true);
    setIsLoadingContextPack(true);
    setContextPackText("");
    setCopyFeedback(false);

    axios
      .post(`${API}/context-pack`, {
        memory_ids: ids,
      })
      .then((res) => {
        setContextPackText(res.data.contextPack || "No context was generated.");
        setIsLoadingContextPack(false);
      })
      .catch((err) => {
        console.error(err);
        setContextPackText("Error generating context pack: " + err.message);
        setIsLoadingContextPack(false);
      });
  };

  // Copy to clipboard
  const handleCopyContextPack = () => {
    navigator.clipboard
      .writeText(contextPackText)
      .then(() => {
        setCopyFeedback(true);
        setTimeout(() => setCopyFeedback(false), 2000);
      })
      .catch((err) => console.error("Clipboard copy failed: ", err));
  };

  // Type badge color mapping
  const getBadgeClass = (type) => {
    if (!type) return "badge badge-default";
    const t = type.toLowerCase().trim();
    if (t === "research") return "badge badge-research";
    if (t === "coding") return "badge badge-coding";
    if (t === "bug") return "badge badge-bug";
    if (t === "project") return "badge badge-project";
    if (t === "task") return "badge badge-task";
    if (t === "decision") return "badge badge-decision";
    if (t === "general note" || t === "generalnote") return "badge badge-general-note";
    return "badge badge-default";
  };

  const displayedMemories = memories.filter((memory) => {
    if (importanceFilter === "important") {
      return memory.isImportant === 1 || memory.isImportant === true;
    }
    return true;
  });

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">Totem</h1>
        <p className="app-subtitle">Active Desktop Context Memory & Classifier Dashboard</p>
      </header>

      {/* Navigation Tabs */}
      <div className="navigation-tabs">
        <button
          className={`nav-tab-btn ${currentView === "dashboard" ? "active" : ""}`}
          onClick={() => setCurrentView("dashboard")}
        >
          🎛 Dashboard
        </button>
        <button
          className={`nav-tab-btn ${currentView === "sessions" || currentView === "session-detail" ? "active" : ""}`}
          onClick={() => {
            loadSessions();
            setCurrentView("sessions");
          }}
        >
          🕒 Work Sessions
        </button>
      </div>

      {currentView === "dashboard" && (
        <>
          {/* Background Capture Status Widget */}
          <div className="capture-status-widget">
            <div className="status-info">
              <span className={`status-dot ${captureStatus.is_active ? "active" : "paused"}`} />
              <span className="status-text">
                Background Capture: <strong>{captureStatus.is_active ? "Active" : "Paused"}</strong>
              </span>
              {captureStatus.last_capture_time && (
                <span className="last-capture-text">
                  (Last captured: {new Date(captureStatus.last_capture_time).toLocaleTimeString()})
                </span>
              )}
            </div>
            <div className="capture-controls">
              {captureStatus.is_active ? (
                <button className="btn btn-warning" onClick={handlePauseCapture}>
                  Pause Background Capture
                </button>
              ) : (
                <button className="btn btn-primary" onClick={handleResumeCapture}>
                  Resume Background Capture
                </button>
              )}
            </div>
          </div>

          {/* Action Bar */}
          <div className="dashboard-actions">
            <div className="search-filter-group">
              <input
                className="input-styled"
                type="text"
                placeholder="Search summaries & titles..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <button className="btn btn-secondary" onClick={handleSearch}>
                Search
              </button>
              
              <input
                className="input-styled"
                type="text"
                placeholder="Filter by type..."
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
              />
              <button className="btn btn-secondary" onClick={handleFilter}>
                Filter
              </button>

              <select
                className="input-styled select-styled"
                value={importanceFilter}
                onChange={(e) => setImportanceFilter(e.target.value)}
                style={{ cursor: "pointer" }}
              >
                <option value="all">All</option>
                <option value="important">Important Only</option>
              </select>

              <button className="btn btn-secondary" onClick={loadAllMemories}>
                Show All
              </button>
            </div>

            <button 
              className="btn btn-primary" 
              onClick={captureMemory} 
              disabled={isCapturing}
            >
              {isCapturing ? (
                <>
                  <div className="spinner" style={{ width: "16px", height: "16px", borderWidth: "2px" }} />
                  Capturing (5s)...
                </>
              ) : (
                "Capture Memory"
              )}
            </button>
          </div>

          {/* Pending Sensitive Confirmations Queue */}
          {pendingMemories.length > 0 && (
            <div className="pending-confirmations-section">
              <h3 className="pending-section-title">
                ⚠️ Pending Confirmations ({pendingMemories.length})
              </h3>
              <p className="pending-section-desc">
                Sensitive content (API keys, tokens, passwords, or credit card details) was detected. Values were automatically masked for your privacy. Please approve (Confirm Save) or Discard these context memories.
              </p>
              <div className="pending-grid">
                {pendingMemories.map((memory) => (
                  <div key={memory.id} className="pending-card">
                    <div className="pending-card-header">
                      <span className="memory-id">Pending ID #{memory.id}</span>
                      <span className="badge pending-sensitive-badge">
                        High Sensitivity
                      </span>
                    </div>
                    <div className="memory-body" style={{ textAlign: "left" }}>
                      {memory.sensitivityReason && (
                        <p style={{ color: "#fbbf24", margin: "0 0 10px 0", fontSize: "0.95rem" }}>
                          <strong>Reason:</strong> {memory.sensitivityReason}
                        </p>
                      )}
                      <p className="memory-summary">
                        <strong>Summary:</strong> {memory.summary || "No summary generated"}
                      </p>
                      <div className="metadata-row">
                        <span className="metadata-item"><strong>App:</strong> {memory.sourceApp || "Unknown"}</span>
                        <span className="metadata-item"><strong>Window:</strong> {memory.windowTitle || "Unknown"}</span>
                        <span className="metadata-item">
                          <strong>Masked Content:</strong> <code style={{ fontSize: "12px" }}>{memory.rawContext || "None"}</code>
                        </span>
                      </div>
                    </div>
                    <div className="pending-card-actions">
                      <button className="btn btn-secondary" onClick={() => getMemory(memory.id)}>
                        View JSON
                      </button>
                      <button className="btn btn-danger" onClick={() => handleDiscardPendingMemory(memory.id)}>
                        Discard
                      </button>
                      <button className="btn btn-primary" onClick={() => handleConfirmMemory(memory.id)}>
                        Confirm Save (Keep Masked)
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Multi-select Header Control */}
          {memories.length > 0 && (
            <div className="selection-bar">
              <div className="selection-info">
                {selectedMemoryIds.length} of {memories.length} memories selected
              </div>
              <div style={{ display: "flex", gap: "12px" }}>
                <button className="btn btn-secondary" onClick={handleSelectAll}>
                  {selectedMemoryIds.length === memories.length ? "Deselect All" : "Select All"}
                </button>
                <button
                  className="btn btn-accent"
                  disabled={selectedMemoryIds.length === 0}
                  onClick={() => openContextPackModal(selectedMemoryIds)}
                >
                  Generate Selected Context Pack
                </button>
              </div>
            </div>
          )}

          {/* Memories Container */}
          <div className="memories-grid">
            {displayedMemories.length === 0 ? (
              <div style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}>
                <h3>
                  {memories.length === 0 
                    ? "No confirmed memories recorded yet. Capture Context or wait for Background Capture!" 
                    : "No important memories found with the current filter."}
                </h3>
              </div>
            ) : (
              displayedMemories.map((memory) => (
                <div
                  key={memory.id}
                  className={`memory-card ${selectedMemoryIds.includes(memory.id) ? "selected" : ""} ${memory.isImportant ? "important" : ""}`}
                >
                  <div className="card-header">
                    <div className="card-header-left">
                      <input
                        type="checkbox"
                        className="memory-checkbox"
                        checked={selectedMemoryIds.includes(memory.id)}
                        onChange={() => handleToggleSelect(memory.id)}
                      />
                      <button
                        className={`star-btn ${memory.isImportant ? "important" : ""} ${animatingStarId === memory.id ? "animating" : ""}`}
                        onClick={(e) => handleToggleImportant(e, memory.id, memory.isImportant)}
                        title={memory.isImportant ? "Mark Unimportant" : "Mark Important"}
                      >
                        {memory.isImportant ? "★" : "☆"}
                      </button>
                      <span className="memory-id">#{memory.id}</span>
                      <h3 className="memory-title">
                        {memory.title || `Memory Chunk`}
                      </h3>
                    </div>
                    <span className={getBadgeClass(memory.type)}>
                      {memory.type}
                    </span>
                  </div>

                  <div className="memory-body">
                    <p className="memory-summary">{memory.summary}</p>
                    <div className="metadata-row">
                      <span className="metadata-item">
                        <strong>App:</strong> {memory.sourceApp || "Unknown"}
                      </span>
                      <span className="metadata-item">
                        <strong>Title:</strong> {memory.windowTitle || "Unknown"}
                      </span>
                      {memory.suggestedNextAction && (
                        <span className="metadata-item">
                          <strong>Next Action:</strong> {memory.suggestedNextAction}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="card-actions">
                    <button className="btn btn-secondary" onClick={() => getMemory(memory.id)}>
                      View JSON
                    </button>
                    <button className="btn btn-secondary" onClick={() => handleOpenEdit(memory)}>
                      Edit
                    </button>
                    <button
                      className="btn btn-accent"
                      onClick={() => openContextPackModal([memory.id])}
                    >
                      Context Pack
                    </button>
                    <button
                      className="btn btn-danger"
                      onClick={() => deleteMemory(memory.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </>
      )}

      {currentView === "sessions" && (
        <div className="sessions-view-container">
          <div className="section-header">
            <h2 className="section-title">Work Sessions</h2>
            <p className="section-subtitle">Continuous periods of workspace activity grouped automatically</p>
          </div>
          {sessions.length === 0 ? (
            <div className="no-sessions-fallback">
              <h3>No work sessions detected yet.</h3>
              <p>Capture some context memories to automatically group them into sessions.</p>
            </div>
          ) : (
            <div className="sessions-grid">
              {sessions.map((sess) => (
                <div
                  key={sess.sessionId}
                  className="session-card"
                  onClick={() => viewSessionDetail(sess.sessionId)}
                >
                  <div className="session-card-header">
                    <span className="session-card-id">Session #{sess.sessionId}</span>
                    <span className={getBadgeClass(sess.topCategory)}>
                      {sess.topCategory}
                    </span>
                  </div>
                  <div className="session-card-body">
                    <div className="session-metric-row">
                      <span className="session-metric-label">Duration:</span>
                      <span className="session-metric-value">{sess.duration}</span>
                    </div>
                    <div className="session-metric-row">
                      <span className="session-metric-label">Memories:</span>
                      <span className="session-metric-value">{sess.totalMemories}</span>
                    </div>
                    <div className="session-metric-row">
                      <span className="session-metric-label">Most Used App:</span>
                      <span className="session-metric-value">{sess.mostUsedApp}</span>
                    </div>
                    <div className="session-metric-row">
                      <span className="session-metric-label">Important Items:</span>
                      <span className="session-metric-value text-warning">★ {sess.importantMemories}</span>
                    </div>
                  </div>
                  <div className="session-card-footer">
                    <span className="session-time-range">
                      {new Date(sess.sessionStart).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - {new Date(sess.sessionEnd).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    <span className="session-card-action-text">View Timeline →</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {currentView === "session-detail" && (
        <div className="session-detail-container">
          <div className="session-detail-header-row">
            <button className="btn btn-secondary" onClick={() => setCurrentView("sessions")}>
              ← Back to Sessions
            </button>
            <h2 className="session-detail-title">Session #{activeSessionId} Details</h2>
          </div>

          {isLoadingSessionDetail || !activeSessionDetail ? (
            <div className="loading-container">
              <div className="spinner" />
              <p style={{ color: "var(--text-muted)", fontSize: "1.1rem" }}>
                Analyzing session details & generating AI summary...
              </p>
            </div>
          ) : (
            <>
              {/* Session Meta Stats Cards */}
              <div className="session-stats-bar">
                <div className="stat-box">
                  <span className="stat-label">Duration</span>
                  <span className="stat-val">{activeSessionDetail.duration}</span>
                </div>
                <div className="stat-box">
                  <span className="stat-label">Total Memories</span>
                  <span className="stat-val">{activeSessionDetail.totalMemories}</span>
                </div>
                <div className="stat-box">
                  <span className="stat-label">Top Category</span>
                  <span className={`stat-val ${getBadgeClass(activeSessionDetail.topCategory)}`} style={{ textTransform: "uppercase", fontSize: "0.95rem" }}>
                    {activeSessionDetail.topCategory}
                  </span>
                </div>
                <div className="stat-box">
                  <span className="stat-label">Most Used App</span>
                  <span className="stat-val">{activeSessionDetail.mostUsedApp}</span>
                </div>
                <div className="stat-box">
                  <span className="stat-label">Important Items</span>
                  <span className="stat-val text-warning">★ {activeSessionDetail.importantMemories}</span>
                </div>
              </div>

              {/* AI Summary Section */}
              <div className="session-summary-card">
                <h3 className="summary-section-title">
                  <span>🧠</span> AI Session Summary
                </h3>
                <div className="summary-grid">
                  <div className="summary-item objective">
                    <strong>Main Objective</strong>
                    <p>{activeSessionDetail.summary?.mainObjective || "N/A"}</p>
                  </div>
                  <div className="summary-item next-step">
                    <strong>Suggested Next Step</strong>
                    <p>{activeSessionDetail.summary?.suggestedNextStep || "N/A"}</p>
                  </div>
                  <div className="summary-item completed">
                    <strong>Work Completed</strong>
                    <div>
                      {typeof activeSessionDetail.summary?.workCompleted === 'string' ? (
                        <p>{activeSessionDetail.summary.workCompleted}</p>
                      ) : Array.isArray(activeSessionDetail.summary?.workCompleted) ? (
                        <ul>
                          {activeSessionDetail.summary.workCompleted.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      ) : (
                        <p>N/A</p>
                      )}
                    </div>
                  </div>
                  <div className="summary-item decisions">
                    <strong>Decisions Made</strong>
                    <p>{activeSessionDetail.summary?.decisionsMade || "N/A"}</p>
                  </div>
                  <div className="summary-item issues">
                    <strong>Outstanding Issues</strong>
                    <p>{activeSessionDetail.summary?.outstandingIssues || "N/A"}</p>
                  </div>
                </div>
              </div>

              {/* Session Context Pack Trigger */}
              <div className="session-context-pack-action">
                <button
                  className="btn btn-accent"
                  onClick={() => openContextPackModal(activeSessionDetail.memories.map(m => m.id))}
                >
                  ✨ Generate Session Context Pack
                </button>
              </div>

              {/* Search Within Session & Timeline Filters */}
              <div className="timeline-section-header">
                <h3 className="timeline-title">Session Timeline</h3>
                <div className="timeline-search-box">
                  <input
                    type="text"
                    className="input-styled"
                    placeholder="Search within session..."
                    value={sessionSearch}
                    onChange={(e) => setSessionSearch(e.target.value)}
                  />
                </div>
              </div>

              {/* Chronological Timeline */}
              <div className="timeline-container">
                <div className="timeline-line" />
                {activeSessionDetail.memories
                  .filter((m) => {
                    if (!sessionSearch.trim()) return true;
                    const query = sessionSearch.toLowerCase();
                    return (
                      (m.title && m.title.toLowerCase().includes(query)) ||
                      (m.summary && m.summary.toLowerCase().includes(query)) ||
                      (m.sourceApp && m.sourceApp.toLowerCase().includes(query)) ||
                      (m.windowTitle && m.windowTitle.toLowerCase().includes(query))
                    );
                  })
                  .map((memory) => {
                    const isImp = memory.isImportant === 1 || memory.isImportant === true;
                    return (
                      <div key={memory.id} className={`timeline-item ${isImp ? "important" : ""}`}>
                        <div className="timeline-badge">
                          <div className="timeline-dot" />
                        </div>
                        <div className={`memory-card ${isImp ? "important" : ""}`}>
                          <div className="card-header">
                            <div className="card-header-left">
                              <button
                                className={`star-btn ${isImp ? "important" : ""} ${animatingStarId === memory.id ? "animating" : ""}`}
                                onClick={(e) => handleToggleImportant(e, memory.id, memory.isImportant)}
                                title={isImp ? "Mark Unimportant" : "Mark Important"}
                              >
                                {isImp ? "★" : "☆"}
                              </button>
                              <span className="memory-id">#{memory.id}</span>
                              <h3 className="memory-title">
                                {memory.title || `Memory Chunk`}
                              </h3>
                            </div>
                            <span className={getBadgeClass(memory.type)}>
                              {memory.type}
                            </span>
                          </div>

                          <div className="memory-body">
                            <p className="memory-summary">{memory.summary}</p>
                            <div className="metadata-row">
                              <span className="metadata-item">
                                <strong>App:</strong> {memory.sourceApp || "Unknown"}
                              </span>
                              <span className="metadata-item">
                                <strong>Title:</strong> {memory.windowTitle || "Unknown"}
                              </span>
                              <span className="metadata-item">
                                <strong>Time:</strong> {new Date(memory.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                              </span>
                            </div>
                          </div>

                          <div className="card-actions">
                            <button className="btn btn-secondary" onClick={() => getMemory(memory.id)}>
                              View JSON
                            </button>
                            <button className="btn btn-secondary" onClick={() => handleOpenEdit(memory)}>
                              Edit
                            </button>
                            <button
                              className="btn btn-danger"
                              onClick={() => {
                                deleteMemory(memory.id);
                                // Refresh session detail if a memory was deleted
                                setTimeout(() => viewSessionDetail(activeSessionId), 500);
                              }}
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </>
          )}
        </div>
      )}

      {/* Detailed memory preview */}
      {selectedMemory && (
        <div className="details-pane">
          <div className="details-header">
            <h2 className="details-title">Memory Detail Schema (ID #{selectedMemory.id})</h2>
            <button className="btn btn-secondary" onClick={() => setSelectedMemory(null)}>
              Hide
            </button>
          </div>
          <pre className="json-view">
            {JSON.stringify(selectedMemory, null, 2)}
          </pre>
        </div>
      )}

      {/* Context Pack Overlay Modal */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">
                Context Pack
              </h2>
              <button className="modal-close-btn" onClick={() => setIsModalOpen(false)}>
                &times;
              </button>
            </div>
            
            <div className="modal-body">
              {isLoadingContextPack ? (
                <div className="loading-container">
                  <div className="spinner" />
                  <p style={{ color: "var(--text-muted)", fontSize: "1.1rem" }}>
                    Weaving context pack from selected memories...
                  </p>
                </div>
              ) : (
                <pre className="context-pack-text">
                  {contextPackText}
                </pre>
              )}
            </div>

            <div className="modal-footer">
              <button 
                className="btn btn-secondary" 
                onClick={() => setIsModalOpen(false)}
              >
                Close
              </button>
              <button 
                className="btn btn-primary" 
                onClick={handleCopyContextPack}
                disabled={isLoadingContextPack}
              >
                {copyFeedback ? "✓ Copied!" : "Copy Context Pack"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Question Answering Centered Modal       {/* Floating AI Assistant Widget */}
      <div className="floating-assistant-container">
        {isQaModalOpen && (
          <div className="assistant-chat-panel">
            <div className="assistant-header">
              <div className="assistant-header-title">
                <span className="assistant-bot-icon">🤖</span>
                <span className="assistant-title-text">Totem Assistant</span>
              </div>
              <button className="assistant-close-btn" onClick={() => setIsQaModalOpen(false)}>
                ✕
              </button>
            </div>
            
            <div className="assistant-body">
              <div className="chat-messages-container">
                {chatMessages.map((msg, index) => (
                  <div key={index} className={`chat-bubble ${msg.role}`}>
                    {msg.content}
                  </div>
                ))}
                {isChatLoading && (
                  <div className="typing-indicator" style={{ padding: "0 0 10px 0" }}>
                    <div className="typing-dot" />
                    <div className="typing-dot" />
                    <div className="typing-dot" />
                  </div>
                )}
                
                {chatMessages.length === 1 && (
                  <div className="chat-suggestions">
                    <button className="chat-suggestion-btn" onClick={() => handleSendChatMessage("What was I working on recently?")}>
                      🔍 What was I working on recently?
                    </button>
                    <button className="chat-suggestion-btn" onClick={() => handleSendChatMessage("Which bugs did I solve?")}>
                      🐛 Which bugs did I solve?
                    </button>
                    <button className="chat-suggestion-btn" onClick={() => handleSendChatMessage("What important decisions did I make?")}>
                      💡 What important decisions did I make?
                    </button>
                  </div>
                )}
                <div ref={chatMessagesEndRef} />
              </div>
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendChatMessage();
              }}
              className="chat-input-row"
              style={{ padding: "12px 16px", background: "rgba(15, 23, 42, 0.4)", borderTop: "1px solid var(--border-color)" }}
            >
              <input
                type="text"
                className="chat-modal-input"
                placeholder="Ask Totem..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                disabled={isChatLoading}
                autoFocus
              />
              <button type="submit" className="btn btn-primary" disabled={isChatLoading}>
                Send
              </button>
            </form>
          </div>
        )}

        <button 
          className={`floating-assistant-btn ${isQaModalOpen ? "active" : ""}`}
          onClick={() => setIsQaModalOpen(!isQaModalOpen)}
          title="Totem Assistant"
        >
          <span className="bot-icon">🤖</span>
          <span className="btn-label">Totem Assistant</span>
        </button>
      </div>

      {/* Sensitive Content Confirmation Modal */}
      {isSensitiveModalOpen && (
        <div className="modal-overlay" onClick={() => handleCancelSensitiveSave()}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header" style={{ borderBottomColor: "rgba(245, 158, 11, 0.3)" }}>
              <h2 className="modal-title" style={{ color: "#fbbf24" }}>
                ⚠ Sensitive Content Detected
              </h2>
              <button className="modal-close-btn" onClick={() => handleCancelSensitiveSave()}>
                &times;
              </button>
            </div>
            
            <div className="modal-body" style={{ textAlign: "center", padding: "30px 24px" }}>
              <p style={{ fontSize: "1.1rem", marginBottom: "20px", color: "var(--text-main)" }}>
                Possible login credentials or authentication information detected.
              </p>
              
              <div style={{
                background: "rgba(245, 158, 11, 0.1)",
                border: "1px solid rgba(245, 158, 11, 0.3)",
                borderRadius: "12px",
                padding: "16px",
                textAlign: "left",
                marginBottom: "24px"
              }}>
                <strong style={{ color: "#fbbf24", display: "block", marginBottom: "6px" }}>Reason:</strong>
                <span style={{ fontSize: "1rem", fontFamily: "var(--font-mono)", color: "#f3f4f6" }}>
                  {sensitiveReasonText || "Possible credentials or keys detected"}
                </span>
              </div>
            </div>

            <div className="modal-footer" style={{ background: "rgba(15, 23, 42, 0.6)" }}>
              <button 
                className="btn btn-secondary" 
                onClick={() => handleCancelSensitiveSave()}
              >
                Cancel
              </button>
              <button 
                className="btn btn-warning" 
                onClick={() => handleConfirmSensitiveSave()}
              >
                Save Anyway
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Edit Memory Modal */}
      {isEditModalOpen && editingMemory && (
        <div className="modal-overlay" onClick={() => setIsEditModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Edit Memory</h2>
              <button className="modal-close-btn" onClick={() => setIsEditModalOpen(false)}>
                &times;
              </button>
            </div>
            
            <div className="modal-body" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {editError && <div className="error-message" style={{ color: "var(--danger)", fontWeight: "500" }}>{editError}</div>}
              {editSuccess && <div className="success-message" style={{ color: "var(--success)", fontWeight: "500" }}>{editSuccess}</div>}
              
              <div className="form-group" style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                <label style={{ fontWeight: "600", fontSize: "0.95rem", color: "var(--text-muted)" }}>Title</label>
                <input
                  type="text"
                  className="input-styled"
                  style={{ width: "100%", boxSizing: "border-box" }}
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  placeholder="Enter memory title..."
                  disabled={isSavingEdit}
                />
              </div>

              <div className="form-group" style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                <label style={{ fontWeight: "600", fontSize: "0.95rem", color: "var(--text-muted)" }}>Summary</label>
                <textarea
                  className="input-styled"
                  style={{ width: "100%", height: "140px", resize: "vertical", boxSizing: "border-box", fontFamily: "inherit" }}
                  value={editSummary}
                  onChange={(e) => setEditSummary(e.target.value)}
                  placeholder="Enter memory summary..."
                  disabled={isSavingEdit}
                />
              </div>
            </div>

            <div className="modal-footer">
              <button 
                className="btn btn-secondary" 
                onClick={() => setIsEditModalOpen(false)}
                disabled={isSavingEdit}
              >
                Cancel
              </button>
              <button 
                className="btn btn-accent" 
                onClick={handleSaveEdit}
                disabled={isSavingEdit}
              >
                {isSavingEdit ? "Saving..." : "Save"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;