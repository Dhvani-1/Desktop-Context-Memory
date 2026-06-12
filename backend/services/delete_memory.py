from database.db import SessionLocal
from database.models import Memory


def delete_memory(memory_id):

    db = SessionLocal()

    memory = db.query(Memory).filter(
        Memory.id == memory_id
    ).first()

    if memory:

        if memory.screenshot:
            import os
            if os.path.exists(memory.screenshot):
                try:
                    os.remove(memory.screenshot)
                    print(f"Deleted screenshot file: {memory.screenshot}")
                except Exception as e:
                    print("Error deleting screenshot file:", e)

        db.delete(memory)

        db.commit()

    db.close()