from secrets import token_urlsafe
import openpyxl
import logging

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler

from config import *
from postgres import *


class Status(StatesGroup):
    payment_company = State()
    payment_facility = State()
    payment_amount = State()
    payment_date = State()
    payment_choice = State()
    payment_purpose_type = State()
    payment_purpose = State()
    payment_user_name = State()
    payment_comment = State()

    settings = State()

    settings_companies = State()
    settings_company_delete = State()
    settings_company_add = State()

    settings_facilities = State()
    settings_facility_delete = State()
    settings_facility_add = State()

    settings_purpose_types = State()
    settings_purpose_type_delete = State()
    settings_purpose_type_add = State()

    settings_purposes = State()
    settings_purpose_delete = State()
    settings_purpose_add = State()

    settings_users = State()
    settings_users_clear_balance = State()
    settings_users_delete = State()
    settings_users_add = State()

    view_all = State()
    view_all_date_from = State()
    view_all_date_to = State()
    view_company = State()
    view_company_date_from = State()
    view_company_date_to = State()
    view_facility = State()
    view_facility_date_from = State()
    view_facility_date_to = State()
    view_purpose_type = State()
    view_purpose_type_date_from = State()
    view_purpose_type_date_to = State()
    view_purpose = State()
    view_purpose_date_from = State()
    view_purpose_date_to = State()
    view_user = State()
    view_user_date_from = State()
    view_user_date_to = State()
    view_creator = State()
    view_creator_date_from = State()
    view_creator_date_to = State()


class CheckBotStatusMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        await bot.delete_message(message.from_user.id, message.message_id)
        await self.before_any_process(message.from_user.id, message.message_id, message.text)
        logging.info(f"\n   Пользователь: {message.from_user.id} прислал сообщение\n"
                     f"   Id сообщения: {message.message_id}\n"
                     f"   Текст сообщения: {message.text}\n"
                     f"   Тип сообщения: {message.content_type}")

    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        await callback_query.answer()
        logging.info(f"\n   Пользователь: {callback_query.from_user.id} нажал кнопку\n"
                     f"   Id сообщения: {callback_query.message.message_id}\n"
                     f"   Текст сообщения: {callback_query.message.text}\n"
                     f"   Callback: {callback_query.data}")
        await self.before_any_process(callback_query.from_user.id, callback_query.message.message_id,
                                      call_data=callback_query.data)

    @staticmethod
    async def before_any_process(user_id, mes_id, mes_text=None, call_data=None):
        if user_id == 641825727 and is_testing is False:
            text = "Работаю!"
            await send_message(user_id, text)
        admin = await get_admin(user_id)
        if admin is None:
            raise CancelHandler()


middleware = CheckBotStatusMiddleware()
dp.middleware.setup(middleware)


async def change_buttons():
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def send_message(chat_id, text, keyboard=None, document=None, reply=None, parse_mode=None):
    if document:
        try:
            document_file = open(str(document), "rb")
            mes = await bot.send_document(chat_id, document_file, caption=text, reply_markup=keyboard,
                                          reply_to_message_id=reply)
            logging.info(f"\n   Бот ответил пользователю {mes.chat.id}\n"
                         f"   Id сообщения: {mes.message_id}\n"
                         f"   Текст сообщения: {mes.text}\n")
            return mes
        except Exception as e:
            logging.error(f"send_message {chat_id}", exc_info=True)

    mes = await bot.send_message(chat_id, text=text, reply_markup=keyboard, reply_to_message_id=reply,
                                 parse_mode=parse_mode)
    logging.info(f"\n   Бот ответил пользователю {mes.chat.id}\n"
                 f"   Id сообщения: {mes.message_id}\n"
                 f"   Текст сообщения: {mes.text}\n")
    return mes


async def send_last_message(chat_id, text, keyboard=None):
    await delete_last_message(chat_id)
    mes = await send_message(chat_id, text, keyboard)
    last_message[chat_id] = mes.message_id
    return mes


async def delete_last_message(chat_id):
    if chat_id in last_message:
        try:
            await bot.delete_message(chat_id, last_message[chat_id])
            del (last_message[chat_id])
        except Exception as e:
            logging.error(f"delete_last_message {chat_id} {last_message[chat_id]}", exc_info=True)


async def change_message(chat_id, mes_id, text, keyboard=None, caption=False):
    try:
        if caption:
            mes = await bot.edit_message_caption(chat_id, mes_id, caption=text, reply_markup=keyboard)
            logging.info(f"\n   Бот меняет сообщение пользователя {mes.chat.id}\n"
                         f"   Id сообщения: {mes.message_id}\n"
                         f"   Текст сообщения: {mes.text}\n")

        else:
            mes = await bot.edit_message_text(text, chat_id, mes_id, reply_markup=keyboard)
            logging.info(f"\n   Бот меняет сообщение пользователя {mes.chat.id}\n"
                         f"   Id сообщения: {mes.message_id}\n"
                         f"   Текст сообщения: {mes.text}\n")
    except Exception as e:
        if e.args[0] == ("Message is not modified: specified new message content and reply "
                         "markup are exactly the same as a current content and reply markup of the message"):
            return
        else:
            logging.error(f"change_message", exc_info=True)


