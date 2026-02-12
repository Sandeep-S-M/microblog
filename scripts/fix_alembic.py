import sqlite3
import os
from datetime import datetime, timezone

# Ensure we are in the right directory
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database.db')

print(f"Checking database at: {db_path}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # 1. Clean up failed migration artifacts (tables that shouldn't exist yet or are temp)
        cursor.execute("DROP TABLE IF EXISTS notification")
        print("Dropped notification table (cleaning up failed migration).")
        
        cursor.execute("DROP TABLE IF EXISTS _alembic_tmp_user")
        print("Dropped _alembic_tmp_user if it existed.")

        # 2. Reset migration history
        cursor.execute("DROP TABLE IF EXISTS alembic_version")
        print("Dropped alembic_version table.")

        # 3. Fix data integrity issues
        now = datetime.now(timezone.utc).isoformat()
        
        # Check for NULL last_seen
        cursor.execute("SELECT id FROM user WHERE last_seen IS NULL")
        null_users = cursor.fetchall()
        if null_users:
            print(f"Found {len(null_users)} users with NULL last_seen. Fixing...")
            cursor.execute("UPDATE user SET last_seen = ? WHERE last_seen IS NULL", (now,))
            conn.commit()
            print("Fixed NULL last_seen values.")
        
        # Check for NULL about_me
        cursor.execute("UPDATE user SET about_me = '' WHERE about_me IS NULL")
        
         # Check for NULL password_hash
        cursor.execute("UPDATE user SET password_hash = '' WHERE password_hash IS NULL")
        
        conn.commit()
        print("Data integrity checks complete.")
        print("\nIMPORTANT: Please delete the file 'migrations/versions/e54f008cf197_notifications_table.py' before running migrate again!")
        print("Then run: flask db migrate -m 'notifications table' && flask db upgrade")

    except sqlite3.OperationalError as e:
        print(f"SQLite Error: {e}")
    finally:
        conn.close()
else:
    print(f"Error: Database file not found at {db_path}")
