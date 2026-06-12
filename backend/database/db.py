from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///memory.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def migrate_db():
    from sqlalchemy import text
    with engine.begin() as conn:
        # Migrate pending_confirmation
        try:
            conn.execute(text("SELECT pending_confirmation FROM memories LIMIT 1"))
        except Exception:
            print("Database migration: Adding pending_confirmation column to memories table...")
            try:
                conn.execute(text("ALTER TABLE memories ADD COLUMN pending_confirmation INTEGER DEFAULT 0"))
                print("Database migration successful for pending_confirmation.")
            except Exception as migration_error:
                print(f"Database migration failed for pending_confirmation: {migration_error}")

        # Migrate sensitivityReason
        try:
            conn.execute(text("SELECT sensitivityReason FROM memories LIMIT 1"))
        except Exception:
            print("Database migration: Adding sensitivityReason column to memories table...")
            try:
                conn.execute(text("ALTER TABLE memories ADD COLUMN sensitivityReason TEXT"))
                print("Database migration successful for sensitivityReason.")
            except Exception as migration_error:
                print(f"Database migration failed for sensitivityReason: {migration_error}")

        # Migrate title
        try:
            conn.execute(text("SELECT title FROM memories LIMIT 1"))
        except Exception:
            print("Database migration: Adding title column to memories table...")
            try:
                conn.execute(text("ALTER TABLE memories ADD COLUMN title TEXT"))
                print("Database migration successful for title.")
            except Exception as migration_error:
                print(f"Database migration failed for title: {migration_error}")

        # Migrate isImportant
        try:
            conn.execute(text("SELECT isImportant FROM memories LIMIT 1"))
        except Exception:
            print("Database migration: Adding isImportant column to memories table...")
            try:
                conn.execute(text("ALTER TABLE memories ADD COLUMN isImportant BOOLEAN DEFAULT FALSE"))
                print("Database migration successful for isImportant.")
            except Exception as migration_error:
                print(f"Database migration failed for isImportant: {migration_error}")

        # Migrate sessionId
        try:
            conn.execute(text("SELECT sessionId FROM memories LIMIT 1"))
        except Exception:
            print("Database migration: Adding sessionId column to memories table...")
            try:
                conn.execute(text("ALTER TABLE memories ADD COLUMN sessionId TEXT"))
                print("Database migration successful for sessionId.")
            except Exception as migration_error:
                print(f"Database migration failed for sessionId: {migration_error}")

        # Migrate sessionStart
        try:
            conn.execute(text("SELECT sessionStart FROM memories LIMIT 1"))
        except Exception:
            print("Database migration: Adding sessionStart column to memories table...")
            try:
                conn.execute(text("ALTER TABLE memories ADD COLUMN sessionStart TEXT"))
                print("Database migration successful for sessionStart.")
            except Exception as migration_error:
                print(f"Database migration failed for sessionStart: {migration_error}")

        # Migrate sessionEnd
        try:
            conn.execute(text("SELECT sessionEnd FROM memories LIMIT 1"))
        except Exception:
            print("Database migration: Adding sessionEnd column to memories table...")
            try:
                conn.execute(text("ALTER TABLE memories ADD COLUMN sessionEnd TEXT"))
                print("Database migration successful for sessionEnd.")
            except Exception as migration_error:
                print(f"Database migration failed for sessionEnd: {migration_error}")

        # Migrate/create work_sessions table
        try:
            conn.execute(text("CREATE TABLE IF NOT EXISTS work_sessions (sessionId TEXT PRIMARY KEY, summary TEXT)"))
            print("Database migration: work_sessions table created or already exists.")
        except Exception as migration_error:
            print(f"Database migration failed for work_sessions table: {migration_error}")