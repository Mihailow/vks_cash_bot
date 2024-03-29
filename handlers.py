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


@dp.message_handler(text="Изменить Компании/объекты", state="*")
async def change_companies(message: types.Message, state: FSMContext):
    companies = await get_companies_by_status("all")

    text = "⬇️ Выберите Компанию ⬇️"
    keyboard = await change_companies_keyboard(companies)
    await send_last_message(message.from_user.id, text, keyboard)

    await state.finish()
    await state.set_state(Status.companies)


@dp.message_handler(text="Просмотр", state="*")
async def view_payments(message: types.Message, state: FSMContext):
    text = "⬇️ Выберите пункт меню ⬇️"
    keyboard = await view_keyboard()
    await send_last_message(message.from_user.id, text, keyboard)

    await state.finish()
    await state.set_state(Status.view_all)


@dp.callback_query_handler(text_startswith="payment_company_", state=Status.payment_company)
async def but_payment_company_payment_company_(callback_query: types.CallbackQuery, state: FSMContext):
    company_id = callback_query.data.replace("payment_company_", "")
    objects = await get_objects_by_status("active", company_id)

    text = "⬇️ Выберите объект ⬇️"
    keyboard = await payment_object_keyboard(objects)

    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(company_id=company_id)
    await state.set_state(Status.payment_object)


@dp.callback_query_handler(text_startswith="payment_object_", state=Status.payment_object)
async def but_payment_object_payment_object_(callback_query: types.CallbackQuery, state: FSMContext):
    object_id = callback_query.data.replace("payment_object_", "")

    text = "Введите сумму"
    keyboard = await back_cancel_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(object_id=object_id)
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

    text = "Выберите дату"
    keyboard = await payment_date_keyboard()
    await send_last_message(message.from_user.id, text, keyboard)

    await state.update_data(amount=message.text)
    await state.set_state(Status.payment_date)


@dp.callback_query_handler(text_startswith="payment_date_", state=Status.payment_date)
async def but_payment_date_payment_date_(callback_query: types.CallbackQuery, state: FSMContext):
    date = callback_query.data.replace("payment_date_", "")

    text = "⬇️ Выберите пункт меню ⬇️"
    keyboard = await payment_choice_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(date=date)
    await state.set_state(Status.payment_choice)


@dp.callback_query_handler(text="payment_spent_for", state=Status.payment_choice)
async def but_payment_spent_for(callback_query: types.CallbackQuery, state: FSMContext):
    purpose_types = await get_purpose_types()

    text = "⬇️ Выберите назначение ⬇️"
    keyboard = await purpose_type_keyboard(purpose_types)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.payment_purpose_type)


@dp.callback_query_handler(text_startswith="payment_purpose_type_", state=Status.payment_purpose_type)
async def but_payment_spent_r(callback_query: types.CallbackQuery, state: FSMContext):
    purpose_type = callback_query.data.replace("payment_purpose_type_", "")
    purposes = await get_purposes(purpose_type)

    text = "⬇️ Выберите назначение ⬇️"
    keyboard = await purpose_keyboard(purposes)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.payment_purpose)


@dp.callback_query_handler(text_startswith="payment_purpose_", state=Status.payment_purpose)
async def but_payment_purpose_(callback_query: types.CallbackQuery, state: FSMContext):
    purpose_id = callback_query.data.replace("payment_purpose_", "")

    text = "Введите комментарий"
    keyboard = await payment_send_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(purpose_id=purpose_id)
    await state.set_state(Status.payment_comment)


@dp.callback_query_handler(text="payment_user_name", state=Status.payment_choice)
async def but_payment_spent_for(callback_query: types.CallbackQuery, state: FSMContext):
    users = await get_all_users_id()

    text = "Выберите пользователя из списка\nИли выберите из списка"
    keyboard = await payment_users_keyboard(users, 1)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.payment_user_name)
    await state.update_data(user_name_page=1)


@dp.callback_query_handler(text="payment_user_page_back", state=Status.payment_user_name)
async def but_payment_user_page_back(callback_query: types.CallbackQuery, state: FSMContext):
    users = await get_all_users_id()
    page = (await state.get_data())["payment_user_name"]
    if page > 1:
        page -= 1

    text = "Выберите пользователя из списка\nИли выберите из списка"
    keyboard = await payment_users_keyboard(users, page)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(user_name_page=page)


