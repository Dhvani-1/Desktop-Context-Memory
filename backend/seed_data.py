import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db import SessionLocal, migrate_db
from database.models import Memory, WorkSession
from services.save_memory import save_memory

def seed():
    print("Seeding database...")
    db = SessionLocal()
    db.query(Memory).delete()
    db.query(WorkSession).delete()
    db.commit()
    
    # Session 1: 3 hours ago, Coding on API
    base_time_1 = datetime.now() - timedelta(hours=3)
    
    # Mem 1: VS Code - api design
    save_memory({
        "timestamp": base_time_1.isoformat(),
        "sourceApp": "VS Code",
        "windowTitle": "models.py - Totem",
        "rawContext": "class Memory(Base):\n    isImportant = Column(Boolean)",
        "screenshot": "screenshots/seed1.png"
    }, {
        "summary": "Designed models and schema for SQLite memory system",
        "type": "Coding",
        "intent": "API Design",
        "topic": "SQLite schema",
        "tags": ["SQLite", "python", "sqlalchemy"],
        "sensitivity": "Low",
        "usefulnessScore": 4.0,
        "suggestedNextAction": "Create migrations"
    })
    
    # Mem 2: Chrome - Stack Overflow (10 mins later)
    save_memory({
        "timestamp": (base_time_1 + timedelta(minutes=10)).isoformat(),
        "sourceApp": "Google Chrome",
        "windowTitle": "SQLAlchemy migrations - Google Search",
        "rawContext": "https://stackoverflow.com/questions/sqlalchemy-migrations",
        "screenshot": "screenshots/seed2.png"
    }, {
        "summary": "Researched SQLAlchemy table alteration and migrations in SQLite",
        "type": "Research",
        "intent": "Researching SQLite capabilities",
        "topic": "Migrations",
        "tags": ["SQLAlchemy", "SQLite", "migrations"],
        "sensitivity": "Low",
        "usefulnessScore": 3.0,
        "suggestedNextAction": "Implement db.py migrate_db"
    })
    
    # Mem 3: VS Code - migration coding (20 mins later, make important)
    mid3 = save_memory({
        "timestamp": (base_time_1 + timedelta(minutes=20)).isoformat(),
        "sourceApp": "VS Code",
        "windowTitle": "db.py - Totem",
        "rawContext": "def migrate_db():\n    try:\n        conn.execute('ALTER TABLE memories ADD...')",
        "screenshot": "screenshots/seed3.png"
    }, {
        "summary": "Implemented self-applying migrations for pending_confirmation and isImportant",
        "type": "Coding",
        "intent": "Migration logic implementation",
        "topic": "Migrations",
        "tags": ["python", "SQLite", "migration"],
        "sensitivity": "Low",
        "usefulnessScore": 5.0,
        "suggestedNextAction": "Verify uvicorn reload"
    })
    # Make important
    m3 = db.query(Memory).filter(Memory.id == mid3).first()
    m3.isImportant = True
    db.commit()

    # Session 2: 1 hour ago, Designing frontend layout
    base_time_2 = datetime.now() - timedelta(hours=1)
    
    # Mem 4: VS Code - App.jsx styling
    save_memory({
        "timestamp": base_time_2.isoformat(),
        "sourceApp": "VS Code",
        "windowTitle": "App.jsx - Totem (Frontend)",
        "rawContext": "const [importanceFilter, setImportanceFilter] = useState('all')",
        "screenshot": "screenshots/seed4.png"
    }, {
        "summary": "Created frontend toggle stars and filter dropdowns for important memories",
        "type": "Coding",
        "intent": "UI Enhancement",
        "topic": "Frontend important filters",
        "tags": ["React", "CSS", "UI"],
        "sensitivity": "Low",
        "usefulnessScore": 4.0,
        "suggestedNextAction": "Verify animations"
    })
    
    # Chrome - Localhost dashboard view (15 mins later)
    save_memory({
        "timestamp": (base_time_2 + timedelta(minutes=15)).isoformat(),
        "sourceApp": "Google Chrome",
        "windowTitle": "Totem Dashboard",
        "rawContext": "http://localhost:5173/",
        "screenshot": "screenshots/seed5.png"
    }, {
        "summary": "Manually verified premium glassmorphism layouts, star toggle bouncers, and select options",
        "type": "Research",
        "intent": "Manual UI testing",
        "topic": "UI Verification",
        "tags": ["React", "frontend", "CSS"],
        "sensitivity": "Low",
        "usefulnessScore": 4.5,
        "suggestedNextAction": "Implement QA Assistant widget"
    })
    
    # VS Code - QA assistant (25 mins later)
    mid6 = save_memory({
        "timestamp": (base_time_2 + timedelta(minutes=25)).isoformat(),
        "sourceApp": "VS Code",
        "windowTitle": "App.jsx - Totem (Frontend)",
        "rawContext": "<div className='floating-assistant-container'>",
        "screenshot": "screenshots/seed6.png"
    }, {
        "summary": "Replaced Ask button with a floating interactive assistant widget in the bottom-right corner",
        "type": "Coding",
        "intent": "Chat Assistant Integration",
        "topic": "UI Components",
        "tags": ["React", "UI", "Chatbot"],
        "sensitivity": "Low",
        "usefulnessScore": 5.0,
        "suggestedNextAction": "Done"
    })
    m6 = db.query(Memory).filter(Memory.id == mid6).first()
    m6.isImportant = True
    db.commit()
    
    db.close()
    print("Seed complete.")

if __name__ == "__main__":
    seed()
