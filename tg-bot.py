from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
import asyncio
import sqlite3
import datetime
from database import init_db
import logging

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from vfs_parser.monitoring import monitoring

BOT_TOKEN = ''

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class Registration(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_gender = State()
    waiting_for_passport = State()
    waiting_for_passport_date = State()
    waiting_for_email = State()
    waiting_for_phone = State()


# --- Категории и подкатегории визы ---
VISA_CATEGORIES = {
    "C": {
        "name": "Краткосрочная (C)",
        "subcategories": {
            "C01": "Туризм",
            "C02": "Деловая",
            "C03": "Гостевая",
            "C04": "Транзит",
            "C05": "Лечение",
            "C06": "Учёба",
            "C07": "Спорт",
            "C08": "Культура",
            "C09": "Официальная",
            "C10": "Водитель",
            "C11": "Член семьи гражданина ЕС",
            "C12": "Другое"
        }
    },
    "D": {
        "name": "Долгосрочная (D)",
        "subcategories": {
            "D01": "Работа",
            "D02": "Учёба",
            "D03": "Воссоединение семьи",
            "D04": "Бизнес",
            "D05": "Другое"
        }
    },
    "A": {
        "name": "Аэропортовая (A)",
        "subcategories": {
            "A01": "Транзит через аэропорт"
        }
    },
    "B": {
        "name": "Транзитная (B)",
        "subcategories": {
            "B01": "Транзит"
        }
    },
    "LTV": {
        "name": "LTV (ограниченная территория действия)",
        "subcategories": {
            "LTV01": "Гуманитарная",
            "LTV02": "Другое"
        }
    }
}

CITIES = [
    ("minsk", "Минск"),
    ("brest", "Брест"),
    ("grodno", "Гродно"),
    ("vitebsk", "Витебск"),
    ("gomel", "Гомель"),
    ("mogilev", "Могилёв")
]

active_monitorings = {}
monitoring_flags = {}


class SettingsFSM(StatesGroup):
    waiting_for_city = State()
    waiting_for_category = State()
    waiting_for_subcategory = State()


def main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📝 Регистрация", callback_data="register"),
        InlineKeyboardButton(text="🔍 Верификация", callback_data="verify")
    )
    builder.row(
        InlineKeyboardButton(text="⚙ Настройки", callback_data="settings"),
        InlineKeyboardButton(text="🎯 Начать поиск", callback_data="monitoring")
    )
    return builder.as_markup()