@dp.callback_query_handler(text="payment_user_page_forward", state=Status.payment_user_name)
async def but_payment_user_page_forward(callback_query: types.CallbackQuery, state: FSMContext):
    users = await get_all_users_id()
    page = (await state.get_data())["payment_user_name"]
    pages = len(users) // 10
    if len(users) % 10 != 0:
        pages += 1
    if page < pages:
        page += 1

    text = "Выберите пользователя из списка\nИли выберите из списка"
    keyboard = await payment_users_keyboard(users, page)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(user_name_page=page)


@dp.callback_query_handler(text_startswith="payment_user_name_", state=Status.payment_user_name)
async def but_payment_user_page_forward(callback_query: types.CallbackQuery, state: FSMContext):
    user_name = callback_query.data.replace("payment_user_name_", "")

    text = "Введите комментарий"
    keyboard = await payment_send_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(user_name=user_name)
    await state.set_state(Status.payment_comment)


@dp.message_handler(state=Status.payment_user_name)
async def status_payment_spent_for(message: types.Message, state: FSMContext):
    user_name = message.text
    if await get_user_by_user_name(user_name):
        users = await get_all_users_id()

        text = "! Такое фио уже существует !\nВыберите пользователя из списка\nИли выберите из списка"
        keyboard = await payment_users_keyboard(users, 1)
        await send_last_message(message.from_user.id, text, keyboard)

        await state.update_data(user_name_page=1)
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


@dp.callback_query_handler(text_startswith="company_change_name_", state=Status.companies)
async def but_company_change_name_(callback_query: types.CallbackQuery, state: FSMContext):
    company_id = callback_query.data.replace("company_change_name_", "")
    
    text = "Введите новое название"
    keyboard = await back_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.company_change_name)
    await state.update_data(company_id=company_id)


@dp.message_handler(state=Status.company_change_name)
async def status_company_change_name(message: types.Message, state: FSMContext):
    name = message.text
    company_id = (await state.get_data())["company_id"]
    await update_company_name(company_id, message.text)
    companies = await get_companies_by_status("all")

    text = "Выберите Компанию"
    keyboard = await change_companies_keyboard(companies)
    await send_last_message(message.from_user.id, text, keyboard)

    await state.finish()
    await state.set_state(Status.companies)


@dp.callback_query_handler(text_startswith="company_change_status_", state=Status.companies)
async def but_company_change_status_(callback_query: types.CallbackQuery, state: FSMContext):
    company_id = callback_query.data.replace("company_change_status_", "")
    await update_company_status(company_id)
    companies = await get_companies_by_status("all")

    text = "Выберите Компанию"
    keyboard = await change_companies_keyboard(companies)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.finish()
    await state.set_state(Status.companies)


@dp.callback_query_handler(text_startswith="company_delete_", state=Status.companies)
async def but_company_delete_(callback_query: types.CallbackQuery, state: FSMContext):
    company_id = callback_query.data.replace("company_delete_", "")

    text = "Вы уверены?"
    keyboard = await yes_no_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.finish()
    await state.update_data(company_id=company_id)
    await state.set_state(Status.company_delete)


@dp.callback_query_handler(text_startswith="company_add", state=Status.companies)
async def but_company_add(callback_query: types.CallbackQuery, state: FSMContext):
    text = "Введите название"
    keyboard = await back_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.company_add)


@dp.message_handler(state=Status.company_add)
async def status_company_add(message: types.Message, state: FSMContext):
    name = message.text
    await insert_company(name)
    companies = await get_companies_by_status("all")

    text = "Выберите Компанию"
    keyboard = await change_companies_keyboard(companies)
    await send_last_message(message.from_user.id, text, keyboard)

    await state.finish()
    await state.set_state(Status.companies)


@dp.callback_query_handler(text_startswith="objects_in_company_", state=Status.companies)
async def but_objects_in_company_(callback_query: types.CallbackQuery, state: FSMContext):
    company_id = callback_query.data.replace("objects_in_company_", "")
    objects = await get_objects_by_status("all", company_id)

    text = "Выберите объект"
    keyboard = await change_objects_keyboard(objects)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.objects)
    await state.update_data(company_id=company_id)


@dp.callback_query_handler(text_startswith="object_change_name_", state=Status.objects)
async def but_object_change_name_(callback_query: types.CallbackQuery, state: FSMContext):
    object_id = callback_query.data.replace("object_change_name_", "")

    text = "Введите новое название"
    keyboard = await back_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.object_change_name)
    await state.update_data(object_id=object_id)


@dp.message_handler(state=Status.object_change_name)
async def status_object_change_name(message: types.Message, state: FSMContext):
    name = message.text
    data = await state.get_data()
    company_id = data["company_id"]
    object_id = data["object_id"]
    await update_object_name(object_id, message.text)
    objects = await get_objects_by_status("all", company_id)

    text = "Выберите объект"
    keyboard = await change_objects_keyboard(objects)
    await send_last_message(message.from_user.id, text, keyboard)

    await state.set_state(Status.objects)


