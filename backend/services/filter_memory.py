from database.db import SessionLocal
from database.models import Memory


def filter_memory(memory_type):

    db = SessionLocal()

    results = db.query(Memory).filter(
        Memory.type.ilike(memory_type.strip()),
        Memory.pending_confirmation != 1
    ).all()

    db.close()

    return results