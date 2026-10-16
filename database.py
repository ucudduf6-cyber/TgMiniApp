import aiosqlite

async def init_db():
    async with aiosqlite.connect('remember.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS saved_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_id INTEGER,
                content_type TEXT,
                text_content TEXT,
                file_id TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()
