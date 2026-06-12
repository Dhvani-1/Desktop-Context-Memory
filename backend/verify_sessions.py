import os
import sys
from datetime import datetime, timedelta

# Adjust path to import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db import SessionLocal, migrate_db
from database.models import Memory, WorkSession
from services.save_memory import save_memory

def run_tests():
    print("Initializing Database...")
    migrate_db()
    
    db = SessionLocal()
    
    print("Clearing database table for clean test...")
    db.query(Memory).delete()
    db.query(WorkSession).delete()
    db.commit()
    
    base_time = datetime(2026, 6, 12, 12, 0, 0)
    
    print("\n--- Test 1: Creating first memory (starts session 1) ---")
    meta1 = {
        "timestamp": base_time.isoformat(),
        "sourceApp": "VS Code",
        "windowTitle": "main.py - Totem - Copy",
        "rawContext": "def hello(): pass",
        "screenshot": "none.png"
    }
    mem1 = {
        "summary": "User is writing python code",
        "type": "Coding",
        "intent": "Coding",
        "topic": "Python",
        "tags": ["python"],
        "sensitivity": "Low",
        "usefulnessScore": 4.0,
        "suggestedNextAction": "Write test"
    }
    id1 = save_memory(meta1, mem1)
    
    record1 = db.query(Memory).filter(Memory.id == id1).first()
    print(f"Memory 1: ID={record1.id}, sessionId={record1.sessionId}, start={record1.sessionStart}, end={record1.sessionEnd}")
    assert record1.sessionId == "1", f"Expected session ID '1', got '{record1.sessionId}'"
    assert record1.sessionStart == meta1["timestamp"]
    assert record1.sessionEnd == meta1["timestamp"]
    
    print("\n--- Test 2: Creating second memory 15 mins later (should group in session 1) ---")
    time2 = base_time + timedelta(minutes=15)
    meta2 = {
        "timestamp": time2.isoformat(),
        "sourceApp": "Chrome",
        "windowTitle": "Stack Overflow",
        "rawContext": "python datetime",
        "screenshot": "none.png"
    }
    mem2 = {
        "summary": "User is researching date parsing",
        "type": "Research",
        "intent": "Research",
        "topic": "Datetime",
        "tags": ["python", "datetime"],
        "sensitivity": "Low",
        "usefulnessScore": 3.0,
        "suggestedNextAction": "Check docs"
    }
    id2 = save_memory(meta2, mem2)
    
    # Reload session to clear cache
    db.close()
    db = SessionLocal()
    
    record1 = db.query(Memory).filter(Memory.id == id1).first()
    record2 = db.query(Memory).filter(Memory.id == id2).first()
    print(f"Memory 1 updated: sessionId={record1.sessionId}, start={record1.sessionStart}, end={record1.sessionEnd}")
    print(f"Memory 2: ID={record2.id}, sessionId={record2.sessionId}, start={record2.sessionStart}, end={record2.sessionEnd}")
    
    assert record2.sessionId == "1", f"Expected memory 2 to share session ID '1', got '{record2.sessionId}'"
    assert record1.sessionEnd == time2.isoformat(), "Expected Memory 1 sessionEnd to be updated"
    assert record2.sessionEnd == time2.isoformat(), "Expected Memory 2 sessionEnd to match"
    
    print("\n--- Test 3: Creating third memory 35 mins later (should start session 2) ---")
    time3 = time2 + timedelta(minutes=35)
    meta3 = {
        "timestamp": time3.isoformat(),
        "sourceApp": "VS Code",
        "windowTitle": "test.py",
        "rawContext": "run test",
        "screenshot": "none.png"
    }
    mem3 = {
        "summary": "User is running test suite",
        "type": "Coding",
        "intent": "Testing",
        "topic": "Tests",
        "tags": ["test"],
        "sensitivity": "Low",
        "usefulnessScore": 5.0,
        "suggestedNextAction": "Finish test"
    }
    id3 = save_memory(meta3, mem3)
    
    record3 = db.query(Memory).filter(Memory.id == id3).first()
    print(f"Memory 3: ID={record3.id}, sessionId={record3.sessionId}, start={record3.sessionStart}, end={record3.sessionEnd}")
    assert record3.sessionId == "2", f"Expected new session ID '2', got '{record3.sessionId}'"
    assert record3.sessionStart == time3.isoformat()
    
    # Check that session 1 end time was not affected
    record1 = db.query(Memory).filter(Memory.id == id1).first()
    assert record1.sessionEnd == time2.isoformat(), "Expected Session 1 end to remain unchanged"
    
    print("\n--- Test 4: Verify unique distinct sessions ---")
    sessions = db.query(Memory.sessionId).distinct().all()
    print("Distinct sessions in DB:", [s[0] for s in sessions])
    assert len(sessions) == 2, "Expected exactly 2 sessions in database"
    
    print("\nALL BACKEND TESTS PASSED SUCCESSFULY!")
    db.close()

if __name__ == "__main__":
    run_tests()
