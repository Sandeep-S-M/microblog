import sys
import os
# Add parent directory to path so we can import 'microblog' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from microblog import app, db
from sqlalchemy import text

print("Attempting to patch database schema...")
with app.app_context():
    try:
        # Check if column exists first to avoid error if re-run
        # SQLite doesn't have IF NOT EXISTS for ADD COLUMN in older versions, but let's try direct add and catch error
        print("Adding column last_message_read_time to user table...")
        db.session.execute(text("ALTER TABLE user ADD COLUMN last_message_read_time DATETIME"))
        db.session.commit()
        print("Successfully added column last_message_read_time to user table.")
    except Exception as e:
        print(f"Error (might be already present): {e}")
