from database.db import SessionLocal
from database.models import Memory


def get_all_memories(include_pending: bool = False):

    db = SessionLocal()

    if include_pending:
        memories = db.query(Memory).all()
    else:
        memories = db.query(Memory).filter(Memory.pending_confirmation != 1).all()

    db.close()

    return memories