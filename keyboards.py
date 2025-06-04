import datetime
from calendar import Calendar
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup


month_names = {1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 5: "Май", 6: "Июнь",
               7: "Июль", 8: "Август", 9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"}


async def make_month_calendar(month=None, year=None):
    today = datetime.date.today()
    calendar = Calendar()
    if month is None:
        month = today.month
    if year is None:
        year = today.year
    dates = calendar.monthdatescalendar(year, month)
    return dates, month, year, today


async def main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text="Добавить платёж"))
    keyboard.add(KeyboardButton(text="Просмотр"))
    keyboard.add(KeyboardButton(text="⚙️"))
    return keyboard


async def payment_company_keyboard(companies):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for company in companies:
        keyboard.add(InlineKeyboardButton(text=company["name"],
                                          callback_data=f"payment_company_{company['company_id']}"))
    keyboard.add(InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def payment_facility_keyboard(facilities):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for facility in facilities:
        keyboard.add(InlineKeyboardButton(text=facility["name"],
                                          callback_data=f"payment_facility_{facility['facility_id']}"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def payment_choice_keyboard():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(InlineKeyboardButton(text="Назначение платежа",
                                      callback_data="payment_purpose"))
    keyboard.add(InlineKeyboardButton(text="Под отчёт",
                                      callback_data="payment_user"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def payment_purpose_type_keyboard(purpose_types):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for purpose_type in purpose_types:
        keyboard.add(InlineKeyboardButton(text=purpose_type["name"],
                                          callback_data=f"payment_purpose_type_{purpose_type['type_id']}"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def payment_purpose_keyboard(purposes):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for purpose in purposes:
        keyboard.add(InlineKeyboardButton(text=purpose["name"],
                                          callback_data=f"payment_purpose_{purpose['purpose_id']}"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def payment_users_keyboard(users):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for user in users:
        keyboard.add(InlineKeyboardButton(text=user["name"],
                                          callback_data=f"payment_user_{user['user_id']}"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def payment_send_keyboard():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(InlineKeyboardButton(text="Отправить без комментария",
                                      callback_data="payment_send_without_comment"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def settings_keyboard():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(InlineKeyboardButton(text="Компании/объекты",
                                      callback_data="settings_companies"))
    keyboard.add(InlineKeyboardButton(text="Назначения",
                                      callback_data="settings_purpose_types"))
    keyboard.add(InlineKeyboardButton(text="Люди",
                                      callback_data="settings_users"))
    keyboard.add(InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def settings_companies_keyboard(companies):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for company in companies:
        if company["status"]:
            company["status"] = "🟢"
        else:
            company["status"] = "🔴"
        keyboard.row(InlineKeyboardButton(text=company["name"],
                                          callback_data="nothing"),
                     InlineKeyboardButton(text="Объекты",
                                          callback_data=f"settings_facilities_in_company_{company['company_id']}"),
                     InlineKeyboardButton(text=company["status"],
                                          callback_data=f"settings_company_change_status_{company['company_id']}"),
                     InlineKeyboardButton(text="🗑️",
                                          callback_data=f"settings_company_delete_{company['company_id']}"))
    keyboard.add(InlineKeyboardButton(text="Добавить Компанию",
                                      callback_data="settings_company_add"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def settings_facilities_keyboard(facilities):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for facility in facilities:
        if facility["status"]:
            facility["status"] = "🟢"
        else:
            facility["status"] = "🔴"
        keyboard.row(InlineKeyboardButton(text=facility["name"],
                                          callback_data="nothing"),
                     InlineKeyboardButton(text=facility["status"],
                                          callback_data=f"settings_facility_change_status_{facility['facility_id']}"),
                     InlineKeyboardButton(text="🗑️",
                                          callback_data=f"settings_facility_delete_{facility['facility_id']}"))
    keyboard.add(InlineKeyboardButton(text="Добавить объект",
                                      callback_data="settings_facility_add"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def settings_purpose_types_keyboard(purpose_types):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for purpose_type in purpose_types:
        if purpose_type["status"]:
            purpose_type["status"] = "🟢"
        else:
            purpose_type["status"] = "🔴"
        keyboard.row(InlineKeyboardButton(text=purpose_type["name"],
                                          callback_data="nothing"),
                     InlineKeyboardButton(text="Назначения",
                                          callback_data=f"settings_purposes_in_purpose_type_{purpose_type['type_id']}"),
                     InlineKeyboardButton(text=purpose_type["status"],
                                          callback_data=f"settings_purpose_type_change_status_{purpose_type['type_id']}"),
                     InlineKeyboardButton(text="🗑️",
                                          callback_data=f"settings_purpose_type_delete_{purpose_type['type_id']}"))
    keyboard.add(InlineKeyboardButton(text="Добавить тип назначения",
                                      callback_data="settings_purpose_type_add"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def settings_purposes_keyboard(purposes):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for purpose in purposes:
        if purpose["status"]:
            purpose["status"] = "🟢"
        else:
            purpose["status"] = "🔴"
        keyboard.row(InlineKeyboardButton(text=purpose["name"],
                                          callback_data="nothing"),
                     InlineKeyboardButton(text=purpose["status"],
                                          callback_data=f"settings_purpose_change_status_{purpose['purpose_id']}"),
                     InlineKeyboardButton(text="🗑️",
                                          callback_data=f"settings_purpose_delete_{purpose['purpose_id']}"))
    keyboard.add(InlineKeyboardButton(text="Добавить назначение",
                                      callback_data="settings_purpose_add"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def settings_users_keyboard(users):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for user in users:
        if user["status"]:
            user["status"] = "🟢"
        else:
            user["status"] = "🔴"
        keyboard.row(InlineKeyboardButton(text=user["name"],
                                          callback_data="nothing"))
        buttons = [InlineKeyboardButton(text=str(user["balance"]),
                                        callback_data="nothing"),
                   InlineKeyboardButton(text="Списать баланс",
                                        callback_data=f"settings_user_clear_balance_{user['user_id']}")]
        if user["secret_key"]:
            buttons.append(InlineKeyboardButton(text="Пароль",
                                                callback_data=f"settings_user_secret_key_{user['user_id']}"))
        buttons.append(InlineKeyboardButton(text="🗑️",
                                            callback_data=f"settings_user_delete_{user['user_id']}"))
        keyboard.row(*buttons)
    keyboard.add(InlineKeyboardButton(text="Добавить нового человека",
                                      callback_data="settings_user_add"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def view_keyboard():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(InlineKeyboardButton(text="Свод - все пункты",
                                      callback_data="view_all"))
    keyboard.add(InlineKeyboardButton(text="Отчёт по компании",
                                      callback_data="view_company"))
    keyboard.add(InlineKeyboardButton(text="Отчёт по объекту",
                                      callback_data="view_facility"))
    keyboard.add(InlineKeyboardButton(text="Отчёт по типу назначения",
                                      callback_data="view_purpose_type"))
    keyboard.add(InlineKeyboardButton(text="Отчёт по назначению",
                                      callback_data="view_purpose"))
    keyboard.add(InlineKeyboardButton(text="Отчёт по подотчётному",
                                      callback_data="view_user"))
    keyboard.add(InlineKeyboardButton(text="Отчёт по автору",
                                      callback_data="view_creator"))
    keyboard.add(InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def view_company_keyboard(companies):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for company in companies:
        keyboard.add(InlineKeyboardButton(text=company["name"],
                                          callback_data=f"view_company_{company['company_id']}"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def view_facility_keyboard(facilities):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for facility in facilities:
        keyboard.add(InlineKeyboardButton(text=facility["name"],
                                          callback_data=f"view_facility_{facility['facility_id']}"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def view_purpose_type_keyboard(purpose_types):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for purpose_type in purpose_types:
        keyboard.add(InlineKeyboardButton(text=purpose_type["name"],
                                          callback_data=f"view_purpose_type_{purpose_type['type_id']}"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def view_purpose_keyboard(purposes):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for purpose in purposes:
        keyboard.add(InlineKeyboardButton(text=purpose["name"],
                                          callback_data=f"view_purpose_{purpose['purpose_id']}"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def view_user_keyboard(users):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for user in users:
        keyboard.add(InlineKeyboardButton(text=user["name"],
                                          callback_data=f"view_user_{user['user_id']}"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def view_creator_keyboard(users):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for user in users:
        keyboard.add(InlineKeyboardButton(text=user["name"],
                                          callback_data=f"view_creator_{user['tg_id']}"))
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def calendar_keyboard(month=None, year=None):
    calendar, month, year, today = await make_month_calendar(month, year)
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text="◀️",
                                      callback_data=f"calendar_year_back_{month}_{year}"),
                 InlineKeyboardButton(text=year,
                                      callback_data="nothing"),
                 InlineKeyboardButton(text="▶️",
                                      callback_data=f"calendar_year_forward_{month}_{year}"))
    keyboard.row(InlineKeyboardButton(text="◀️",
                                      callback_data=f"calendar_month_back_{month}_{year}"),
                 InlineKeyboardButton(text=month_names[month],
                                      callback_data="nothing"),
                 InlineKeyboardButton(text="▶️",
                                      callback_data=f"calendar_month_forward_{month}_{year}"))
    for week in calendar:
        button_list = []
        for day in week:
            if day.month != month:
                button_list.append(InlineKeyboardButton(text=" ",
                                                        callback_data=f"nothing"))
            elif day == today:
                button_list.append(InlineKeyboardButton(text=f"🟢{day.day}",
                                                        callback_data=f"date_{day}"))
            else:
                button_list.append(InlineKeyboardButton(text=str(day.day),
                                                        callback_data=f"date_{day}"))
        keyboard.row(*button_list)
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def yes_no_keyboard():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(InlineKeyboardButton(text="Да",
                                      callback_data="yes"))
    keyboard.add(InlineKeyboardButton(text="Нет",
                                      callback_data="back"))
    return keyboard


async def back_cancel_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text="↩️",
                                      callback_data="back"),
                 InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard


async def back_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="↩️",
                                      callback_data="back"))
    return keyboard


async def cancel_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text="🚫",
                                      callback_data="cancel"))
    return keyboard
