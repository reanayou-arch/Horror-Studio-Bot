# ================================
# groq_ai.py
# Подключение Groq API для AI-ответов
# ================================

import requests
from config import GROQ_API_KEY


MODEL_NAME = "llama-3.1-8b-instant"


def generate_story_reply(story_data, characters, user_message):
    """
    Генерация ответа AI в стиле Horror-Studio.

    story_data = (title, description, hero_past, start_scene)
    characters = список персонажей
    user_message = сообщение игрока
    """

    title, description, hero_past, start_scene = story_data

    # Формируем список персонажей для промпта
    char_text = ""
    for c in characters:
        name, role, personality, known_status = c
        char_text += f"- {name} ({role}), характер: {personality}, статус: {known_status}\n"

    # Главный промпт Horror-Studio
    prompt = f"""
Ты — AI-движок Horror-Studio.
Ты пишешь хоррор историю в формате настоящей переписки.

История: {title}

Описание автора (основа сюжета):
{description}

Прошлое главного героя:
{hero_past}

Персонажи:
{char_text}

Правила:
- Игрок — главный герой, он единственный реальный человек.
- Все остальные персонажи отвечают как живые люди в чате.
- Сообщения короткие, как в Telegram.
- Атмосфера хоррора, напряжение.
- Диалог должен быть логичным, связанным, не мусорным.
- Не пиши слишком длинные рассказы — это переписка.

Сообщение игрока:
{user_message}

Ответ:
(Напиши 1-3 сообщения от персонажей, как переписку)
"""

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9,
        "max_tokens": 250
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        return "⚠️ Ошибка AI ответа. Проверь Groq ключ."

    data = response.json()
    return data["choices"][0]["message"]["content"]