def back_button():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅ Назад", callback_data="back"))
    return builder.as_markup()


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def log_active_user(user_id, username):
    import sqlite3
    import datetime
    now = datetime.datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    hour = int(now.strftime('%H'))
    with sqlite3.connect('database.db') as conn:
        # Проверяем, был ли уже лог за этот час для этого пользователя
        exists = conn.execute(
            "SELECT 1 FROM bookings WHERE user_id=? AND date=? AND hour=?",
            (user_id, date_str, hour)
        ).fetchone()
        if not exists:
            conn.execute(
                '''INSERT INTO bookings (user_id, username, attempts, successful, booking_time, hour, date)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (user_id, username, 1, 0, now.isoformat(), hour, date_str)
            )
            conn.commit()


def log_error(error_message):
    now = datetime.datetime.now()
    with sqlite3.connect('database.db') as conn:
        conn.execute(
            'UPDATE metrics SET errors = errors + 1, last_updated = ? WHERE id = (SELECT id FROM metrics ORDER BY last_updated DESC LIMIT 1)',
            (now.isoformat(),)
        )
        conn.commit()
    logger.error(f"Ошибка: {error_message}")


@dp.message(CommandStart())
async def start(message: types.Message):
    log_active_user(message.from_user.id, message.from_user.username)
    logger.info(f"/start от пользователя {message.from_user.id} (@{message.from_user.username})")
    # handle_start(message.from_user.id, f"@{message.from_user.username}")  # Запись пользователя в базу данных
    await message.answer("🤖 VFS Booking Bot", reply_markup=main_menu())


@dp.callback_query(F.data == "back")
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    log_active_user(callback.from_user.id, callback.from_user.username)
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Назад'")
    await state.clear()
    await callback.message.edit_text("🤖 VFS Booking Bot", reply_markup=main_menu())
    await callback.answer()


@dp.callback_query(F.data == "register")
async def register_start(callback: types.CallbackQuery, state: FSMContext):
    log_active_user(callback.from_user.id, callback.from_user.username)
    logger.info(f"Пользователь {callback.from_user.id} начал регистрацию")
    await callback.message.edit_text(
        "Введите ваше имя и фамилию (как в паспорте):"
    )
    await callback.answer()
    await state.set_state(Registration.waiting_for_fullname)


@dp.message(Registration.waiting_for_fullname)
async def reg_fullname(message: types.Message, state: FSMContext):
    log_active_user(message.from_user.id, message.from_user.username)
    logger.info(f"Пользователь {message.from_user.id} ввёл ФИО: {message.text.strip()}")
    await state.update_data(fullname=message.text.strip())
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Мужской", callback_data="gender_male"),
        InlineKeyboardButton(text="Женский", callback_data="gender_female")
    )
    await message.answer("Выберите пол:", reply_markup=builder.as_markup())
    await state.set_state(Registration.waiting_for_gender)


@dp.callback_query(F.data.startswith("gender_"), Registration.waiting_for_gender)
async def reg_gender(callback: types.CallbackQuery, state: FSMContext):
    log_active_user(callback.from_user.id, callback.from_user.username)
    gender = callback.data.split("_")[1]
    logger.info(f"Пользователь {callback.from_user.id} выбрал пол: {gender}")
    await state.update_data(gender=gender)
    await callback.message.edit_text("Введите номер паспорта:")
    await state.set_state(Registration.waiting_for_passport)
    await callback.answer()


@dp.message(Registration.waiting_for_passport)
async def reg_passport(message: types.Message, state: FSMContext):
    log_active_user(message.from_user.id, message.from_user.username)
    logger.info(f"Пользователь {message.from_user.id} ввёл паспорт: {message.text.strip()}")
    await state.update_data(passport=message.text.strip())
    await message.answer("Введите дату выдачи паспорта (ДД.ММ.ГГГГ):")
    await state.set_state(Registration.waiting_for_passport_date)


@dp.message(Registration.waiting_for_passport_date)
async def reg_passport_date(message: types.Message, state: FSMContext):
    log_active_user(message.from_user.id, message.from_user.username)
    logger.info(f"Пользователь {message.from_user.id} ввёл дату выдачи паспорта: {message.text.strip()}")
    await state.update_data(passport_date=message.text.strip())
    await message.answer("Введите вашу электронную почту:")
    await state.set_state(Registration.waiting_for_email)


@dp.message(Registration.waiting_for_email)
async def reg_email(message: types.Message, state: FSMContext):
    log_active_user(message.from_user.id, message.from_user.username)
    logger.info(f"Пользователь {message.from_user.id} ввёл email: {message.text.strip()}")
    await state.update_data(email=message.text.strip())
    await message.answer("Введите номер телефона полностью:")
    await state.set_state(Registration.waiting_for_phone)


@dp.message(Registration.waiting_for_phone)
async def reg_phone(message: types.Message, state: FSMContext):
    log_active_user(message.from_user.id, message.from_user.username)
    logger.info(f"Пользователь {message.from_user.id} ввёл телефон: {message.text.strip()}")
    await state.update_data(phone=message.text.strip())
    data = await state.get_data()
    logger.info(f"Регистрация завершена для пользователя {message.from_user.id}: {data}")
    # Здесь можно сохранить данные в базу, если нужно
    await message.answer("Спасибо! Ваши данные сохранены.\nВозвращаемся в меню:", reply_markup=main_menu())
    await state.clear()


@dp.callback_query(F.data == "verify")
async def verify_start(callback: types.CallbackQuery):
    log_active_user(callback.from_user.id, callback.from_user.username)
    logger.info(f"Пользователь {callback.from_user.id} выбрал верификацию")
    await callback.message.edit_text(
        "Для верификации перейдите по ссылке и выполните камеру-тест + биометрию:\nhttps://msivfs.com",
        reply_markup=back_button()
    )
    await callback.answer()


@dp.callback_query(F.data == "settings")
async def settings_start(callback: types.CallbackQuery, state: FSMContext):
    log_active_user(callback.from_user.id, callback.from_user.username)
    logger.info(f"Пользователь {callback.from_user.id} открыл настройки")
    builder = InlineKeyboardBuilder()
    for city_code, city_name in CITIES:
        builder.row(InlineKeyboardButton(text=city_name, callback_data=f"city_{city_code}"))
    builder.row(InlineKeyboardButton(text="⬅ Назад", callback_data="back"))
    await callback.message.edit_text(
        "Выберите город подачи заявления:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(SettingsFSM.waiting_for_city)
    await callback.answer()


@dp.callback_query(F.data.startswith("city_"), SettingsFSM.waiting_for_city)
async def choose_city(callback: types.CallbackQuery, state: FSMContext):
    log_active_user(callback.from_user.id, callback.from_user.username)
    city_code = callback.data.split("_", 1)[1]
    logger.info(f"Пользователь {callback.from_user.id} выбрал город: {city_code}")
    await state.update_data(city=city_code)
    builder = InlineKeyboardBuilder()
    for cat_code, cat in VISA_CATEGORIES.items():
        builder.row(InlineKeyboardButton(text=cat['name'], callback_data=f"cat_{cat_code}"))
    builder.row(InlineKeyboardButton(text="⬅ Назад", callback_data="back"))
    await callback.message.edit_text(
        "Выберите категорию визы:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(SettingsFSM.waiting_for_category)
    await callback.answer()


@dp.callback_query(F.data.startswith("cat_"), SettingsFSM.waiting_for_category)
async def choose_category(callback: types.CallbackQuery, state: FSMContext):
    log_active_user(callback.from_user.id, callback.from_user.username)
    cat_code = callback.data.split("_", 1)[1]
    logger.info(f"Пользователь {callback.from_user.id} выбрал категорию визы: {cat_code}")
    await state.update_data(category=cat_code)
    builder = InlineKeyboardBuilder()
    for sub_code, sub_name in VISA_CATEGORIES[cat_code]["subcategories"].items():
        builder.row(InlineKeyboardButton(text=f"{sub_name} ({sub_code})", callback_data=f"sub_{sub_code}"))
    builder.row(InlineKeyboardButton(text="⬅ Назад", callback_data="back"))
    await callback.message.edit_text(
        "Выберите подкатегорию визы:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(SettingsFSM.waiting_for_subcategory)
    await callback.answer()


@dp.callback_query(F.data.startswith("sub_"), SettingsFSM.waiting_for_subcategory)
async def choose_subcategory(callback: types.CallbackQuery, state: FSMContext):
    log_active_user(callback.from_user.id, callback.from_user.username)
    sub_code = callback.data.split("_", 1)[1]
    logger.info(f"Пользователь {callback.from_user.id} выбрал подкатегорию визы: {sub_code}")
    await state.update_data(subcategory=sub_code)
    data = await state.get_data()
    logger.info(f"Настройки сохранены для пользователя {callback.from_user.id}: {data}")
    await callback.message.edit_text(
        f"Настройки сохранены:\n"
        f"Город: {next(name for code, name in CITIES if code == data['city'])}\n"
        f"Категория: {VISA_CATEGORIES[data['category']]['name']} ({data['category']})\n"
        f"Подкатегория: {VISA_CATEGORIES[data['category']]['subcategories'][data['subcategory']]} ({data['subcategory']})\n",
        reply_markup=main_menu()
    )
    await state.clear()
    await callback.answer()


@dp.callback_query(F.data == "monitoring")
async def monitoring_start(callback: types.CallbackQuery):
    log_active_user(callback.from_user.id, callback.from_user.username)
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} начал мониторинг слотов")

    update_metrics(slots=1, users=1)
    update_status('Worker', 'ONLINE')

    await callback.message.edit_text(
        "Поиск слотов запущен 24/7. Вы будете получать уведомления.",
        reply_markup=back_button()
    )
    await callback.answer()

    if active_monitorings.get(user_id):
        return

    monitoring_flags[user_id] = True

    async def background_monitoring():
        while monitoring_flags.get(user_id, False):
            logger.info(f"[Пользователь {user_id}] Запускаю monitoring...")
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, monitoring)  # синхронная функция в потоке
            except Exception as e:
                logger.error(f"[Пользователь {user_id}] Ошибка при выполнении monitoring(): {e}")

            logger.info(f"[Пользователь {user_id}] Жду 7 минут...")
            await asyncio.sleep(420)

    task = asyncio.create_task(background_monitoring())
    active_monitorings[user_id] = task


def update_metrics(slots=0, users=0, success=0, errors=0):
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
            INSERT INTO metrics (slots_checked, active_users, successful_records, errors, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (slots, users, success, errors, datetime.datetime.now().isoformat()))
        conn.commit()


def update_status(component, status):
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
            INSERT OR REPLACE INTO system_status (component, status, last_updated)
            VALUES (?, ?, ?)
        ''', (component, status, datetime.datetime.now().isoformat()))
        conn.commit()


# def handle_start(user_id, username):
#     conn = sqlite3.connect('database.db')
#     now = datetime.datetime.now().isoformat()
#     # Пример: добавляем пользователя как активного
#     conn.execute('''
#         INSERT INTO bookings (user_id, username, attempts, successful, booking_time, hour, date)
#         VALUES (?, ?, ?, ?, ?, ?, ?)
#     ''', (user_id, username, 1, 1, now, now[11:13], now[:10]))
#     conn.commit()
#     conn.close()

async def main():
    # Initialize database
    init_db()
    # Set initial system status
    update_status('API', 'ONLINE')
    update_status('DB', 'ONLINE')
    update_status('Worker', 'ONLINE')
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(main())