@dp.callback_query_handler(text_startswith="object_change_status_", state=Status.objects)
async def but_object_change_status_(callback_query: types.CallbackQuery, state: FSMContext):
    company_id = (await state.get_data())["company_id"]
    objects_id = callback_query.data.replace("object_change_status_", "")
    await update_object_status(objects_id)
    objects = await get_objects_by_status("all", company_id)

    text = "Выберите объект"
    keyboard = await change_objects_keyboard(objects)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.objects)


@dp.callback_query_handler(text_startswith="object_delete_", state=Status.objects)
async def but_object_delete_(callback_query: types.CallbackQuery, state: FSMContext):
    object_id = callback_query.data.replace("object_delete_", "")

    text = "Вы уверены?"
    keyboard = await yes_no_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.update_data(object_id=object_id)
    await state.set_state(Status.object_delete)


@dp.callback_query_handler(text_startswith="object_add", state=Status.objects)
async def but_object_add(callback_query: types.CallbackQuery, state: FSMContext):
    text = "Введите название"
    keyboard = await back_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.object_add)


@dp.message_handler(state=Status.object_add)
async def status_object_add(message: types.Message, state: FSMContext):
    company_id = (await state.get_data())["company_id"]
    name = message.text
    await insert_object(name, company_id)
    objects = await get_objects_by_status("all", company_id)

    text = "Выберите объект"
    keyboard = await change_objects_keyboard(objects)
    await send_last_message(message.from_user.id, text, keyboard)

    await state.set_state(Status.objects)


@dp.callback_query_handler(text="view_all", state=Status.view_all)
async def but_view_all(callback_query: types.CallbackQuery, state: FSMContext):
    text = "Выберите дату начала"
    keyboard = await payment_date_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.view_all_date_from)


@dp.callback_query_handler(text_startswith="payment_date_", state=Status.view_all_date_from)
async def but_payment_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    date_from = callback_query.data.replace("payment_date_", "")

    text = "Выберите дату конца"
    keyboard = await payment_date_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.view_all_date_to)
    await state.update_data(date_from=date_from)


@dp.callback_query_handler(text_startswith="payment_date_", state=Status.view_all_date_to)
async def but_payment_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    date_from = (await state.get_data())["date_from"]
    date_to = callback_query.data.replace("payment_date_", "")

    text = "Файл собирается, подождите"
    mes = await send_message(callback_query.from_user.id, text)

    name = await create_excel_for_all(date_from, date_to)

    await delete_last_message(callback_query.from_user.id)

    await send_message(callback_query.from_user.id, None, None, f"{name}.xlsx")

    await bot.delete_message(callback_query.from_user.id, mes.message_id)

    os.remove(f"{name}.xlsx")
    await state.finish()


@dp.callback_query_handler(text="view_companies", state=Status.view_all)
async def but_view_companies(callback_query: types.CallbackQuery, state: FSMContext):
    companies = await get_companies_by_status("active")

    text = "Выберите Компанию"
    keyboard = await view_companies_keyboard(companies)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.view_companies)


@dp.callback_query_handler(text_startswith="view_company_", state=Status.view_companies)
async def but_view_company_(callback_query: types.CallbackQuery, state: FSMContext):
    company_id = callback_query.data.replace("view_company_", "")

    text = "Выберите дату начала"
    keyboard = await payment_date_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.view_company_date_from)
    await state.update_data(company_id=company_id)


@dp.callback_query_handler(text_startswith="payment_date_", state=Status.view_company_date_from)
async def but_payment_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    date_from = callback_query.data.replace("payment_date_", "")

    text = "Выберите дату конца"
    keyboard = await payment_date_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.view_company_date_to)
    await state.update_data(date_from=date_from)


@dp.callback_query_handler(text_startswith="payment_date_", state=Status.view_company_date_to)
async def but_payment_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    company_id = data["company_id"]
    date_from = data["date_from"]
    date_to = callback_query.data.replace("payment_date_", "")

    text = "Файл собирается, подождите"
    mes = await send_message(callback_query.from_user.id, text)

    name = await create_excel(date_from, date_to, company_id=company_id)

    await delete_last_message(callback_query.from_user.id)

    await send_message(callback_query.from_user.id, None, None, f"{name}.xlsx")

    await bot.delete_message(callback_query.from_user.id, mes.message_id)

    os.remove(f"{name}.xlsx")
    await state.finish()


