import os
from misk import *
from keyboards import *


@dp.message_handler(commands=["start"], state="*")
async def command_start(message: types.Message, state: FSMContext):
    await delete_last_message(message.chat.id)

    text = "Здравствуйте!"
    keyboard = await main_keyboard()
    await send_message(message.from_user.id, text, keyboard)

    await state.finish()


@dp.message_handler(text="Добавить платёж", state="*")
async def insert_document(message: types.Message, state: FSMContext):
    companies = await get_companies_by_status("active")

    text = "⬇️ Выберите Компанию ⬇️"
    keyboard = await payment_company_keyboard(companies)
    await send_last_message(message.from_user.id, text, keyboard)

    await state.finish()
    await state.set_state(Status.payment_company)


@dp.message_handler(text="Просмотр", state="*")
async def view_payments(message: types.Message, state: FSMContext):
    text = "⬇️ Выберите пункт меню ⬇️"
    keyboard = await view_keyboard()
    await send_last_message(message.from_user.id, text, keyboard)

    await state.finish()
    await state.set_state(Status.view_all)


@dp.message_handler(text="⚙️", state="*")
async def change_companies(message: types.Message, state: FSMContext):
    text = "⬇️ Выберите пункт меню ⬇️"
    keyboard = await settings_keyboard()
    await send_last_message(message.from_user.id, text, keyboard)

    await state.finish()
    await state.set_state(Status.settings)


####################################################################


@dp.callback_query_handler(text_startswith="payment_company_", state=Status.payment_company)
async def but_payment_company_payment_company_(callback_query: types.CallbackQuery, state: FSMContext):
    company_id = callback_query.data.replace("payment_company_", "")
    facilities = await get_facilities_by_status("active", company_id)

    text = "⬇️ Выберите объект ⬇️"
    keyboard = await payment_facility_keyboard(facilities)

    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(company_id=company_id)
    await state.set_state(Status.payment_facility)


@dp.callback_query_handler(text_startswith="payment_facility_", state=Status.payment_facility)
async def but_payment_facility_payment_facility_(callback_query: types.CallbackQuery, state: FSMContext):
    facility_id = callback_query.data.replace("payment_facility_", "")

    text = "Введите сумму"
    keyboard = await back_cancel_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(facility_id=facility_id)
    await state.set_state(Status.payment_amount)


@dp.message_handler(state=Status.payment_amount)
async def status_payment_amount(message: types.Message, state: FSMContext):
    message.text = message.text.replace(",", ".")
    try:
        float(message.text)
    except Exception as e:
        logging.error(f"status_payment_amount {message.from_user.id} {message.text}", exc_info=True)
        text = "Не могу прочитать значение\nВведите сумму цифрами\nКопейки через точку"
        keyboard = await back_cancel_keyboard()
        await send_last_message(message.from_user.id, text, keyboard)
        return

    text = "⬇️ Выберите дату ⬇️"
    keyboard = await calendar_keyboard()
    await send_last_message(message.from_user.id, text, keyboard)

    await state.update_data(amount=message.text)
    await state.set_state(Status.payment_date)


@dp.callback_query_handler(text_startswith="date_", state=Status.payment_date)
async def but_date_date_(callback_query: types.CallbackQuery, state: FSMContext):
    date = callback_query.data.replace("date_", "")

    text = "⬇️ Выберите пункт меню ⬇️"
    keyboard = await payment_choice_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(date=date)
    await state.set_state(Status.payment_choice)


@dp.callback_query_handler(text="payment_purpose", state=Status.payment_choice)
async def but_payment_spent_for(callback_query: types.CallbackQuery, state: FSMContext):
    purpose_types = await get_purpose_types_by_status(True)

    text = "⬇️ Выберите назначение ⬇️"
    keyboard = await payment_purpose_type_keyboard(purpose_types)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.payment_purpose_type)


@dp.callback_query_handler(text_startswith="payment_purpose_type_", state=Status.payment_purpose_type)
async def but_payment_spent_r(callback_query: types.CallbackQuery, state: FSMContext):
    type_id = callback_query.data.replace("payment_purpose_type_", "")
    purposes = await get_purposes_by_status(True, type_id)

    text = "⬇️ Выберите назначение ⬇️"
    keyboard = await payment_purpose_keyboard(purposes)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(type_id=type_id)
    await state.set_state(Status.payment_purpose)


@dp.callback_query_handler(text_startswith="payment_purpose_", state=Status.payment_purpose)
async def but_payment_purpose_(callback_query: types.CallbackQuery, state: FSMContext):
    purpose_id = callback_query.data.replace("payment_purpose_", "")

    text = "Введите комментарий"
    keyboard = await payment_send_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(purpose_id=purpose_id)
    await state.set_state(Status.payment_comment)


@dp.callback_query_handler(text="payment_user", state=Status.payment_choice)
async def but_payment_spent_for(callback_query: types.CallbackQuery, state: FSMContext):
    users = await get_users_by_status(True)

    text = "⬇️ Выберите пользователя из списка ⬇️\nИли введите текстом новое фио"
    keyboard = await payment_users_keyboard(users)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.payment_user_name)


