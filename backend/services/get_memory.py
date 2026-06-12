from database.db import SessionLocal
from database.models import Memory


def get_memory_by_id(memory_id):

    db = SessionLocal()

    memory = db.query(Memory).filter(
        Memory.id == memory_id
    ).first()

    db.close()

    return memory