@dp.callback_query_handler(text_startswith="view_objects_", state=Status.view_companies)
async def but_view_companies(callback_query: types.CallbackQuery, state: FSMContext):
    company_id = callback_query.data.replace("view_objects_", "")
    objects = await get_objects_by_status("active", company_id)

    text = "Выберите объект"
    keyboard = await view_objects_keyboard(objects)
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.view_objects)
    await state.update_data(company_id=company_id)


@dp.callback_query_handler(text_startswith="view_object_", state=Status.view_objects)
async def but_view_company_(callback_query: types.CallbackQuery, state: FSMContext):
    object_id = callback_query.data.replace("view_object_", "")

    text = "Выберите дату начала"
    keyboard = await payment_date_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.view_object_date_from)
    await state.update_data(object_id=object_id)


@dp.callback_query_handler(text_startswith="payment_date_", state=Status.view_object_date_from)
async def but_payment_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    date_from = callback_query.data.replace("payment_date_", "")

    text = "Выберите дату конца"
    keyboard = await payment_date_keyboard()
    await send_last_message(callback_query.from_user.id, text, keyboard)

    await state.set_state(Status.view_object_date_to)
    await state.update_data(date_from=date_from)


@dp.callback_query_handler(text_startswith="payment_date_", state=Status.view_object_date_to)
async def but_payment_date_company_date_to_(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    object_id = data["company_id"]
    date_from = data["date_from"]
    date_to = callback_query.data.replace("payment_date_", "")

    text = "Файл собирается, подождите"
    mes = await send_message(callback_query.from_user.id, text)

    name = await create_excel(date_from, date_to, object_id=object_id)

    await delete_last_message(callback_query.from_user.id)

    await send_message(callback_query.from_user.id, None, None, f"{name}.xlsx")

    await bot.delete_message(callback_query.from_user.id, mes.message_id)

    os.remove(f"{name}.xlsx")
    await state.finish()


@dp.callback_query_handler(text_startswith="payment_year_back_", state="*")
async def but_payment_year_back_(callback_query: types.CallbackQuery, state: FSMContext):
    month, year = callback_query.data[18:].split("_")
    year = int(year) - 1

    text = "Выберите дату"
    keyboard = await payment_date_keyboard(int(month), int(year))
    await change_message(callback_query.from_user.id, callback_query.message.message_id, text, keyboard)


@dp.callback_query_handler(text_startswith="payment_year_forward_", state="*")
async def payment_year_forward_(callback_query: types.CallbackQuery, state: FSMContext):
    month, year = callback_query.data[21:].split("_")
    year = int(year) + 1

    text = "Выберите дату"
    keyboard = await payment_date_keyboard(int(month), int(year))
    await change_message(callback_query.from_user.id, callback_query.message.message_id, text, keyboard)


@dp.callback_query_handler(text_startswith="payment_month_back_", state="*")
async def but_payment_month_back_(callback_query: types.CallbackQuery, state: FSMContext):
    month, year = callback_query.data[19:].split("_")
    month = int(month) - 1
    if month == 0:
        month = 12
        year = int(year) - 1

    text = "Выберите дату"
    keyboard = await payment_date_keyboard(int(month), int(year))
    await change_message(callback_query.from_user.id, callback_query.message.message_id, text, keyboard)


@dp.callback_query_handler(text_startswith="payment_month_forward_", state="*")
async def but_payment_month_forward_(callback_query: types.CallbackQuery, state: FSMContext):
    month, year = callback_query.data[22:].split("_")
    month = int(month) + 1
    if month == 13:
        month = 1
        year = int(year) + 1

    text = "Выберите дату"
    keyboard = await payment_date_keyboard(int(month), int(year))
    await change_message(callback_query.from_user.id, callback_query.message.message_id, text, keyboard)


@dp.callback_query_handler(text="yes", state="*")
async def but_yes(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    current_data = await state.get_data()
    if current_state == "Status:company_delete":
        company_id = current_data["company_id"]
        await update_company_delete(company_id)
        companies = await get_companies_by_status("all")

        text = "Выберите Компанию"
        keyboard = await change_companies_keyboard(companies)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.finish()
        await state.set_state(Status.companies)
    elif current_state == "Status:object_delete":
        company_id = current_data["company_id"]
        object_id = current_data["object_id"]
        await update_object_delete(object_id)
        objects = await get_objects_by_status("all", company_id)

        text = "Выберите объект"
        keyboard = await change_objects_keyboard(objects)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        del(current_data["object_id"])
        await state.set_data(current_data)
        await state.set_state(Status.objects)


@dp.callback_query_handler(text="back", state="*")
async def but_no(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    current_data = await state.get_data()
    if current_state == "Status:payment_company":
        await delete_last_message(callback_query.from_user.id)

        await state.finish()
    elif current_state == "Status:payment_object":
        companies = await get_companies_by_status("active")

        text = "Выберите Компанию"
        keyboard = await payment_company_keyboard(companies)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.finish()
        await state.set_state(Status.payment_company)
    elif current_state == "Status:payment_amount":
        company_id = current_data["company_id"]
        objects = await get_objects_by_status("active", company_id)

        text = "Выберите объект"
        keyboard = await payment_object_keyboard(objects)

        await send_last_message(callback_query.from_user.id, text, keyboard)

        del(current_data["company_id"])
        await state.set_data(current_data)
        await state.set_state(Status.payment_object)
    elif current_state == "Status:payment_date":
        text = "Введите сумму"
        keyboard = await back_cancel_keyboard()
        await send_last_message(callback_query.from_user.id, text, keyboard)

        del (current_data["object_id"])
        await state.set_data(current_data)
        await state.set_state(Status.payment_amount)
    elif current_state == "Status:payment_choice":
        text = "Выберите дату"
        keyboard = await payment_date_keyboard()
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
        purpose_types = await get_purpose_types()

        text = "⬇️ Выберите назначение ⬇️"
        keyboard = await purpose_type_keyboard(purpose_types)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.set_state(Status.payment_purpose_type)
    elif current_state == "Status:payment_comment":
        if "purpose_id" in current_data:
            purpose = await get_purpose(current_data["purpose_id"])
            purposes = await get_purposes(purpose["type"])

            text = "⬇️ Выберите назначение ⬇️"
            keyboard = await purpose_keyboard(purposes)
            await send_last_message(callback_query.from_user.id, text, keyboard)

            del (current_data["purpose_id"])
            await state.set_data(current_data)
            await state.set_state(Status.payment_purpose)
        else:
            users = await get_all_users_id()

            text = "Выберите пользователя из списка\nИли выберите из списка"
            keyboard = await payment_users_keyboard(users, 1)
            await send_last_message(callback_query.from_user.id, text, keyboard)

            del (current_data["user_name"])
            current_data["user_name_page"] = 1
            await state.set_data(current_data)
            await state.set_state(Status.payment_user_name)
    elif current_state in ["Status:company_add", "Status:company_change_name", "Status:company_delete", "Status:objects"]:
        companies = await get_companies_by_status("all")

        text = "Выберите Компанию"
        keyboard = await change_companies_keyboard(companies)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.finish()
        await state.set_state(Status.companies)
    elif current_state in ["Status:object_add", "Status:object_change_name", "Status:object_delete"]:
        company_id = current_data["company_id"]
        objects = await get_objects_by_status("all", company_id)

        text = "Выберите объект"
        keyboard = await change_objects_keyboard(objects)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        del(current_data["object_id"])
        await state.set_data(current_data)
        await state.set_state(Status.objects)
    elif current_state in ["Status:view_all_date_from", "Status:view_companies"]:
        text = "Выберите пункт меню"
        keyboard = await view_keyboard()
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.finish()
        await state.set_state(Status.view_all)
    elif current_state == "Status:view_all_date_to":
        text = "Выберите дату начала"
        keyboard = await payment_date_keyboard()
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.set_state(Status.view_all_date_from)
        del (current_data["date_from"])
        await state.set_data(current_data)
    elif current_state in ["Status:view_company_date_from", "Status:view_objects"]:
        companies = await get_companies_by_status("active")

        text = "Выберите Компанию"
        keyboard = await view_companies_keyboard(companies)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.set_state(Status.view_companies)
    elif current_state == "Status:view_company_date_to":
        text = "Выберите дату начала"
        keyboard = await payment_date_keyboard()
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.set_state(Status.view_company_date_from)
        del (current_data["date_from"])
        await state.set_data(current_data)
    elif current_state == "Status:view_object_date_from":
        company_id = current_data["company_id"]
        objects = await get_objects_by_status("active", company_id)

        text = "Выберите объект"
        keyboard = await view_objects_keyboard(objects)
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.set_state(Status.view_objects)
    elif current_state == "Status:view_object_date_to":
        text = "Выберите дату начала"
        keyboard = await payment_date_keyboard()
        await send_last_message(callback_query.from_user.id, text, keyboard)

        await state.set_state(Status.view_object_date_from)
        del (current_data["date_from"])
        await state.set_data(current_data)


@dp.callback_query_handler(text="cancel", state="*")
async def but_no(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_last_message(callback_query.from_user.id)

    await state.finish()