@dp.callback_query_handler(text_startswith="payment_user_", state=Status.payment_user_name)
async def but_payment_user_page_forward(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.data.replace("payment_user_", "")

    text = "Введите комментарий"
    keyboard = await payment_send_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(user_id=user_id)
    await state.set_state(Status.payment_comment)


@dp.message_handler(state=Status.payment_user_name)
async def status_payment_spent_for(message: types.Message, state: FSMContext):
    user_name = message.text
    if await get_user_by_user_name(user_name):
        page = (await state.get_data())["user_page"]
        users = await get_users_by_status(True)

        text = "! Такое фио уже существует !\n⬇️ Выберите пользователя из списка ⬇️\nИли введите текстом новое фио"
        keyboard = await payment_users_keyboard(users, page)
        await send_last_message(message.from_user.id, text, keyboard)
    else:
        text = "Введите комментарий"
        keyboard = await payment_send_keyboard()
        await send_last_message(message.from_user.id, text, keyboard)

        await state.update_data(user_name=message.text)
        await state.set_state(Status.payment_comment)


@dp.message_handler(state=Status.payment_comment)
async def status_payment_date(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data["comment"] = message.text

    await send_payment_to_user(data, message.from_user.id)

    await state.finish()


@dp.callback_query_handler(text="payment_send_without_comment", state=Status.payment_comment)
async def but_payment_send_without_comment(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await send_payment_to_user(data, callback_query.from_user.id)

    await state.finish()


####################################################################


@dp.callback_query_handler(text="settings_companies", state=Status.settings)
async def change_companies(message: types.Message, state: FSMContext):
    companies = await get_companies_by_status("all")

    text = "⬇️ Выберите Компанию ⬇️"
    keyboard = await settings_companies_keyboard(companies)
    await send_last_message(message.from_user.id, text, keyboard)

    await state.set_state(Status.settings_companies)


@dp.callback_query_handler(text_startswith="settings_company_change_status_", state=Status.settings_companies)
async def but_company_change_status_(callback_query: types.CallbackQuery, state: FSMContext):
    company_id = callback_query.data.replace("settings_company_change_status_", "")
    await update_company_status(company_id)
    companies = await get_companies_by_status("all")

    text = "⬇️ Выберите Компанию ⬇️"
    keyboard = await settings_companies_keyboard(companies)
    await send_last_message(callback_query.from_user.id, text, keyboard)


@dp.callback_query_handler(text_startswith="settings_company_delete_", state=Status.settings_companies)
async def but_company_delete_(callback_query: types.CallbackQuery, state: FSMContext):
    company_id = callback_query.data.replace("settings_company_delete_", "")

    text = "Вы уверены?"
    keyboard = await yes_no_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(company_id=company_id)
    await state.set_state(Status.settings_company_delete)


@dp.callback_query_handler(text="settings_company_add", state=Status.settings_companies)
async def but_company_add(callback_query: types.CallbackQuery, state: FSMContext):
    text = "Введите название"
    keyboard = await back_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.settings_company_add)


@dp.message_handler(state=Status.settings_company_add)
async def status_company_add(message: types.Message, state: FSMContext):
    name = message.text
    if await get_company_by_name(name):
        text = "! Такая компания уже существует !\nВведите новое название"
        keyboard = await back_keyboard()
        await send_last_message(message.from_user.id, text, keyboard)
    else:
        await insert_company(name)
        companies = await get_companies_by_status("all")

        text = "⬇️ Выберите Компанию ⬇️"
        keyboard = await settings_companies_keyboard(companies)
        await send_last_message(message.from_user.id, text, keyboard)

        await state.set_state(Status.settings_companies)


####################################################################


@dp.callback_query_handler(text_startswith="settings_facilities_in_company_", state=Status.settings_companies)
async def but_facilities_in_company_(callback_query: types.CallbackQuery, state: FSMContext):
    company_id = callback_query.data.replace("settings_facilities_in_company_", "")
    facilities = await get_facilities_by_status("all", company_id)

    text = "⬇️ Выберите объект ⬇️"
    keyboard = await settings_facilities_keyboard(facilities)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(company_id=company_id)
    await state.set_state(Status.settings_facilities)


@dp.callback_query_handler(text_startswith="settings_facility_change_status_", state=Status.settings_facilities)
async def but_facility_change_status_(callback_query: types.CallbackQuery, state: FSMContext):
    company_id = (await state.get_data())["company_id"]
    facilities_id = callback_query.data.replace("settings_facility_change_status_", "")
    await update_facility_status(facilities_id)
    facilities = await get_facilities_by_status("all", company_id)

    text = "⬇️ Выберите объект ⬇️"
    keyboard = await settings_facilities_keyboard(facilities)
    await send_last_message(callback_query.from_user.id, text, keyboard)


@dp.callback_query_handler(text_startswith="settings_facility_delete_", state=Status.settings_facilities)
async def but_facility_delete_(callback_query: types.CallbackQuery, state: FSMContext):
    facility_id = callback_query.data.replace("settings_facility_delete_", "")

    text = "Вы уверены?"
    keyboard = await yes_no_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(facility_id=facility_id)
    await state.set_state(Status.settings_facility_delete)


@dp.callback_query_handler(text="settings_facility_add", state=Status.settings_facilities)
async def but_facility_add(callback_query: types.CallbackQuery, state: FSMContext):
    text = "Введите название"
    keyboard = await back_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.settings_facility_add)


@dp.message_handler(state=Status.settings_facility_add)
async def status_facility_add(message: types.Message, state: FSMContext):
    company_id = (await state.get_data())["company_id"]
    name = message.text
    if await get_facility_by_name(name, company_id):
        text = "! Такой объект уже существует !\nВведите новое название"
        keyboard = await back_keyboard()
        await send_last_message(message.from_user.id, text, keyboard)
    else:
        await insert_facility(name, company_id)
        facilities = await get_facilities_by_status("all", company_id)

        text = "⬇️ Выберите объект ⬇️"
        keyboard = await settings_facilities_keyboard(facilities)
        await send_last_message(message.from_user.id, text, keyboard)

        await state.set_state(Status.settings_facilities)


####################################################################


@dp.callback_query_handler(text="settings_purpose_types", state=Status.settings)
async def change_companies(message: types.Message, state: FSMContext):
    purpose_types = await get_purpose_types_by_status("all")

    text = "⬇️ Выберите тип назначения ⬇️"
    keyboard = await settings_purpose_types_keyboard(purpose_types)
    await send_last_message(message.from_user.id, text, keyboard)

    await state.set_state(Status.settings_purpose_types)


@dp.callback_query_handler(text_startswith="settings_purpose_type_change_status_", state=Status.settings_purpose_types)
async def but_company_change_status_(callback_query: types.CallbackQuery, state: FSMContext):
    type_id = callback_query.data.replace("settings_purpose_type_change_status_", "")
    await update_purpose_type_status(type_id)
    purpose_types = await get_purpose_types_by_status("all")

    text = "⬇️ Выберите тип назначения ⬇️"
    keyboard = await settings_purpose_types_keyboard(purpose_types)
    await send_last_message(callback_query.from_user.id, text, keyboard)


@dp.callback_query_handler(text_startswith="settings_purpose_type_delete_", state=Status.settings_purpose_types)
async def but_company_delete_(callback_query: types.CallbackQuery, state: FSMContext):
    type_id = callback_query.data.replace("settings_purpose_type_delete_", "")

    text = "Вы уверены?"
    keyboard = await yes_no_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(type_id=type_id)
    await state.set_state(Status.settings_purpose_type_delete)


@dp.callback_query_handler(text="settings_purpose_type_add", state=Status.settings_purpose_types)
async def but_company_add(callback_query: types.CallbackQuery, state: FSMContext):
    text = "Введите название"
    keyboard = await back_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.settings_purpose_type_add)


