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
    keyboard.add(KeyboardButton(text="Изменить Компании/объекты"))
    # keyboard.add(KeyboardButton(text="Пользователи"))
    keyboard.add(KeyboardButton(text="Просмотр"))
    return keyboard


async def payment_company_keyboard(companies):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for company in companies:
        keyboard.add(InlineKeyboardButton(text=company["name"],
                                          callback_data=f"payment_company_{company['company_id']}"))
    keyboard.row(InlineKeyboardButton(text="↩️", callback_data="back"),
                 InlineKeyboardButton(text="🚫", callback_data="cancel"))
    return keyboard


async def payment_object_keyboard(objects):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for _object in objects:
        keyboard.add(InlineKeyboardButton(text=_object["name"], callback_data=f"payment_object_{_object['object_id']}"))
    keyboard.row(InlineKeyboardButton(text="↩️", callback_data="back"),
                 InlineKeyboardButton(text="🚫", callback_data="cancel"))
    return keyboard


async def payment_choice_keyboard():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(InlineKeyboardButton(text="Назначение платежа", callback_data="payment_spent_for"))
    keyboard.add(InlineKeyboardButton(text="Под отчёт", callback_data="payment_user_name"))
    keyboard.row(InlineKeyboardButton(text="↩️", callback_data="back"),
                 InlineKeyboardButton(text="🚫", callback_data="cancel"))
    return keyboard


async def payment_users_keyboard(users, page):
    pages = len(users) // 10
    if len(users) % 10 != 0:
        pages += 1
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for i in range(page * 10 - 10, page * 10):
        if i == len(users):
            break
        keyboard.add(InlineKeyboardButton(text=users[i]["name"], callback_data=f"payment_user_name_{users[i]['name']}"))
    if len(users) > 10:
        keyboard.row(InlineKeyboardButton(text="◀️",
                                          callback_data="payment_user_page_back"),
                     InlineKeyboardButton(text=f"{page} / {pages}",
                                          callback_data="nothing"),
                     InlineKeyboardButton(text="▶️",
                                          callback_data="payment_user_page_forward"))
    keyboard.row(InlineKeyboardButton(text="↩️", callback_data="back"),
                 InlineKeyboardButton(text="🚫", callback_data="cancel"))
    return keyboard


async def payment_send_keyboard():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(InlineKeyboardButton(text="Отправить без комментария", callback_data="payment_send_without_comment"))
    keyboard.row(InlineKeyboardButton(text="↩️", callback_data="back"),
                 InlineKeyboardButton(text="🚫", callback_data="cancel"))
    return keyboard


async def change_companies_keyboard(companies):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for company in companies:
        if company["status"]:
            company["status"] = "🟢"
        else:
            company["status"] = "🔴"
        keyboard.row(InlineKeyboardButton(text=company["name"],
                                          callback_data=f"company_change_name_{company['company_id']}"),
                     InlineKeyboardButton(text="Объекты",
                                          callback_data=f"objects_in_company_{company['company_id']}"),
                     InlineKeyboardButton(text=company["status"],
                                          callback_data=f"company_change_status_{company['company_id']}"),
                     InlineKeyboardButton(text="🗑️",
                                          callback_data=f"company_delete_{company['company_id']}"))
    keyboard.add(InlineKeyboardButton(text="Добавить Компанию", callback_data="company_add"))
    keyboard.add(InlineKeyboardButton(text="🚫", callback_data="cancel"))
    return keyboard


async def change_objects_keyboard(objects):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for object in objects:
        if object["status"]:
            object["status"] = "🟢"
        else:
            object["status"] = "🔴"
        keyboard.row(InlineKeyboardButton(text=object["name"],
                                          callback_data=f"object_change_name_{object['object_id']}"),
                     InlineKeyboardButton(text=object["status"],
                                          callback_data=f"object_change_status_{object['object_id']}"),
                     InlineKeyboardButton(text="🗑️",
                                          callback_data=f"object_delete_{object['object_id']}"))
    keyboard.add(InlineKeyboardButton(text="Добавить объект", callback_data="object_add"))
    keyboard.row(InlineKeyboardButton(text="↩️", callback_data="back"),
                 InlineKeyboardButton(text="🚫", callback_data="cancel"))
    return keyboard


