from microblog import app, db
from microblog.models import Message, User
import sqlalchemy as sa

with app.app_context():
    # Get all messages ordered by timestamp
    messages = db.session.scalars(
        sa.select(Message).order_by(Message.timestamp.desc()).limit(20)
    ).all()
    
    print(f"Total messages in last 20: {len(messages)}\n")
    print("ID | Sender -> Recipient | Body | Timestamp")
    print("-" * 80)
    
    for msg in messages:
        sender = msg.author.username
        recipient = msg.recipient.username
        body = msg.body[:30] + "..." if len(msg.body) > 30 else msg.body
        timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{msg.id:3d} | {sender:10s} -> {recipient:10s} | {body:30s} | {timestamp}")
    
    # Check for exact duplicates
    print("\n" + "=" * 80)
    print("Checking for duplicate messages (same sender, recipient, body, timestamp):")
    print("=" * 80)
    
    duplicates = db.session.execute(
        sa.text("""
            SELECT sender_id, recipient_id, body, timestamp, COUNT(*) as count
            FROM message
            GROUP BY sender_id, recipient_id, body, timestamp
            HAVING COUNT(*) > 1
        """)
    ).fetchall()
    
    if duplicates:
        print(f"\nFound {len(duplicates)} sets of duplicate messages:")
        for dup in duplicates:
            print(f"  Sender ID: {dup[0]}, Recipient ID: {dup[1]}, Body: {dup[2][:30]}, Count: {dup[4]}")
    else:
        print("\nNo duplicate messages found in database!")