@dp.message_handler(state=Status.settings_purpose_type_add)
async def status_company_add(message: types.Message, state: FSMContext):
    name = message.text
    if await get_purpose_type_by_name(name):
        text = "! Такая тип назначения уже существует !\nВведите новое название"
        keyboard = await back_keyboard()
        await send_last_message(message.from_user.id, text, keyboard)
    else:
        await insert_purpose_type(name)
        purpose_types = await get_purpose_types_by_status("all")

        text = "⬇️ Выберите тип назначения ⬇️"
        keyboard = await settings_purpose_types_keyboard(purpose_types)
        await send_last_message(message.from_user.id, text, keyboard)

        await state.set_state(Status.settings_purpose_types)


####################################################################


@dp.callback_query_handler(text_startswith="settings_purposes_in_purpose_type_", state=Status.settings_purpose_types)
async def but_facilities_in_company_(callback_query: types.CallbackQuery, state: FSMContext):
    type_id = callback_query.data.replace("settings_purposes_in_purpose_type_", "")
    purposes = await get_purposes_by_status("all", type_id)

    text = "⬇️ Выберите назначение ⬇️"
    keyboard = await settings_purposes_keyboard(purposes)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(type_id=type_id)
    await state.set_state(Status.settings_purposes)


@dp.callback_query_handler(text_startswith="settings_purpose_change_status_", state=Status.settings_purposes)
async def but_facility_change_status_(callback_query: types.CallbackQuery, state: FSMContext):
    type_id = (await state.get_data())["type_id"]
    purpose_id = callback_query.data.replace("settings_purpose_change_status_", "")
    await update_purpose_status(purpose_id)
    purposes = await get_purposes_by_status("all", type_id)

    text = "⬇️ Выберите назначение ⬇️"
    keyboard = await settings_purposes_keyboard(purposes)
    await send_last_message(callback_query.from_user.id, text, keyboard)


@dp.callback_query_handler(text_startswith="settings_purpose_delete_", state=Status.settings_purposes)
async def but_facility_delete_(callback_query: types.CallbackQuery, state: FSMContext):
    purpose_id = callback_query.data.replace("settings_purpose_delete_", "")

    text = "Вы уверены?"
    keyboard = await yes_no_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(purpose_id=purpose_id)
    await state.set_state(Status.settings_purpose_delete)


@dp.callback_query_handler(text="settings_purpose_add", state=Status.settings_purposes)
async def but_facility_add(callback_query: types.CallbackQuery, state: FSMContext):
    text = "Введите название"
    keyboard = await back_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.settings_purpose_add)


