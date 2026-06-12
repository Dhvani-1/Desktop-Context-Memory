import json
from datetime import datetime

from database.db import SessionLocal
from database.models import Memory, WorkSession


def parse_timestamp(ts_str):
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str)
    except Exception:
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(ts_str, fmt)
            except Exception:
                continue
    return None


def save_memory(metadata, memory, pending_confirmation: int = 0, sensitivity_reason: str = None):

    db = SessionLocal()

    current_time_str = metadata["timestamp"]
    current_time = parse_timestamp(current_time_str)

    # Retrieve the last saved memory overall
    last_memory = db.query(Memory).order_by(Memory.id.desc()).first()

    session_id = None
    session_start = None
    session_end = None

    if last_memory and last_memory.sessionId:
        last_time = parse_timestamp(last_memory.createdAt)
        if last_time and current_time:
            time_diff = (current_time - last_time).total_seconds()
            if time_diff <= 1800:  # 30 minutes
                session_id = last_memory.sessionId
                session_start = last_memory.sessionStart
                session_end = current_time_str

                # Update all other memories in the active session
                db.query(Memory).filter(Memory.sessionId == session_id).update({"sessionEnd": session_end})
                # Invalidate cached session summary
                db.query(WorkSession).filter(WorkSession.sessionId == session_id).delete()

    if not session_id:
        # Generate new sequential session ID
        session_ids = db.query(Memory.sessionId).filter(Memory.sessionId.isnot(None)).distinct().all()
        numeric_ids = []
        for (sid,) in session_ids:
            try:
                numeric_ids.append(int(sid))
            except (ValueError, TypeError):
                pass
        next_num_id = max(numeric_ids) + 1 if numeric_ids else 1
        session_id = str(next_num_id)
        session_start = current_time_str
        session_end = current_time_str

    record = Memory(

        createdAt=current_time_str,

        sourceApp=metadata["sourceApp"],

        windowTitle=metadata["windowTitle"],

        rawContext=metadata["rawContext"],

        summary=memory["summary"],

        type=memory["type"],

        intent=memory["intent"],

        topic=memory["topic"],

        tags=json.dumps(memory["tags"]),

        sensitivity=memory["sensitivity"],

        usefulnessScore=memory["usefulnessScore"],

        suggestedNextAction=memory["suggestedNextAction"],

        screenshot=metadata["screenshot"],

        pending_confirmation=pending_confirmation,

        sensitivityReason=sensitivity_reason,

        title=memory.get("title"),

        sessionId=session_id,

        sessionStart=session_start,

        sessionEnd=session_end
    )

    db.add(record)

    db.commit()

    db.refresh(record)

    db.close()

    return record.id