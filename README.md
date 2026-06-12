# Totem: Active Desktop Context Memory, Classifier & Sessions Dashboard

Totem is a premium desktop productivity companion that captures your active workspace context (active application, window title, clipboard content, and system screenshots) and uses an advanced AI classifier (via Groq and Llama-3.3-70b-versatile) to group, summarize, and categorize your activities. 

It organizes your work history into continuous "Work Sessions", priorities, and interactive timelines, and compiles memories into a unified "Context Pack"—an optimized system prompt designed to help you quickly resume tasks or bootstrap LLM chat sessions.

---

## 🚀 Key Features

### 🕒 Automatic Session Detection (New)
*   **Temporal Grouping**: Automatically groups interaction memories captured within **30 minutes** of each other into a single, continuous work session. Gaps greater than 30 minutes start a new session.
*   **Sequential Session IDs**: Generates sequential IDs automatically.
*   **Active Session Propagations**: Automatically updates `sessionEnd` for all memories in an active session upon new captures.
*   **Session Metrics**: Calculates Total Memories, Session Duration, Top Category, Most Used App, and count of Important Memories for each session.
*   **AI-Generated Session Summaries**: Leverages Groq Llama 3.3 to analyze session timelines and generate JSON summaries describing the **Main Objective**, **Work Completed**, **Decisions Made**, **Outstanding Issues**, and **Suggested Next Step**.
*   **Performance Caching**: Caches session summaries in a dedicated SQLite `work_sessions` table, automatically invalidating/clearing the cache when new captures are added to an active session.

### 🎛️ Interactive Glassmorphic UI
*   **Multi-View Navigation**: A top navigation tab bar to seamlessly switch between the **Dashboard** and **Work Sessions** pages.
*   **Sessions List Page**: Displays a clean grid of session summary cards sorted in reverse chronological order.
*   **Session Detail Page**:
    *   **AI Summary Card**: Displays the structured AI session analysis.
    *   **Stats Summary Bar**: Renders session duration, app usage, and priority counts.
    *   **Chronological Timeline**: A vertical timeline layout connecting memories with glowing nodes.
    *   **Timeline Search**: Instant keyword filtering within the session timeline.
    *   **Session Context Pack**: Generates a consolidated context pack for the entire session in one click.

### 🤖 Floating AI Assistant Widget
*   **ChatGPT-Style Assistant**: A fixed circular widget in the bottom-right corner with a bot icon and label `Totem Assistant`.
*   **Interactive Chat Panel**: Slides up into a glassmorphic sidebar drawer. Users can ask context-aware questions (e.g. *"What was I working on recently?"* or *"Which bugs did I solve?"*), retrieving relevant data dynamically from SQL.

### 🌟 Important & Editable Memories
*   **Star Priority Toggles**: Star icons next to memories trigger smooth pop/bounce animations and highlight card borders in amber/gold.
*   **Priority Filters**: Filter dashboard memory cards by **All** or **Important Only**.
*   **Inline Editing**: Edit memory titles and summaries in-place via a pre-filled popup modal, writing updates back to the SQLite DB.
*   **Context Pack Prioritization**: Places important memories first inside context packs, adding a `(Priority: Important)` suffix.

### 🔒 Sensitive-Content Protection & Masking
*   **Multichannel Credentials Check**: Automatically scans window titles, clipboard text, and screenshot OCR (using Groq Vision `llama-3.2-11b-vision-preview`) for passwords, access tokens, bank details, credentials, and API keys.
*   **Automatic Masking**: Replaces sensitive data with masked markers before database storage or AI requests.
*   **Pending Confirmation Queue**: Isolates high-sensitivity captures into a "Pending Confirmations" dashboard section. Users can review, **Confirm Save** (to keep masked), or **Discard** them.

### 🐍 Continuous System Capture
*   **Auto-Capture Daemon**: A background thread executing delay-free context captures every 20 seconds.
*   **Dashboard Controls**: Quickly pause or resume the background capture thread with pulsating active indicators and last capture timestamps.
*   **Manual Trigger**: Capture active system context instantly on demand.
*   **AI Classification**: Automatically extracts summaries, user intent, topics, usefulness scores, and activity tags (Research, Coding, Bug, Project, Task, Decision, General Note).

---

## 📂 Project Structure & File Index

### 🐍 Backend (`/backend`)
*   **[main.py](file:///c:/Users/admin/Desktop/Totem%20-%20Copy/backend/main.py)**: Entry point. Handles CORS, startup SQLite migrations, and background capture daemons.
*   **[database/models.py](file:///c:/Users/admin/Desktop/Totem%20-%20Copy/backend/database/models.py)**: Declares SQLAlchemy models for the `memories` and `work_sessions` tables.
*   **[database/db.py](file:///c:/Users/admin/Desktop/Totem%20-%20Copy/backend/database/db.py)**: Coordinates SQLite connections and handles self-applying schema migrations.
*   **[routes/capture_route.py](file:///c:/Users/admin/Desktop/Totem%20-%20Copy/backend/routes/capture_route.py)**: Exposes endpoints for capture operations, QA ask requests, database filters, session list queries, and AI summary generators.
*   **[services/save_memory.py](file:///c:/Users/admin/Desktop/Totem%20-%20Copy/backend/services/save_memory.py)**: Computes 30-minute session boundaries, updates end times, invalidates session caches, and writes memory records to SQL.
*   **[services/sensitive_detector.py](file:///c:/Users/admin/Desktop/Totem%20-%20Copy/backend/services/sensitive_detector.py)**: Regex credential detectors and vision OCR utilities.

### ⚛️ Frontend (`/frontend`)
*   **[src/App.jsx](file:///c:/Users/admin/Desktop/Totem%20-%20Copy/frontend/src/App.jsx)**: Main dashboard page routing. Orchestrates status panels, search bars, QA chat drawer overlay, session card lists, and chronological detail timelines.
*   **[src/App.css](file:///c:/Users/admin/Desktop/Totem%20-%20Copy/frontend/src/App.css)**: Glassmorphic theme styling rules, navigation tabs, vertical timeline nodes, grid cards, and layout animations.

---

## 🛠️ Local Setup & Deployment

### 1. Set Up Environment Variables
Create or verify that `/backend/.env` contains your Groq API Key:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Launch the Backend API Server
Navigate to the `/backend` directory, activate the python virtual environment, and run uvicorn:
```powershell
# Windows (from backend directory)
.\venv\Scripts\uvicorn.exe main:app --reload
```
The FastAPI backend server runs at `http://127.0.0.1:8000`.

### 3. Launch the Frontend Development Server
Navigate to the `/frontend` directory and start the Vite server:
```bash
# From frontend directory
npm install
npm run dev
```
Open `http://localhost:5173` in your browser to interact with Totem!