@dp.message_handler(state=Status.settings_purpose_add)
async def status_facility_add(message: types.Message, state: FSMContext):
    type_id = (await state.get_data())["type_id"]
    name = message.text
    if await get_purpose_by_name(name, type_id):
        text = "! Такое назначение уже существует !\nВведите новое название"
        keyboard = await back_keyboard()
        await send_last_message(message.from_user.id, text, keyboard)
    else:
        await insert_purpose(name, type_id)
        purposes = await get_purposes_by_status("all", type_id)

        text = "⬇️ Выберите назначение ⬇️"
        keyboard = await settings_purposes_keyboard(purposes)
        await send_last_message(message.from_user.id, text, keyboard)

        await state.set_state(Status.settings_purposes)


####################################################################


@dp.callback_query_handler(text="settings_users", state=Status.settings)
async def but_facility_add(callback_query: types.CallbackQuery, state: FSMContext):
    users = await get_users_by_status("all")

    text = "⬇️ Выберите человека ⬇️"
    keyboard = await settings_users_keyboard(users)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.settings_users)


@dp.callback_query_handler(text_startswith="settings_user_secret_key_", state=Status.settings_users)
async def but_facility_add(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.data.replace("settings_user_secret_key_", "")
    user = await get_user(user_id)

    text = (f"[Нажмите сюда](https://t.me/OtchetVKSBot?start={user['secret_key']})\n"
            f"Или введите в чат этот текст\n`{user['secret_key']}`")
    await send_message(callback_query.from_user.id, text, parse_mode="markdown")


@dp.callback_query_handler(text_startswith="settings_user_clear_balance_", state=Status.settings_users)
async def but_facility_add(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.data.replace("settings_user_clear_balance_", "")
    await update_user_clear_balance(user_id)

    users = await get_users_by_status("all")

    text = "⬇️ Выберите человека ⬇️"
    keyboard = await settings_users_keyboard(users)
    await send_last_message(callback_query.from_user.id, text, keyboard)


@dp.callback_query_handler(text_startswith="settings_user_delete_", state=Status.settings_users)
async def but_company_delete_(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.data.replace("settings_user_delete_", "")

    text = "Вы уверены?"
    keyboard = await yes_no_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(user_id=user_id)
    await state.set_state(Status.settings_users_delete)


@dp.callback_query_handler(text="settings_user_add", state=Status.settings_users)
async def but_company_add(callback_query: types.CallbackQuery, state: FSMContext):
    text = "Введите ФИО"
    keyboard = await back_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.settings_users_add)


@dp.message_handler(state=Status.settings_users_add)
async def status_company_add(message: types.Message, state: FSMContext):
    name = message.text
    if await get_user_by_user_name(name):
        text = "! Такое фио уже существует !\n Введите новые ФИО"
        keyboard = await back_keyboard()
        await send_last_message(message.from_user.id, text, keyboard)
    else:
        secret_key = await create_secret_key()
        await insert_user(name, secret_key)
        users = await get_users_by_status("all")

        text = "⬇️ Выберите человека ⬇️"
        keyboard = await settings_users_keyboard(users)
        await send_last_message(message.from_user.id, text, keyboard)

        await state.set_state(Status.settings_users)


####################################################################


@dp.callback_query_handler(text="view_company", state=Status.view_all)
async def but_view_companies(callback_query: types.CallbackQuery, state: FSMContext):
    companies = await get_companies_by_status("active")

    text = "⬇️ Выберите Компанию ⬇️"
    keyboard = await view_company_keyboard(companies)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.view_company)


@dp.callback_query_handler(text_startswith="view_company_", state=Status.view_company)
async def but_view_company_(callback_query: types.CallbackQuery, state: FSMContext):
    company_id = callback_query.data.replace("view_company_", "")

    text = "⬇️ Выберите дату начала ⬇️"
    keyboard = await calendar_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(company_id=company_id)
    await state.set_state(Status.view_company_date_from)


@dp.callback_query_handler(text_startswith="date_", state=Status.view_company_date_from)
async def but_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    date_from = callback_query.data.replace("date_", "")

    text = "⬇️ Выберите дату конца ⬇️"
    keyboard = await calendar_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(date_from=date_from)
    await state.set_state(Status.view_company_date_to)


@dp.callback_query_handler(text_startswith="date_", state=Status.view_company_date_to)
async def but_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    company_id = data["company_id"]
    date_from = data["date_from"]
    date_to = callback_query.data.replace("date_", "")

    text = "Файл собирается, подождите"
    mes = await send_message(callback_query.from_user.id, text)

    name = (await get_company(company_id))["name"]
    payments = await get_company_payments_in_interval(date_from, date_to, company_id)

    await create_excel(payments, name)

    await delete_last_message(callback_query.from_user.id)

    await send_message(callback_query.from_user.id, None, None, f"{name}.xlsx")

    await bot.delete_message(callback_query.from_user.id, mes.message_id)

    os.remove(f"{name}.xlsx")
    await state.finish()


@dp.callback_query_handler(text="view_facility", state=Status.view_all)
async def but_view_companies(callback_query: types.CallbackQuery, state: FSMContext):
    companies = await get_companies_by_status("active")

    text = "⬇️ Выберите Компанию ⬇️"
    keyboard = await view_company_keyboard(companies)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.view_facility)


@dp.callback_query_handler(text_startswith="view_company_", state=Status.view_facility)
async def but_view_company_(callback_query: types.CallbackQuery, state: FSMContext):
    company_id = callback_query.data.replace("view_company_", "")

    facilities = await get_facilities_by_status("active", company_id)

    text = "⬇️ Выберите объект ⬇️"
    keyboard = await view_facility_keyboard(facilities)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(company_id=company_id)
    await state.set_state(Status.view_facility)


