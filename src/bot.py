import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.config import BOT_TOKEN
from .schedule_parser import get_schools_and_years, get_groups_by_url, get_schedule_by_group_id
from .db import init_db, save_user_group, get_user_group

# только погода
from .weather_api import get_weather_now, get_weather_forecast

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_data = {}

# ================== ГЛАВНОЕ МЕНЮ ==================
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Выбрать группу"), KeyboardButton(text="Моё расписание")],
        [KeyboardButton(text="Погода")]
    ],
    resize_keyboard=True
)

# ================== INLINE КНОПКИ ==================
def get_schedule_inline_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Сегодня", callback_data="sch_today"),
            InlineKeyboardButton(text="Завтра", callback_data="sch_tomorrow"),
        ],
        [
            InlineKeyboardButton(text="На неделю", callback_data="sch_week"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="sch_back")
        ]
    ])

# ================== ВСПОМОГАТЕЛЬНЫЕ ==================
def get_unique_schools():
    schools = get_schools_and_years()
    unique = []
    seen = set()

    for item in schools:
        if item["school"] not in seen:
            seen.add(item["school"])
            unique.append(item["school"])

    return unique


def get_day_name_by_date(target_date: datetime):
    days = [
        "Понедельник", "Вторник", "Среда",
        "Четверг", "Пятница", "Суббота", "Воскресенье"
    ]
    return days[target_date.weekday()]


def get_lessons_for_day(schedule, day_name):
    return [lesson for lesson in schedule if lesson["day"] == day_name]


def build_day_schedule_text(group_name, day_name, lessons):
    if not lessons:
        return f"{group_name}\n{day_name}\n\nПар нет 🎉"

    text = f"{group_name}\n{day_name}\n\n"

    for lesson in lessons:
        text += (
            f"⏰ {lesson['time']}\n"
            f"📘 {lesson['subject']}\n"
            f"👤 {lesson['teacher']}\n"
            f"🏫 {lesson['room']}\n\n"
        )

    return text


def build_week_schedule_text(group_name, schedule):
    text = f"{group_name}\n\n"

    for lesson in schedule:
        text += (
            f"{lesson['day']} {lesson['time']}\n"
            f"{lesson['subject']}\n\n"
        )

    return text[:4000]


def get_saved_group_or_none(user_id):
    return get_user_group(user_id)

# ================== START ==================
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Это Student Helper VKTU",
        reply_markup=main_keyboard
    )

# ================== ВЫБОР ГРУППЫ ==================
@dp.message(F.text == "Выбрать группу")
async def choose_group(message: Message):
    schools = get_unique_schools()

    builder = InlineKeyboardBuilder()

    for i, school in enumerate(schools):
        builder.button(text=school, callback_data=f"sch:{i}")

    builder.adjust(1)

    await message.answer("Выбери школу:", reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith("sch:"))
async def school_selected(callback: CallbackQuery):
    user_id = callback.from_user.id
    index = int(callback.data.split(":")[1])

    schools = get_unique_schools()
    school_name = schools[index]

    user_data[user_id] = {"school": school_name}

    data = get_schools_and_years()

    years = [
        item["year"] for item in data
        if item["school"] == school_name and item["count"] != "0"
    ]

    builder = InlineKeyboardBuilder()

    for year in years:
        builder.button(text=year, callback_data=f"year:{year}")

    builder.adjust(2)

    await callback.message.edit_text(
        f"{school_name}\nВыбери год:",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data.startswith("year:"))
async def year_selected(callback: CallbackQuery):
    user_id = callback.from_user.id
    year = callback.data.split(":")[1]

    school = user_data[user_id]["school"]

    data = get_schools_and_years()

    target = next(
        item for item in data
        if item["school"] == school and item["year"] == year
    )

    groups = get_groups_by_url(target["url"])

    user_data[user_id]["groups"] = groups

    builder = InlineKeyboardBuilder()

    for i, g in enumerate(groups):
        builder.button(text=g["group_name"], callback_data=f"grp:{i}")

    builder.adjust(2)

    await callback.message.edit_text(
        f"{school} {year}\nВыбери группу:",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data.startswith("grp:"))
async def group_selected(callback: CallbackQuery):
    user_id = callback.from_user.id
    index = int(callback.data.split(":")[1])

    group = user_data[user_id]["groups"][index]

    save_user_group(user_id, group["group_id"], group["group_name"])

    await callback.message.edit_text(
        f"Сохранено: {group['group_name']}"
    )

# ================== РАСПИСАНИЕ ==================
@dp.message(F.text == "Моё расписание")
async def my_schedule(message: Message):
    user_id = message.from_user.id
    group = get_saved_group_or_none(user_id)

    if not group:
        await message.answer("Сначала выбери группу")
        return

    await message.answer(
        f"{group['group_name']}\n\nВыбери:",
        reply_markup=get_schedule_inline_keyboard()
    )


@dp.callback_query(F.data == "sch_today")
async def today(callback: CallbackQuery):
    group = get_saved_group_or_none(callback.from_user.id)

    today = datetime.now()
    day = get_day_name_by_date(today)

    schedule = get_schedule_by_group_id(group["group_id"])
    lessons = get_lessons_for_day(schedule, day)

    text = build_day_schedule_text(group["group_name"], day, lessons)

    await callback.message.edit_text(text, reply_markup=get_schedule_inline_keyboard())


@dp.callback_query(F.data == "sch_tomorrow")
async def tomorrow(callback: CallbackQuery):
    group = get_saved_group_or_none(callback.from_user.id)

    tomorrow = datetime.now() + timedelta(days=1)
    day = get_day_name_by_date(tomorrow)

    schedule = get_schedule_by_group_id(group["group_id"])
    lessons = get_lessons_for_day(schedule, day)

    text = build_day_schedule_text(group["group_name"], day, lessons)

    await callback.message.edit_text(text, reply_markup=get_schedule_inline_keyboard())


@dp.callback_query(F.data == "sch_week")
async def week(callback: CallbackQuery):
    group = get_saved_group_or_none(callback.from_user.id)

    schedule = get_schedule_by_group_id(group["group_id"])
    text = build_week_schedule_text(group["group_name"], schedule)

    await callback.message.edit_text(text, reply_markup=get_schedule_inline_keyboard())


@dp.callback_query(F.data == "sch_back")
async def back(callback: CallbackQuery):
    await callback.message.edit_text("Главное меню")

# ================== ПОГОДА ==================
def get_weather_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Сейчас", callback_data="w_now"),
            InlineKeyboardButton(text="Сегодня", callback_data="w_today"),
            InlineKeyboardButton(text="Завтра", callback_data="w_tomorrow"),
        ]
    ])


@dp.message(F.text == "Погода")
async def weather_menu(message: Message):
    await message.answer(
        "Выбери:",
        reply_markup=get_weather_keyboard()
    )
    
@dp.callback_query(F.data == "w_now")
async def weather_now(callback: CallbackQuery):
    text = get_weather_now("Oskemen")
    await callback.message.edit_text(text, reply_markup=get_weather_keyboard())


@dp.callback_query(F.data == "w_today")
async def weather_today(callback: CallbackQuery):
    text = get_weather_forecast("Oskemen", days=0)
    await callback.message.edit_text(text, reply_markup=get_weather_keyboard())


@dp.callback_query(F.data == "w_tomorrow")
async def weather_tomorrow(callback: CallbackQuery):
    text = get_weather_forecast("Oskemen", days=1)
    await callback.message.edit_text(text, reply_markup=get_weather_keyboard())

# ================== ЗАПУСК ==================
async def main():
    init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())