import aiosqlite
import json

async def init_db():
    async with aiosqlite.connect('business_logs.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                event_type TEXT,
                user_id INTEGER,
                user_name TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def log_event(chat_id, event_type, user_id, user_name, content):
    async with aiosqlite.connect('business_logs.db') as db:
        await db.execute(
            'INSERT INTO events (chat_id, event_type, user_id, user_name, content) VALUES (?, ?, ?, ?, ?)',
            (chat_id, event_type, user_id, user_name, content)
        )
        await db.commit()

async def get_events(chat_id=None, limit=50):
    async with aiosqlite.connect('business_logs.db') as db:
        if chat_id:
            query = 'SELECT * FROM events WHERE chat_id = ? ORDER BY timestamp DESC LIMIT ?'
            params = (chat_id, limit)
        else:
            query = 'SELECT * FROM events ORDER BY timestamp DESC LIMIT ?'
            params = (limit,)
            
        async with db.execute(query, params) as cursor:
            return await cursor.fetchall()