@dp.callback_query_handler(text_startswith="view_facility_", state=Status.view_facility)
async def but_view_company_(callback_query: types.CallbackQuery, state: FSMContext):
    facility_id = callback_query.data.replace("view_facility_", "")

    text = "⬇️ Выберите дату начала ⬇️"
    keyboard = await calendar_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(facility_id=facility_id)
    await state.set_state(Status.view_facility_date_from)


@dp.callback_query_handler(text_startswith="date_", state=Status.view_facility_date_from)
async def but_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    date_from = callback_query.data.replace("date_", "")

    text = "⬇️ Выберите дату конца ⬇️"
    keyboard = await calendar_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(date_from=date_from)
    await state.set_state(Status.view_facility_date_to)


@dp.callback_query_handler(text_startswith="date_", state=Status.view_facility_date_to)
async def but_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    facility_id = data["facility_id"]
    date_from = data["date_from"]
    date_to = callback_query.data.replace("date_", "")

    text = "Файл собирается, подождите"
    mes = await send_message(callback_query.from_user.id, text)

    name = (await get_facility(facility_id))["name"]
    payments = await get_facility_payments_in_interval(date_from, date_to, facility_id)

    await create_excel(payments, name)

    await delete_last_message(callback_query.from_user.id)

    await send_message(callback_query.from_user.id, None, None, f"{name}.xlsx")

    await bot.delete_message(callback_query.from_user.id, mes.message_id)

    os.remove(f"{name}.xlsx")
    await state.finish()


@dp.callback_query_handler(text="view_purpose_type", state=Status.view_all)
async def but_view_companies(callback_query: types.CallbackQuery, state: FSMContext):
    purpose_types = await get_purpose_types_by_status("active")

    text = "⬇️ Выберите тип назначения ⬇️"
    keyboard = await view_purpose_type_keyboard(purpose_types)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.view_purpose_type)


@dp.callback_query_handler(text_startswith="view_purpose_type_", state=Status.view_purpose_type)
async def but_view_company_(callback_query: types.CallbackQuery, state: FSMContext):
    type_id = callback_query.data.replace("view_purpose_type_", "")

    text = "⬇️ Выберите дату начала ⬇️"
    keyboard = await calendar_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(type_id=type_id)
    await state.set_state(Status.view_purpose_type_date_from)


@dp.callback_query_handler(text_startswith="date_", state=Status.view_purpose_type_date_from)
async def but_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    date_from = callback_query.data.replace("date_", "")

    text = "⬇️ Выберите дату конца ⬇️"
    keyboard = await calendar_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(date_from=date_from)
    await state.set_state(Status.view_purpose_type_date_to)


@dp.callback_query_handler(text_startswith="date_", state=Status.view_purpose_type_date_to)
async def but_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    type_id = data["type_id"]
    date_from = data["date_from"]
    date_to = callback_query.data.replace("date_", "")

    text = "Файл собирается, подождите"
    mes = await send_message(callback_query.from_user.id, text)

    name = (await get_purpose_type(type_id))["name"]
    payments = await get_purpose_types_payments_in_interval(date_from, date_to, type_id)

    await create_excel(payments, name)

    await delete_last_message(callback_query.from_user.id)

    await send_message(callback_query.from_user.id, None, None, f"{name}.xlsx")

    await bot.delete_message(callback_query.from_user.id, mes.message_id)

    os.remove(f"{name}.xlsx")
    await state.finish()


@dp.callback_query_handler(text="view_purpose", state=Status.view_all)
async def but_view_companies(callback_query: types.CallbackQuery, state: FSMContext):
    purpose_types = await get_purpose_types_by_status("active")

    text = "⬇️ Выберите тип назначения ⬇️"
    keyboard = await view_purpose_type_keyboard(purpose_types)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.view_purpose)


@dp.callback_query_handler(text_startswith="view_purpose_type_", state=Status.view_purpose)
async def but_view_company_(callback_query: types.CallbackQuery, state: FSMContext):
    type_id = callback_query.data.replace("view_purpose_type_", "")

    purposes = await get_purposes_by_status("active", type_id)

    text = "⬇️ Выберите назначение ⬇️"
    keyboard = await view_purpose_keyboard(purposes)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(type_id=type_id)
    await state.set_state(Status.view_purpose)


@dp.callback_query_handler(text_startswith="view_purpose_", state=Status.view_purpose)
async def but_view_company_(callback_query: types.CallbackQuery, state: FSMContext):
    purpose_id = callback_query.data.replace("view_purpose_", "")

    text = "⬇️ Выберите дату начала ⬇️"
    keyboard = await calendar_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(purpose_id=purpose_id)
    await state.set_state(Status.view_purpose_date_from)


@dp.callback_query_handler(text_startswith="date_", state=Status.view_purpose_date_from)
async def but_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    date_from = callback_query.data.replace("date_", "")

    text = "⬇️ Выберите дату конца ⬇️"
    keyboard = await calendar_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(date_from=date_from)
    await state.set_state(Status.view_purpose_date_to)


