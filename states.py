# ================================
# states.py
# FSM состояния создания истории
# ================================

from aiogram.fsm.state import StatesGroup, State


class StoryCreation(StatesGroup):
    # Этапы создания истории
    title = State()
    description = State()
    hero_past = State()
    start_scene = State()

    # Этапы добавления персонажа
    char_name = State()
    char_age = State()          # ✅ ВОТ ЭТОГО НЕ ХВАТАЛО
    char_role = State()
    char_personality = State()
