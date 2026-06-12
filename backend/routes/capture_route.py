from fastapi import APIRouter
from pydantic import BaseModel

from capture.context_capture import capture_context
from ai.groq_service import classify_context
from services.save_memory import save_memory
from services.get_memories import get_all_memories
from services.get_memory import get_memory_by_id
from services.search_memory import search_memory
from services.filter_memory import filter_memory
from services.delete_memory import delete_memory
from services.background_capture import background_capture_manager


router = APIRouter()


class AskRequest(BaseModel):
    question: str


class UpdateMemoryRequest(BaseModel):
    title: str = None
    summary: str = None


@router.get("/capture/status")
def get_capture_status():
    return background_capture_manager.get_status()


@router.post("/capture/pause")
def pause_capture():
    background_capture_manager.pause()
    return background_capture_manager.get_status()


@router.post("/capture/resume")
def resume_capture():
    background_capture_manager.resume()
    return background_capture_manager.get_status()


@router.get("/memories/pending")
def get_pending_memories():
    from database.db import SessionLocal
    from database.models import Memory
    db = SessionLocal()
    pending = db.query(Memory).filter(Memory.pending_confirmation == 1).all()
    db.close()
    return pending


@router.post("/memory/{memory_id}/confirm")
def confirm_memory(memory_id: int):
    from database.db import SessionLocal
    from database.models import Memory
    db = SessionLocal()
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if memory:
        memory.pending_confirmation = 0
        db.commit()
        db.close()
        return {"status": "success", "message": f"Memory {memory_id} confirmed."}
    db.close()
    return {"status": "error", "message": "Memory not found."}