@dp.callback_query_handler(text_startswith="date_", state=Status.view_purpose_date_to)
async def but_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    purpose_id = data["purpose_id"]
    date_from = data["date_from"]
    date_to = callback_query.data.replace("date_", "")

    text = "Файл собирается, подождите"
    mes = await send_message(callback_query.from_user.id, text)

    name = (await get_purpose(purpose_id))["name"]
    payments = await get_purposes_payments_in_interval(date_from, date_to, purpose_id)

    await create_excel(payments, name)

    await delete_last_message(callback_query.from_user.id)

    await send_message(callback_query.from_user.id, None, None, f"{name}.xlsx")

    await bot.delete_message(callback_query.from_user.id, mes.message_id)

    os.remove(f"{name}.xlsx")
    await state.finish()


@dp.callback_query_handler(text="view_user", state=Status.view_all)
async def but_view_companies(callback_query: types.CallbackQuery, state: FSMContext):
    users = await get_users_by_status("active")

    text = "⬇️ Выберите ФИО ⬇️"
    keyboard = await view_user_keyboard(users)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.view_user)


@dp.callback_query_handler(text_startswith="view_user_", state=Status.view_user)
async def but_view_company_(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.data.replace("view_user_", "")

    text = "⬇️ Выберите дату начала ⬇️"
    keyboard = await calendar_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(user_id=user_id)
    await state.set_state(Status.view_user_date_from)


@dp.callback_query_handler(text_startswith="date_", state=Status.view_user_date_from)
async def but_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    date_from = callback_query.data.replace("date_", "")

    text = "⬇️ Выберите дату конца ⬇️"
    keyboard = await calendar_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(date_from=date_from)
    await state.set_state(Status.view_user_date_to)


@dp.callback_query_handler(text_startswith="date_", state=Status.view_user_date_to)
async def but_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]
    date_from = data["date_from"]
    date_to = callback_query.data.replace("date_", "")

    text = "Файл собирается, подождите"
    mes = await send_message(callback_query.from_user.id, text)

    name = (await get_user(user_id))["name"]
    payments = await get_user_payments_in_interval(date_from, date_to, user_id)

    await create_excel(payments, name)

    await delete_last_message(callback_query.from_user.id)

    await send_message(callback_query.from_user.id, None, None, f"{name}.xlsx")

    await bot.delete_message(callback_query.from_user.id, mes.message_id)

    os.remove(f"{name}.xlsx")
    await state.finish()


@dp.callback_query_handler(text="view_creator", state=Status.view_all)
async def but_view_companies(callback_query: types.CallbackQuery, state: FSMContext):
    admins = await get_admins()

    text = "⬇️ Выберите автора ⬇️"
    keyboard = await view_creator_keyboard(admins)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.view_creator)


@dp.callback_query_handler(text_startswith="view_creator_", state=Status.view_creator)
async def but_view_company_(callback_query: types.CallbackQuery, state: FSMContext):
    tg_id = callback_query.data.replace("view_creator_", "")

    text = "⬇️ Выберите дату начала ⬇️"
    keyboard = await calendar_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(tg_id=tg_id)
    await state.set_state(Status.view_creator_date_from)


@dp.callback_query_handler(text_startswith="date_", state=Status.view_creator_date_from)
async def but_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    date_from = callback_query.data.replace("date_", "")

    text = "⬇️ Выберите дату конца ⬇️"
    keyboard = await calendar_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(date_from=date_from)
    await state.set_state(Status.view_creator_date_to)


@dp.callback_query_handler(text_startswith="date_", state=Status.view_creator_date_to)
async def but_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tg_id = data["tg_id"]
    date_from = data["date_from"]
    date_to = callback_query.data.replace("date_", "")

    text = "Файл собирается, подождите"
    mes = await send_message(callback_query.from_user.id, text)

    name = (await get_admin(tg_id))["name"]
    payments = await get_creator_payments_in_interval(date_from, date_to, tg_id)

    await create_excel(payments, name)

    await delete_last_message(callback_query.from_user.id)

    await send_message(callback_query.from_user.id, None, None, f"{name}.xlsx")

    await bot.delete_message(callback_query.from_user.id, mes.message_id)

    os.remove(f"{name}.xlsx")
    await state.finish()


####################################################################


@dp.callback_query_handler(text_startswith="calendar_year_back_", state="*")
async def but_date_year_back_(callback_query: types.CallbackQuery, state: FSMContext):
    month, year = callback_query.data.replace("calendar_year_back_", "").split("_")
    year = int(year) - 1

    text = "⬇️ Выберите дату ⬇️"
    keyboard = await calendar_keyboard(int(month), int(year))
    await change_message(callback_query.from_user.id, callback_query.message.message_id, text, keyboard)


@dp.callback_query_handler(text_startswith="calendar_year_forward_", state="*")
async def date_year_forward_(callback_query: types.CallbackQuery, state: FSMContext):
    month, year = callback_query.data.replace("calendar_year_forward_", "").split("_")
    year = int(year) + 1

    text = "⬇️ Выберите дату ⬇️"
    keyboard = await calendar_keyboard(int(month), int(year))
    await change_message(callback_query.from_user.id, callback_query.message.message_id, text, keyboard)


