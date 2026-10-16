import sqlite3
import json
import os

def export_logs():
    db_path = 'business_logs.db'
    json_path = 'logs.json'
    
    if not os.path.exists(db_path):
        print("База данных не найдена. Создаем пустую...")
        # Создаем пустой JSON, если базы нет
        with open(json_path, 'w') as f:
            json.dump([], f)
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Выбираем последние 100 записей
        cursor.execute('SELECT id, chat_id, event_type, user_id, user_name, content, timestamp FROM events ORDER BY timestamp DESC LIMIT 100')
        rows = cursor.fetchall()
        
        # Преобразуем в список списков (JSON-friendly)
        data = []
        for row in rows:
            data.append(list(row))
            
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"Успешно экспортировано {len(data)} записей в logs.json")
        conn.close()
        
    except Exception as e:
        print(f"Ошибка при экспорте: {e}")
        # На случай ошибки создаем пустой файл, чтобы сайт не ломался
        with open(json_path, 'w') as f:
            json.dump([], f)

if __name__ == "__main__":
    export_logs()
