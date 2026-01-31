# ================================
# db.py
# Horror-Studio Bot Database System
# ================================

import sqlite3


# ================================
# Подключение к базе данных
# ================================
DB_NAME = "stories.db"


# ================================
# Инициализация базы данных
# ================================
def init_db():
    """
    Создаёт все нужные таблицы,
    если их ещё нет.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ----------------------------
    # Таблица историй
    # ----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            hero_past TEXT,
            start_scene TEXT
        )
    """)

    # ----------------------------
    # Таблица персонажей
    # ----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER,
            name TEXT,
            role TEXT,
            personality TEXT,
            known TEXT
        )
    """)

    # ----------------------------
    # Таблица сообщений (НОВОЕ)
    # ----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            story_id INTEGER,
            sender TEXT,
            text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ================================
# Истории
# ================================
def add_story(title, description, hero_past, start_scene):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO stories (title, description, hero_past, start_scene)
        VALUES (?, ?, ?, ?)
    """, (title, description, hero_past, start_scene))

    conn.commit()
    story_id = cursor.lastrowid
    conn.close()

    return story_id


def get_stories():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, title FROM stories")
    stories = cursor.fetchall()

    conn.close()
    return stories


def get_story(story_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, description, hero_past, start_scene
        FROM stories
        WHERE id = ?
    """, (story_id,))

    story = cursor.fetchone()
    conn.close()

    return story


# ================================
# Персонажи
# ================================
def add_character(story_id, name, role, personality, known):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO characters (story_id, name, role, personality, known)
        VALUES (?, ?, ?, ?, ?)
    """, (story_id, name, role, personality, known))

    conn.commit()
    conn.close()


def get_characters(story_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, role, personality, known
        FROM characters
        WHERE story_id = ?
    """, (story_id,))

    chars = cursor.fetchall()
    conn.close()
    return chars


# ================================
# Сообщения (НОВОЕ)
# ================================

def save_message(user_id, story_id, sender, text):
    """
    Сохраняет сообщение в историю диалога.
    sender = "player" или "character"
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (user_id, story_id, sender, text)
        VALUES (?, ?, ?, ?)
    """, (user_id, story_id, sender, text))

    conn.commit()
    conn.close()


def get_last_messages(user_id, story_id, limit=20):
    """
    Возвращает последние limit сообщений
    для отправки в Groq.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sender, text
        FROM messages
        WHERE user_id = ? AND story_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (user_id, story_id, limit))

    rows = cursor.fetchall()
    conn.close()

    return list(reversed(rows))


def get_full_dialog(user_id, story_id):
    """
    Возвращает весь диалог полностью.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sender, text, timestamp
        FROM messages
        WHERE user_id = ? AND story_id = ?
        ORDER BY id ASC
    """, (user_id, story_id))

    dialog = cursor.fetchall()
    conn.close()

    return dialog