@dp.callback_query_handler(text_startswith="calendar_month_back_", state="*")
async def but_date_month_back_(callback_query: types.CallbackQuery, state: FSMContext):
    month, year = callback_query.data.replace("calendar_month_back_", "").split("_")
    month = int(month) - 1
    if month == 0:
        month = 12
        year = int(year) - 1

    text = "⬇️ Выберите дату ⬇️"
    keyboard = await calendar_keyboard(int(month), int(year))
    await change_message(callback_query.from_user.id, callback_query.message.message_id, text, keyboard)


@dp.callback_query_handler(text_startswith="calendar_month_forward_", state="*")
async def but_date_month_forward_(callback_query: types.CallbackQuery, state: FSMContext):
    month, year = callback_query.data.replace("calendar_month_forward_", "").split("_")
    month = int(month) + 1
    if month == 13:
        month = 1
        year = int(year) + 1

    text = "⬇️ Выберите дату ⬇️"
    keyboard = await calendar_keyboard(int(month), int(year))
    await change_message(callback_query.from_user.id, callback_query.message.message_id, text, keyboard)


####################################################################


@dp.callback_query_handler(text="yes", state="*")
async def but_yes(callback_query: types.CallbackQuery, state: FSMContext):
    current_data = await state.get_data()
    current_state = await state.get_state()
    if current_state == "Status:settings_company_delete":
        company_id = current_data["company_id"]
        await update_company_delete(company_id)
        companies = await get_companies_by_status("all")

        text = "⬇️ Выберите Компанию ⬇️"
        keyboard = await settings_companies_keyboard(companies)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        del(current_data["company_id"])
        await state.set_data(current_data)
        await state.set_state(Status.settings_companies)
    elif current_state == "Status:settings_facility_delete":
        company_id = current_data["company_id"]
        facility_id = current_data["facility_id"]
        await update_facility_delete(facility_id)
        facilities = await get_facilities_by_status("all", company_id)

        text = "⬇️ Выберите объект ⬇️"
        keyboard = await settings_facilities_keyboard(facilities)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        del(current_data["facility_id"])
        await state.set_data(current_data)
        await state.set_state(Status.settings_facilities)
    elif current_state == "Status:settings_users_delete":
        user_id = current_data["user_id"]
        await update_user_delete(user_id)
        users = await get_users_by_status("all")

        text = "⬇️ Выберите человека ⬇️"
        keyboard = await settings_users_keyboard(users)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        del(current_data["user_id"])
        await state.set_data(current_data)
        await state.set_state(Status.settings_users)
    elif current_state == "Status:settings_purpose_type_delete":
        type_id = current_data["type_id"]
        await update_purpose_type_delete(type_id)
        purpose_types = await get_purpose_types_by_status("all")

        text = "⬇️ Выберите тип назначения ⬇️"
        keyboard = await settings_purpose_types_keyboard(purpose_types)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        del(current_data["type_id"])
        await state.set_data(current_data)
        await state.set_state(Status.settings_purpose_types)
    elif current_state == "Status:settings_purpose_delete":
        type_id = current_data["type_id"]
        purpose_id = current_data["purpose_id"]
        await update_purpose_delete(purpose_id)
        purposes = await get_purposes_by_status("all", type_id)

        text = "⬇️ Выберите назначение ⬇️"
        keyboard = await settings_purposes_keyboard(purposes)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        del(current_data["purpose_id"])
        await state.set_data(current_data)
        await state.set_state(Status.settings_purposes)


