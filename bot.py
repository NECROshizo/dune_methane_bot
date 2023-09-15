from math import comb

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_reader import config
from magic_filter import F
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest


from keyboards import get_keyboard_rolling, RollCallbackFactory

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")

dp = Dispatcher()

user_data = {}
DICE = 20
PULL_DEFAULT = {
    "dice": 2,
    "skill": 4,
    "motive": 4,
    "complexity": 1,
}


# TODO неверное общее вычесление с критическим успехом проверить
def get_probility(dices: int, skill: int, motive: int, complexity: int) -> tuple:
    """Подсчет вероятностей успеха"""
    success = (skill + motive) / DICE
    crit_succes = skill / DICE
    fail = 1 - success
    crit_fail = 1 - crit_succes
    probability = 1 - sum(
        comb(dices, i) * success**i * fail ** (dices - i)
        for i in range(complexity)
    )
    crit_probability = 1 - sum(
        comb(dices, i) * crit_succes**i * crit_fail ** (dices - i)
        for i in range(complexity)
    )
    all_probability = probability * (1 + crit_probability)

    return probability * 100, all_probability * 100


async def update_prob_text(message: types.Message, new_pull: dict[str, int]):
    """Обновление сообщения"""
    with suppress(TelegramBadRequest):
        probility, probability_critical = get_probility(*new_pull.values())
        dice, skill, motiv, complexity = new_pull.values()
        await message.edit_text(
            f"Вероятность успеха при пулле из [{dice}] кубов\n"
            f"с навыком [{skill}] и мотивом [{motiv}] со "
            f"сложностью [{complexity}]\n"
            f"равна {probility}%, со специализацией {probability_critical}%",
            reply_markup=get_keyboard_rolling(),
        )


@dp.message(Command("rolldice"))
async def cmd_numbers(message: types.Message):
    """Инициализация запроса"""
    user_data[message.from_user.id] = PULL_DEFAULT
    data: dict = user_data[message.from_user.id]
    probility, probability_critical = get_probility(*data.values())
    await message.answer(
        f"Вероятность успеха при пулле из [2] кубов\n"
        f"с навыком [4] и мотивом [4] со сложностью [1]\n"
        f"равна {probility}%, со специализацией {probability_critical}%",
        reply_markup=get_keyboard_rolling(),
    )


@dp.callback_query(RollCallbackFactory.filter(F.action == "dices"))
async def callbacks_dice_change_fab(
    callback: types.CallbackQuery, callback_data: RollCallbackFactory
):
    user_pull = user_data.get(callback.from_user.id, PULL_DEFAULT)
    user_pull["dice"] = callback_data.value
    user_data[callback.from_user.id] = user_pull
    await update_prob_text(callback.message, user_pull)
    await callback.answer()


@dp.callback_query(RollCallbackFactory.filter(F.action == "skill"))
async def callbacks_skill_change_fab(
    callback: types.CallbackQuery, callback_data: RollCallbackFactory
):
    user_pull = user_data.get(callback.from_user.id, PULL_DEFAULT)
    user_pull["skill"] += callback_data.value
    user_data[callback.from_user.id] = user_pull
    await update_prob_text(callback.message, user_pull)
    await callback.answer()


@dp.callback_query(RollCallbackFactory.filter(F.action == "motive"))
async def callbacks_motive_change_fab(
    callback: types.CallbackQuery, callback_data: RollCallbackFactory
):
    user_pull = user_data.get(callback.from_user.id, PULL_DEFAULT)
    user_pull["motive"] += callback_data.value
    user_data[callback.from_user.id] = user_pull
    await update_prob_text(callback.message, user_pull)
    await callback.answer()


@dp.callback_query(RollCallbackFactory.filter(F.action == "complexity"))
async def callbacks_complexity_change_fab(
    callback: types.CallbackQuery, callback_data: RollCallbackFactory
):
    user_pull = user_data.get(callback.from_user.id, PULL_DEFAULT)
    user_pull["complexity"] += callback_data.value
    user_data[callback.from_user.id] = user_pull
    await update_prob_text(callback.message, user_pull)
    await callback.answer()


@dp.callback_query(RollCallbackFactory.filter(F.action == "stop"))
async def callbacks_stop_change_fab(callback: types.CallbackQuery):
    await callback.message.edit_text("Долг выполнен")
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
