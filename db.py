# ================================
# db.py
# Работа с базой данных SQLite
# ================================

import sqlite3


DB_NAME = "stories.db"


def init_db():
    """
    Создаём базу данных и таблицы,
    если они ещё не существуют.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Таблица историй
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            hero_past TEXT,
            start_scene TEXT
        )
    """)

    # Таблица персонажей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER,
            name TEXT,
            role TEXT,
            personality TEXT,
            known_status TEXT,
            FOREIGN KEY(story_id) REFERENCES stories(id)
        )
    """)

    conn.commit()
    conn.close()


def add_story(title, description, hero_past, start_scene):
    """
    Добавляем историю в базу.
    Возвращаем ID созданной истории.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO stories (title, description, hero_past, start_scene)
        VALUES (?, ?, ?, ?)
    """, (title, description, hero_past, start_scene))

    story_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return story_id


def add_character(story_id, name, role, personality, known_status):
    """
    Добавляем персонажа в историю.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO characters (story_id, name, role, personality, known_status)
        VALUES (?, ?, ?, ?, ?)
    """, (story_id, name, role, personality, known_status))

    conn.commit()
    conn.close()


def get_stories():
    """
    Получаем список всех историй.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, title FROM stories")
    stories = cursor.fetchall()

    conn.close()
    return stories


def get_story(story_id):
    """
    Получаем полную информацию об истории.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, description, hero_past, start_scene
        FROM stories WHERE id=?
    """, (story_id,))
    story = cursor.fetchone()

    conn.close()
    return story


def get_characters(story_id):
    """
    Получаем персонажей конкретной истории.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, role, personality, known_status
        FROM characters WHERE story_id=?
    """, (story_id,))
    chars = cursor.fetchall()

    conn.close()
    return chars


def delete_story(story_id):
    """
    Удаляем историю и всех её персонажей.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM characters WHERE story_id=?", (story_id,))
    cursor.execute("DELETE FROM stories WHERE id=?", (story_id,))

    conn.commit()
    conn.close()
