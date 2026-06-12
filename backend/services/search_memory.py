from database.db import SessionLocal
from database.models import Memory
from sqlalchemy import or_


def search_memory(query):

    db = SessionLocal()

    results = db.query(Memory).filter(
        or_(
            Memory.summary.contains(query),
            Memory.title.contains(query)
        ),
        Memory.pending_confirmation != 1
    ).all()

    db.close()

    return results