async def send_payment_to_user(data, creator):
    await delete_last_message(creator)
    facility_id = data["facility_id"]
    amount = data["amount"]
    date = data["date"]
    purpose_id = None
    if "purpose_id" in data:
        purpose_id = data["purpose_id"]
    user_id = None
    if "user_name" in data:
        secret_key = await create_secret_key()
        data["user_id"] = await insert_user(data["user_name"], secret_key)
    if "user_id" in data:
        user_id = data["user_id"]
        await update_user_balance(user_id, amount)
    comment = None
    if "comment" in data:
        comment = data["comment"]
    payment_id = await insert_payment(creator, facility_id, amount, date, purpose_id, user_id, comment)

    payment = await get_payment(payment_id)
    text = "\nКомпания: " + str(payment["company"])
    text += "\nОбъект: " + str(payment["facility"])
    text += "\nСумма: " + str(payment["amount"])
    text += "\nДата: " + str(payment["date"].strftime("%d.%m.%Y"))
    if payment["purpose_type"]:
        text += f"\nНазначение: {payment['purpose_type']} {payment['purpose_name']}"
    if payment["user_name"]:
        text += "\nФИО: " + str(payment["user_name"])
    if payment["comment"]:
        text += "\nКомментарий: " + str(payment["comment"])
    mes = await bot.send_message(creator, text)
    logging.info(f"\n   Бот ответил пользователю {mes.chat.id}\n"
                 f"   Id сообщения: {mes.message_id}\n"
                 f"   Текст сообщения: {mes.text}\n")


async def create_excel_for_all(date_from, date_to):
    payments = await get_all_payments_in_interval(date_from, date_to)
    wb = openpyxl.Workbook()
    list = wb.active
    list.append(["Компания", "Объект", "Сумма"])

    company = ""
    company_amount = 0

    for payment in payments:
        if company != "" and company != payment["company"]:
            list.append([None, "ИТОГО", company_amount])
            list.append([None])
            amount = 0
        elif company != "":
            payment["company"] = ""
        else:
            company = payment["company"]
        list.append([payment["company"], payment["facility"], payment["amount"]])
        company_amount += payment["amount"]
    list.append([None, "ИТОГО", company_amount])
    wb.active = await excel_column_width(list)
    wb.save("Платежи.xlsx")
    return "Платежи"


async def create_excel(payments, name):
    wb = openpyxl.Workbook()
    list = wb.active
    list.append(["Компания", "Объект", "Создатель", "Сумма", "Дата", "Назначение", "Тип документа", "ФИО", "Комментарий"])

    # company = ""
    # facility = ""
    # company_amount = 0
    # facility_amount = 0
    #
    # for payment in payments:
    #     if facility != "" and facility != payment["facility"]:
    #         list.append([None, None, None, None, None, "ИТОГО ПО ОБЪЕКТУ", facility_amount])
    #         list.append([None])
    #         facility = payment["facility"]
    #         company_amount += facility_amount
    #         facility_amount = 0
    #     elif facility != "":
    #         payment["facility"] = ""
    #     else:
    #         facility = payment["facility"]
    #     if company != "" and company != payment["company"]:
    #         list.append([None, None, None, None, None, "ИТОГО ПО КОМПАНИИ", company_amount])
    #         list.append([None])
    #         company = payment["company"]
    #         company_amount = 0
    #     elif company != "":
    #         payment["company"] = ""
    #     else:
    #         company = payment["company"]
    #     if payment["spent_for"] is None:
    #         payment["spent_for"] = payment["user_name"]
    #     list.append([payment["payment_id"], payment["company"], payment["facility"], payment["creator"],
    #                  payment["date"], payment["spent_for"], payment["amount"], payment["comment"]])
    #     facility_amount += payment["amount"]
    # company_amount += facility_amount
    # list.append([None, None, None, None, None, "ИТОГО ПО ОБЪЕКТУ", facility_amount])
    # list.append([None])
    # list.append([None, None, None, None, None, "ИТОГО ПО КОМПАНИИ", company_amount])

    for payment in payments:
        list.append([payment["company"], payment["facility"], payment["creator"], payment["amount"], payment["date"],
                     payment["purpose"], payment["type"], payment["user_name"], payment["comment"]])

    wb.active = await excel_column_width(list)
    wb.save(f"{name}.xlsx")


async def excel_column_width(worksheet):
    for col in worksheet.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        worksheet.column_dimensions[column].width = adjusted_width
    return worksheet


async def create_secret_key():
    while True:
        secret_key = token_urlsafe(16)
        if await get_secret_key(secret_key) is None:
            return secret_key
