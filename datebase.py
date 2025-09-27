import sqlite3
import os

def create_table():
    """创建数据库表，如果表已存在则跳过"""
    conn = sqlite3.connect('qq.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT,
            message_id TEXT,
            message TEXT,
            time TEXT
        )
    ''')
    conn.commit()
    conn.close()

def init_database():
    """初始化数据库，如果数据库文件不存在则创建"""
    if not os.path.exists('qq.db'):
        print("Database file not found, creating new database...")
        create_table()
        print("Database initialized successfully!")
    else:
        print("Database file exists, skipping initialization.")

def insert_data(group_id, message_id, message, time):
    conn = sqlite3.connect('qq.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO qq (group_id, message_id, message, time) VALUES (?, ?, ?, ?)
    ''', (group_id, message_id, message, time))
    conn.commit()
    conn.close()

def remove_data(group_id, message_id):
    conn = sqlite3.connect('qq.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM qq WHERE group_id = ? AND message_id = ?
    ''', (group_id, message_id))
    conn.commit()
    conn.close()

def find_if_exist(group_id, message_id):
    conn = sqlite3.connect('qq.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM qq WHERE group_id = ? AND message_id = ?
    ''', (group_id, message_id))
    result = cursor.fetchone()
    conn.close()
    return result

def iter_data():
    conn = sqlite3.connect('qq.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM qq
    ''')
    result = cursor.fetchall()
    conn.close()
    return result

if __name__ == "__main__":
    remove_data('1062848088', '98224408')
    for i in iter_data():
        print(i)