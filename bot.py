import asyncio
import logging
from aiogram import Bot, Dispatcher, types, html
from aiogram.filters.command import Command
from aiogram.filters import CommandObject, Text
from aiogram.types.dice import DiceEmoji
from config_reader import config

# from aiogram import F
from magic_filter import F
from datetime import datetime
from aiogram.utils.markdown import hide_link
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from random import randint
from math import comb, factorial
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from dataclasses import dataclass


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


class RollCallbackFactory(CallbackData, prefix="roll"):
    action: str
    value: Optional[int]


def get_keyboard():
    builder = InlineKeyboardBuilder()
    # dices
    builder.button(text="2", callback_data=RollCallbackFactory(action="dices", value=2))
    builder.button(text="3", callback_data=RollCallbackFactory(action="dices", value=3))
    builder.button(text="4", callback_data=RollCallbackFactory(action="dices", value=4))
    builder.button(text="5", callback_data=RollCallbackFactory(action="dices", value=5))
    # skill
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
    # motiv
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
    # complexity
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


def get_probility(dices: int, skill: int, motive: int, complexity: int):
    def choose(N, i):
        """
        Вычисляет количество комбинаций из N элементов, выбирая i элементов из них.
        """
        from math import factorial

        return factorial(N) // (factorial(i) * factorial(N - i))

    def binom(i, N, T1, T2):
        p1 = (T1 // 20) + 1
        q1 = (T1 % 20) / 20
        p2 = (T2 // 20) + 1
        q2 = (T2 % 20) / 20
        prob = (
            choose(N, i)
            * ((q1**i) * ((1 - p1) ** (N - i)))
            * (
                (q2 ** (i - min(i, (N - i + 1))))
                * ((1 - p2) ** (N - i - max(0, (N - i + 1) - i)))
            )
        )
        return prob

    success = (skill + motive) / DICE
    fail = 1 - success
    probability = 1 - sum(
        comb(dices, i) * success**i * fail ** (dices - i) for i in range(complexity)
    )

    # success_skill = (skill - 1) / DICE
    # success_motive = motive / DICE
    # success_critical = success_skill + success_motive
    # fail_critical = 1 - success_critical
    # probability_critical = 0
    # for i in range(complexity, dices + 1):
    #     probability_critical += (comb(dices, i
    #                                   ) * ((success_skill**(2 * i - dices)
    #                                         ) * ((success_critical**(dices - i)
    #                                               ) * (fail_critical ** i
    #                                                    ) * (
    #                                                     min(i, (dices - i + 1))
    #                                                     + (i > 0 and (dices - i + 1) > 0)
    #                                                     )))                                                           )
    # (min(i, (N - i + 1)) + (i > 0 and (N - i + 1) > 0))))

    N = dices
    T1 = skill
    T2 = motive
    S = complexity

    prob = 0
    for i in range(S, N + 1):
        prob += (
            choose(N, i) * (T1 / 20) ** (2 * i - N) * ((T1 + T2) / 20) ** (N - 2 * i)
        )

    return round(probability * 100, 2), round(prob * 100, 2)

    # p1 = (T1 - 1) / 20
    # p2 = T2 / 20
    # q = 1 - (p1 + p2)
    # prob = 0
    # for i in range(S, N+1):
    #     prob += (comb(N, i) *
    #              ((p1 ** (2 * i - N)) *
    #               ((p1 + p2) ** (N - i)) *
    #               (q ** i) *
    #               (min(i, (N - i + 1)) + (i > 0 and (N - i + 1) > 0))))

    # p1 = (T1 - 1) / 20  # вероятность успеха на одном броске для первого случая
    # p2 = T2 / 20  # вероятность успеха на одном броске для второго случая
    # q = 1 - p1 - p2  # вероятность неудачи на одном броске

    # вычисляем вероятность успеха в S или более бросках
    # prob = sum([choose(N, i) * p1**(2*i ) * (p2+p1)**(-i) * q**(N-3*i) for i in range(S // 2 + 1)])

    # p1 = (T1 - 1) / 20
    # p2 = T2 / 20
    # q = 1 - (p1 + p2)
    # prob = 0
    # for i in range(S, N+1):
    #     prob += comb(N, i) * (p1 ** (2 * i - N)) * ((p1 + p2) ** (N - i)) * (q ** (N-i))

    # if T1 == 0:
    #     # если T1 = 0, используем формулу биномиального распределения
    #     T = T2
    #     p = (T // 20) + 1
    #     q = (T % 20) / 20
    #     prob = 1 - ((1 - q) ** N) * ((1 - p) ** S)
    # else:
    #     # иначе используем формулу, учитывающую оба значения T1 и T2
    #     prob = 0
    #     for i in range(S, N + 1):
    #         prob += binom(i, N, T1, T2)

    # return round(probability * 100, 2), round(probability_critical * 100, 2)

    # return round(probability * 100, 2), round(success_prob * 100, 2)


async def update_prob_text(message: types.Message, new_pull: dict[str, int]):
    with suppress(TelegramBadRequest):
        probility, probability_critical = get_probility(*new_pull.values())
        dice, skill, motiv, complexity = new_pull.values()
        await message.edit_text(
            f"Вероятность успеха при пулле из [{dice}] кубов\n"
            f"с навыком [{skill}] и мотивом [{motiv}] со "
            f"сложностью [{complexity}]\n"
            f"равна {probility}%, со специализацией {probability_critical}%",
            reply_markup=get_keyboard(),
        )


@dp.message(Command("rolldice"))
async def cmd_numbers(message: types.Message):
    user_data[message.from_user.id] = PULL_DEFAULT
    data: dict = user_data[message.from_user.id]
    probility, probability_critical = get_probility(*data.values())
    await message.answer(
        f"Вероятность успеха при пулле из [2] кубов\n"
        f"с навыком [4] и мотивом [4] со сложностью [1]\n"
        f"равна {probility}%, со специализацией {probability_critical}%",
        reply_markup=get_keyboard(),
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


#
# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
