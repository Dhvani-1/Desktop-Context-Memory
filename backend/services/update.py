from database.db import SessionLocal
from database.models import Memory


def update_memory(memory_id, summary, memory_type):

    db = SessionLocal()

    memory = db.query(Memory).filter(
        Memory.id == memory_id
    ).first()

    if memory:

        memory.summary = summary

        memory.type = memory_type

        db.commit()

        db.refresh(memory)

    db.close()

    return memory