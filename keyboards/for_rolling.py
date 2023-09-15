from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class RollCallbackFactory(CallbackData, prefix="roll"):
    action: str
    value: Optional[int]


def get_keyboard_rolling():
    """Описание клавиатуры"""
    builder = InlineKeyboardBuilder()
    # Кнопки количества брозаемых кубов
    builder.button(text="2", callback_data=RollCallbackFactory(action="dices", value=2))
    builder.button(text="3", callback_data=RollCallbackFactory(action="dices", value=3))
    builder.button(text="4", callback_data=RollCallbackFactory(action="dices", value=4))
    builder.button(text="5", callback_data=RollCallbackFactory(action="dices", value=5))
    # Кнопки увелечения или уменьшения значения навыка
    builder.button(
        text="-2 SD", callback_data=RollCallbackFactory(action="skill", value=-2)
    )
    builder.button(
        text="-1 SD", callback_data=RollCallbackFactory(action="skill", value=-1)
    )
    builder.button(
        text="+1 SD", callback_data=RollCallbackFactory(action="skill", value=1)
    )
    builder.button(
        text="+2 SD", callback_data=RollCallbackFactory(action="skill", value=2)
    )
    # Кнопки увелечения или уменьшения значения мотива
    builder.button(
        text="-2 MD", callback_data=RollCallbackFactory(action="motive", value=-2)
    )
    builder.button(
        text="-1 MD", callback_data=RollCallbackFactory(action="motive", value=-1)
    )
    builder.button(
        text="+1 MD", callback_data=RollCallbackFactory(action="motive", value=1)
    )
    builder.button(
        text="+2 MD", callback_data=RollCallbackFactory(action="motive", value=2)
    )
    # Кнопки увелечения или уменьшения значения необходимой сложности
    builder.button(
        text="-2 C", callback_data=RollCallbackFactory(action="complexity", value=-2)
    )
    builder.button(
        text="-1 C", callback_data=RollCallbackFactory(action="complexity", value=-1)
    )
    builder.button(
        text="+1 C", callback_data=RollCallbackFactory(action="complexity", value=1)
    )
    builder.button(
        text="+2 C", callback_data=RollCallbackFactory(action="complexity", value=2)
    )
    builder.button(
        text="Закончить анализ", callback_data=RollCallbackFactory(action="stop")
    )
    builder.adjust(4)
    return builder.as_markup()
