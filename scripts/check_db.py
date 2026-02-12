import sqlite3
import os

# Path to your database
db_path = os.path.join(os.path.dirname(__file__), 'microblog', 'database.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all messages
cursor.execute("""
    SELECT id, sender_id, recipient_id, body, timestamp 
    FROM message 
    ORDER BY timestamp DESC 
    LIMIT 30
""")

messages = cursor.fetchall()

print("=" * 100)
print("RECENT MESSAGES (Last 30)")
print("=" * 100)
print(f"{'ID':<5} {'Sender':<10} {'Recipient':<10} {'Body':<40} {'Timestamp':<20}")
print("-" * 100)

for msg in messages:
    msg_id, sender_id, recipient_id, body, timestamp = msg
    body_short = (body[:37] + '...') if len(body) > 40 else body
    print(f"{msg_id:<5} {sender_id:<10} {recipient_id:<10} {body_short:<40} {timestamp:<20}")

# Check for exact duplicates
print("\n" + "=" * 100)
print("CHECKING FOR DUPLICATE MESSAGES")
print("=" * 100)

cursor.execute("""
    SELECT sender_id, recipient_id, body, timestamp, COUNT(*) as count
    FROM message
    GROUP BY sender_id, recipient_id, body, timestamp
    HAVING COUNT(*) > 1
    ORDER BY timestamp DESC
""")

duplicates = cursor.fetchall()

if duplicates:
    print(f"\n⚠️  Found {len(duplicates)} sets of duplicate messages:\n")
    for dup in duplicates:
        sender_id, recipient_id, body, timestamp, count = dup
        body_short = (body[:37] + '...') if len(body) > 40 else body
        print(f"  • Sender: {sender_id}, Recipient: {recipient_id}")
        print(f"    Body: {body_short}")
        print(f"    Timestamp: {timestamp}")
        print(f"    Count: {count} duplicates\n")
else:
    print("\n✅ No duplicate messages found in the database!")

conn.close()
