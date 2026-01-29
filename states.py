# ================================
# states.py
# FSM состояния для создания истории
# ================================

from aiogram.fsm.state import StatesGroup, State


class StoryCreation(StatesGroup):
    # Шаги создания истории
    title = State()
    description = State()
    hero_past = State()
    start_scene = State()

    # Персонажи
    char_name = State()
    char_role = State()
    char_personality = State()
    char_known = State()