async def view_keyboard():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(InlineKeyboardButton(text="Общий отчёт", callback_data="view_all"))
    keyboard.add(InlineKeyboardButton(text="Выбрать Компанию", callback_data="view_companies"))
    keyboard.add(InlineKeyboardButton(text="Выбрать человека", callback_data="view_users"))
    keyboard.add(InlineKeyboardButton(text="🚫", callback_data="cancel"))
    return keyboard


async def view_companies_keyboard(companies):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for company in companies:
        keyboard.row(InlineKeyboardButton(text=company["name"], callback_data=f"view_company_{company['company_id']}"),
                     InlineKeyboardButton(text="Объекты", callback_data=f"view_objects_{company['company_id']}"))
    keyboard.row(InlineKeyboardButton(text="↩️", callback_data="back"),
                 InlineKeyboardButton(text="🚫", callback_data="cancel"))
    return keyboard


async def view_objects_keyboard(objects):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for object in objects:
        keyboard.add(InlineKeyboardButton(text=object["name"], callback_data=f"view_object_{object['object_id']}"))
    keyboard.row(InlineKeyboardButton(text="↩️", callback_data="back"),
                 InlineKeyboardButton(text="🚫", callback_data="cancel"))
    return keyboard


async def payment_date_keyboard(month=None, year=None):
    calendar, month, year, today = await make_month_calendar(month, year)
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text="◀️",
                                      callback_data=f"payment_year_back_{month}_{year}"),
                 InlineKeyboardButton(text=year,
                                      callback_data="nothing"),
                 InlineKeyboardButton(text="▶️",
                                      callback_data=f"payment_year_forward_{month}_{year}"))
    keyboard.row(InlineKeyboardButton(text="◀️",
                                      callback_data=f"payment_month_back_{month}_{year}"),
                 InlineKeyboardButton(text=month_names[month],
                                      callback_data="nothing"),
                 InlineKeyboardButton(text="▶️",
                                      callback_data=f"payment_month_forward_{month}_{year}"))
    for week in calendar:
        button_list = []
        for day in week:
            if day.month != month:
                button_list.append(InlineKeyboardButton(text=" ",
                                                        callback_data=f"nothing"))
            elif day == today:
                button_list.append(InlineKeyboardButton(text=f"🟢{day.day}",
                                                        callback_data=f"payment_date_{day}"))
            else:
                button_list.append(InlineKeyboardButton(text=str(day.day),
                                                        callback_data=f"payment_date_{day}"))
        keyboard.row(*button_list)
    keyboard.row(InlineKeyboardButton(text="↩️", callback_data="back"),
                 InlineKeyboardButton(text="🚫", callback_data="cancel"))
    return keyboard


async def purpose_type_keyboard(purpose_types):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for purpose_type in purpose_types:
        keyboard.add(InlineKeyboardButton(text=purpose_type["type"], callback_data=f"payment_purpose_type_{purpose_type['type']}"))
    keyboard.row(InlineKeyboardButton(text="↩️", callback_data="back"),
                 InlineKeyboardButton(text="🚫", callback_data="cancel"))
    return keyboard


async def purpose_keyboard(purposes):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for purpose in purposes:
        keyboard.add(InlineKeyboardButton(text=purpose["name"], callback_data=f"payment_purpose_{purpose['id']}"))
    keyboard.row(InlineKeyboardButton(text="↩️", callback_data="back"),
                 InlineKeyboardButton(text="🚫", callback_data="cancel"))
    return keyboard


async def yes_no_keyboard():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(InlineKeyboardButton(text="Да", callback_data="yes"))
    keyboard.add(InlineKeyboardButton(text="Нет", callback_data="back"))
    return keyboard


async def back_cancel_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text="↩️", callback_data="back"),
                 InlineKeyboardButton(text="🚫", callback_data="cancel"))
    return keyboard


async def back_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="↩️", callback_data="back"))
    return keyboard


async def cancel_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text="🚫", callback_data="cancel"))
    return keyboard