@dp.callback_query_handler(text="back", state="*")
async def but_no(callback_query: types.CallbackQuery, state: FSMContext):
    current_data = await state.get_data()
    current_state = await state.get_state()
    if current_state == "Status:payment_facility":
        companies = await get_companies_by_status("active")

        text = "⬇️ Выберите Компанию ⬇️"
        keyboard = await payment_company_keyboard(companies)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        del (current_data["company_id"])
        await state.set_data(current_data)
        await state.set_state(Status.payment_company)
    elif current_state == "Status:payment_amount":
        company_id = current_data["company_id"]
        facilities = await get_facilities_by_status("active", company_id)

        text = "⬇️ Выберите объект ⬇️"
        keyboard = await payment_facility_keyboard(facilities)

        await send_last_message(callback_query.from_user.id, text, keyboard)

        del(current_data["facility_id"])
        await state.set_data(current_data)
        await state.set_state(Status.payment_facility)
    elif current_state == "Status:payment_date":
        text = "Введите сумму"
        keyboard = await back_cancel_keyboard()
        await send_last_message(callback_query.from_user.id, text, keyboard)

        del (current_data["amount"])
        await state.set_data(current_data)
        await state.set_state(Status.payment_amount)
    elif current_state == "Status:payment_choice":
        text = "⬇️ Выберите дату ⬇️"
        keyboard = await calendar_keyboard()
        await send_last_message(callback_query.from_user.id, text, keyboard)

        del (current_data["date"])
        await state.set_data(current_data)
        await state.set_state(Status.payment_date)
    elif current_state in ["Status:payment_purpose_type", "Status:payment_user_name"]:
        text = "⬇️ Выберите пункт меню ⬇️"
        keyboard = await payment_choice_keyboard()
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.set_state(Status.payment_choice)
    elif current_state == "Status:payment_purpose":
        purpose_types = await get_purpose_types_by_status(True)

        text = "⬇️ Выберите назначение ⬇️"
        keyboard = await payment_purpose_type_keyboard(purpose_types)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        del (current_data["type_id"])
        await state.set_data(current_data)
        await state.set_state(Status.payment_purpose_type)
    elif current_state == "Status:payment_comment":
        if "purpose_id" in current_data:
            type_id = current_data["type_id"]
            purposes = await get_purposes_by_status(True, type_id)

            text = "⬇️ Выберите назначение ⬇️"
            keyboard = await payment_purpose_keyboard(purposes)
            await send_last_message(callback_query.from_user.id, text, keyboard)

            del (current_data["purpose_id"])
            await state.set_data(current_data)
            await state.set_state(Status.payment_purpose)
        else:
            users = await get_users_by_status(True)

            text = "⬇️ Выберите пользователя из списка ⬇️\nИли введите текстом новое фио"
            keyboard = await payment_users_keyboard(users)
            await send_last_message(callback_query.from_user.id, text, keyboard)

            del (current_data["user_name"])
            await state.set_data(current_data)
            await state.set_state(Status.payment_user_name)

    elif current_state in ["Status:settings_companies", "Status:settings_purpose_types", "Status:settings_users"]:
        text = "⬇️ Выберите пункт меню ⬇️"
        keyboard = await settings_keyboard()
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.finish()
        await state.set_state(Status.settings)
    elif current_state in ["Status:settings_company_add", "Status:settings_company_delete", "Status:settings_facilities"]:
        companies = await get_companies_by_status("all")

        text = "⬇️ Выберите Компанию ⬇️"
        keyboard = await settings_companies_keyboard(companies)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.set_state(Status.settings_companies)
    elif current_state in ["Status:settings_facility_add", "Status:settings_facility_delete"]:
        company_id = current_data["company_id"]
        facilities = await get_facilities_by_status("all", company_id)

        text = "⬇️ Выберите объект ⬇️"
        keyboard = await settings_facilities_keyboard(facilities)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.set_state(Status.settings_facilities)
    elif current_state in ["Status:settings_purpose_type_add", "Status:settings_purpose_type_delete", "Status:settings_purposes"]:
        purpose_types = await get_purpose_types_by_status("all")

        text = "⬇️ Выберите тип назначения ⬇️"
        keyboard = await settings_purpose_types_keyboard(purpose_types)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.set_state(Status.settings_purpose_types)
    elif current_state in ["Status:settings_purpose_add", "Status:settings_purpose_delete"]:
        type_id = current_data["type_id"]
        purposes = await get_purposes_by_status("all", type_id)

        text = "⬇️ Выберите назначение ⬇️"
        keyboard = await settings_purposes_keyboard(purposes)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.set_state(Status.settings_purposes)
    elif current_state in ["Status:settings_users_add", "Status:settings_users_delete", "Status:settings_users_clear_balance"]:
        users = await get_users_by_status("all")

        text = "⬇️ Выберите человека ⬇️"
        keyboard = await settings_users_keyboard(users)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.set_state(Status.settings_users)

    # elif current_state in ["Status:view_all_date_from", "Status:view_companies"]:
    #     text = "⬇️ Выберите пункт меню ⬇️"
    #     keyboard = await view_keyboard()
    #     await send_last_message(callback_query.from_user.id, text, keyboard)
    #
    #     await state.finish()
    #     await state.set_state(Status.view_all)
    # elif current_state == "Status:view_all_date_to":
    #     text = "⬇️ Выберите дату начала ⬇️"
    #     keyboard = await date_keyboard()
    #     await send_last_message(callback_query.from_user.id, text, keyboard)
    #
    #     del (current_data["date_from"])
    #     await state.set_data(current_data)
    #     await state.set_state(Status.view_all_date_from)
    # elif current_state in ["Status:view_company_date_from", "Status:view_facilities"]:
    #     companies = await get_companies_by_status("active")
    #
    #     text = "⬇️ Выберите Компанию ⬇️"
    #     keyboard = await view_companies_keyboard(companies)
    #     await send_last_message(callback_query.from_user.id, text, keyboard)
    #
    #     await state.set_state(Status.view_companies)
    # elif current_state == "Status:view_company_date_to":
    #     text = "⬇️ Выберите дату начала ⬇️"
    #     keyboard = await date_keyboard()
    #     await send_last_message(callback_query.from_user.id, text, keyboard)
    #
    #     del (current_data["date_from"])
    #     await state.set_data(current_data)
    #     await state.set_state(Status.view_company_date_from)
    # elif current_state == "Status:view_facility_date_from":
    #     company_id = current_data["company_id"]
    #     facilities = await get_facilities_by_status("active", company_id)
    #
    #     text = "⬇️ Выберите объект ⬇️"
    #     keyboard = await view_facilities_keyboard(facilities)
    #     await send_last_message(callback_query.from_user.id, text, keyboard)
    #
    #     await state.set_state(Status.view_facilities)
    # elif current_state == "Status:view_facility_date_to":
    #     text = "⬇️ Выберите дату начала ⬇️"
    #     keyboard = await date_keyboard()
    #     await send_last_message(callback_query.from_user.id, text, keyboard)
    #
    #     del (current_data["date_from"])
    #     await state.set_data(current_data)
    #     await state.set_state(Status.view_facility_date_from)


@dp.callback_query_handler(text="cancel", state="*")
async def but_no(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_last_message(callback_query.from_user.id)

    await state.finish()