@router.post("/ask")
def ask_memories(payload: AskRequest):
    from database.db import SessionLocal
    from database.models import Memory
    from ai.groq_service import client

    db = SessionLocal()
    memories = db.query(Memory).filter(Memory.pending_confirmation != 1).all()
    db.close()

    # Format memories for the context window
    memories_text = ""
    for m in memories:
        memories_text += (
            f"- Memory #{m.id} ({m.createdAt}):\n"
            f"  App: {m.sourceApp} | Window: {m.windowTitle}\n"
            f"  Summary: {m.summary}\n"
            f"  Type: {m.type} | Topic: {m.topic}\n"
            f"  Next Action: {m.suggestedNextAction or 'None'}\n\n"
        )

    system_prompt = (
        "You are Totem QA, a helpful AI coding and work assistant.\n"
        "You are given a list of captured user memories (desktop interactions) and a user question.\n"
        "Answer the user's question accurately and concisely, drawing information strictly from the provided memories.\n"
        "Identify details by memory IDs and timestamps where appropriate.\n"
        "If the memories do not contain enough information to answer the question, state that clearly.\n"
        "Do not make up facts. Use a polite, professional tone."
    )

    user_prompt = (
        f"Here are my captured memories:\n\n{memories_text}\n"
        f"User Question: {payload.question}\n\n"
        "Answer:"
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Error querying Groq model for QA: {str(e)}"

    return {"answer": answer}


@router.post("/capture")
def capture():

    context = capture_context()

    title = context.get("windowTitle", "")
    if any(keyword in title for keyword in ["Totem", "Question Answering", "localhost:5173", "127.0.0.1:5173"]):
        import os
        screenshot_path = context.get("screenshot")
        if screenshot_path and os.path.exists(screenshot_path):
            try:
                os.remove(screenshot_path)
            except Exception as e:
                print("Error removing self-capture screenshot:", e)
        return {
            "status": "skipped",
            "message": f"Capture skipped: active window is Totem dashboard/QA ({title})"
        }

    # Perform OCR and sensitive check
    from services.sensitive_detector import detect_and_mask_sensitive_data, extract_ocr_text_from_screenshot, check_sensitivity_rules
    ocr_text = extract_ocr_text_from_screenshot(context.get("screenshot"))

    has_sens_win, masked_win = detect_and_mask_sensitive_data(context.get("windowTitle", ""))
    has_sens_clip, masked_clip = detect_and_mask_sensitive_data(context.get("rawContext", ""))
    has_sens_ocr, masked_ocr = detect_and_mask_sensitive_data(ocr_text)

    # Pre-mask context inputs
    context["windowTitle"] = masked_win
    context["rawContext"] = masked_clip

    # Classify context using Groq
    memory = classify_context(context)

    # Mask sensitive data in summary if generated
    has_sens_sum, masked_sum = detect_and_mask_sensitive_data(memory.get("summary", ""))
    memory["summary"] = masked_sum

    # Run custom sensitivity rules
    is_sensitive, sensitivity_reason = check_sensitivity_rules(masked_win, masked_clip, masked_ocr, masked_sum)

    # Combine with regex match indicators
    regex_sensitive = has_sens_win or has_sens_clip or has_sens_ocr or has_sens_sum
    if regex_sensitive and not is_sensitive:
        is_sensitive = True
        sensitivity_reason = "Possible credentials or keys detected"
        print(f"[Sensitive] {sensitivity_reason}")
        print("[Sensitive] Save blocked until user confirmation")

    pending_confirmation = 0
    if is_sensitive:
        memory["sensitivity"] = "High"
        pending_confirmation = 1

    memory_id = save_memory(
        context,
        memory,
        pending_confirmation=pending_confirmation,
        sensitivity_reason=sensitivity_reason if is_sensitive else None
    )

    return {

        "id": memory_id,

        "metadata": context,

        "memory": memory,

        "pending_confirmation": pending_confirmation,

        "sensitivity_reason": sensitivity_reason if is_sensitive else None

    }


@router.get("/memories")
def get_memories():

    memories = get_all_memories()

    return memories

@router.get("/memory/{memory_id}")
def get_memory(memory_id: int):

    return get_memory_by_id(memory_id)

@router.get("/search")
def search(q: str):

    return search_memory(q)



@router.get("/filter/{memory_type}")
def filter_by_type(memory_type: str):

    return filter_memory(memory_type)


@router.delete("/memory/{memory_id}")
def delete(memory_id: int):

    delete_memory(memory_id)

    return {
        "message": "Memory deleted"
    }


@router.post("/memories/{memory_id}/important")
def make_important(memory_id: int):
    from database.db import SessionLocal
    from database.models import Memory
    db = SessionLocal()
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if memory:
        memory.isImportant = True
        db.commit()
        db.refresh(memory)
        db.close()
        return {"status": "success", "message": f"Memory {memory_id} marked as important."}
    db.close()
    return {"status": "error", "message": "Memory not found."}


@router.post("/memories/{memory_id}/unimportant")
def make_unimportant(memory_id: int):
    from database.db import SessionLocal
    from database.models import Memory
    db = SessionLocal()
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if memory:
        memory.isImportant = False
        db.commit()
        db.refresh(memory)
        db.close()
        return {"status": "success", "message": f"Memory {memory_id} marked as unimportant."}
    db.close()
    return {"status": "error", "message": "Memory not found."}


@router.put("/memories/{memory_id}")
def update_memory(memory_id: int, payload: UpdateMemoryRequest):
    from database.db import SessionLocal
    from database.models import Memory
    db = SessionLocal()
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory:
        db.close()
        return {"status": "error", "message": "Memory not found."}
    
    if payload.title is not None:
        memory.title = payload.title
    if payload.summary is not None:
        memory.summary = payload.summary
        
    db.commit()
    db.refresh(memory)
    db.close()
    return memory


def parse_timestamp(ts_str):
    if not ts_str:
        return None
    from datetime import datetime
    try:
        return datetime.fromisoformat(ts_str)
    except Exception:
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(ts_str, fmt)
            except Exception:
                continue
    return None


def format_duration(seconds):
    seconds = max(0, int(seconds))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return f"{seconds}s"


def generate_session_summary_ai(memories):
    from ai.groq_service import client
    import json

    memories_text = ""
    for idx, m in enumerate(memories):
        is_imp = " (Important)" if getattr(m, 'isImportant', False) else ""
        memories_text += (
            f"[{idx+1}] Time: {m.createdAt} | App: {m.sourceApp} | Window: {m.windowTitle}{is_imp}\n"
            f"    Type: {m.type} | Topic: {m.topic} | Intent: {m.intent}\n"
            f"    Summary: {m.summary}\n\n"
        )

    system_prompt = (
        "You are Totem Session Analyzer, an AI assistant that analyzes a user's work session and generates a summary.\n"
        "You are given a list of desktop interaction memories from a single session, sorted chronologically.\n"
        "Generate a JSON object describing the work session. The JSON object must contain exactly these five keys:\n"
        "  - \"mainObjective\": A concise description of the main objective of this session (e.g. \"Fix frontend API\").\n"
        "  - \"workCompleted\": A bulleted list or paragraph describing the work completed.\n"
        "  - \"decisionsMade\": A list of decisions made during the session (N/A if none).\n"
        "  - \"outstandingIssues\": Any outstanding issues, bugs, or things left incomplete.\n"
        "  - \"suggestedNextStep\": The logical next step for the user.\n\n"
        "Respond ONLY with a valid raw JSON block. Do not wrap it in ```json codeblocks or add any extra text or conversational filler."
    )

    user_prompt = f"Here are the memories from this session:\n\n{memories_text}\n\nJSON Summary:"

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
        result = response.choices[0].message.content.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        result = result.strip()
        return json.loads(result)
    except Exception as e:
        print("Error generating session summary:", e)
        return {
            "mainObjective": "Error generating summary",
            "workCompleted": f"Could not generate summary due to error: {str(e)}",
            "decisionsMade": "N/A",
            "outstandingIssues": "N/A",
            "suggestedNextStep": "Please check backend logs or Groq configuration"
        }


@router.get("/sessions")
def get_sessions():
    from database.db import SessionLocal
    from database.models import Memory
    from collections import defaultdict

    db = SessionLocal()
    memories = db.query(Memory).filter(Memory.sessionId.isnot(None)).all()
    db.close()

    sessions_map = defaultdict(list)
    for m in memories:
        sessions_map[m.sessionId].append(m)

    sessions_list = []
    for s_id, s_memories in sessions_map.items():
        s_memories.sort(key=lambda x: x.createdAt or "")

        start_str = s_memories[0].sessionStart or s_memories[0].createdAt
        end_str = s_memories[-1].sessionEnd or s_memories[-1].createdAt

        t_start = parse_timestamp(start_str)
        t_end = parse_timestamp(end_str)
        duration_sec = 0
        if t_start and t_end:
            duration_sec = (t_end - t_start).total_seconds()
        duration_formatted = format_duration(duration_sec)

        types = [m.type for m in s_memories if m.type]
        top_category = max(set(types), key=types.count) if types else "N/A"

        apps = [m.sourceApp for m in s_memories if m.sourceApp]
        most_used_app = max(set(apps), key=apps.count) if apps else "N/A"

        important_count = sum(1 for m in s_memories if getattr(m, 'isImportant', False))

        sessions_list.append({
            "sessionId": s_id,
            "sessionStart": start_str,
            "sessionEnd": end_str,
            "duration": duration_formatted,
            "durationSeconds": duration_sec,
            "totalMemories": len(s_memories),
            "topCategory": top_category,
            "mostUsedApp": most_used_app,
            "importantMemories": important_count
        })

    def get_sort_key(s):
        try:
            return (int(s["sessionId"]), s["sessionStart"])
        except ValueError:
            return (0, s["sessionStart"])

    sessions_list.sort(key=get_sort_key, reverse=True)
    return sessions_list


@router.get("/sessions/{session_id}")
def get_session_detail(session_id: str):
    from database.db import SessionLocal
    from database.models import Memory, WorkSession
    import json
    
    db = SessionLocal()
    memories = db.query(Memory).filter(Memory.sessionId == session_id).all()
    
    if not memories:
        db.close()
        return {"status": "error", "message": f"Session {session_id} not found."}
        
    memories.sort(key=lambda x: x.createdAt or "")
    
    start_str = memories[0].sessionStart or memories[0].createdAt
    end_str = memories[-1].sessionEnd or memories[-1].createdAt
    
    t_start = parse_timestamp(start_str)
    t_end = parse_timestamp(end_str)
    duration_sec = 0
    if t_start and t_end:
        duration_sec = (t_end - t_start).total_seconds()
    duration_formatted = format_duration(duration_sec)
    
    cached_session = db.query(WorkSession).filter(WorkSession.sessionId == session_id).first()
    summary_obj = None
    if cached_session and cached_session.summary:
        try:
            summary_obj = json.loads(cached_session.summary)
        except Exception:
            pass
            
    if not summary_obj:
        summary_obj = generate_session_summary_ai(memories)
        if not cached_session:
            cached_session = WorkSession(sessionId=session_id, summary=json.dumps(summary_obj))
            db.add(cached_session)
        else:
            cached_session.summary = json.dumps(summary_obj)
        db.commit()

    db.close()

    types = [m.type for m in memories if m.type]
    top_category = max(set(types), key=types.count) if types else "N/A"

    apps = [m.sourceApp for m in memories if m.sourceApp]
    most_used_app = max(set(apps), key=apps.count) if apps else "N/A"

    important_count = sum(1 for m in memories if getattr(m, 'isImportant', False))
    
    return {
        "sessionId": session_id,
        "sessionStart": start_str,
        "sessionEnd": end_str,
        "duration": duration_formatted,
        "totalMemories": len(memories),
        "topCategory": top_category,
        "mostUsedApp": most_used_app,
        "importantMemories": important_count,
        "summary": summary_obj,
        "memories": memories
    }