from postgres_queries import *


async def get_admin(user_id):
    admin = await postgres_select_one("SELECT * FROM admins WHERE user_id = %s AND send_cash_expenses = true;",
                                      (user_id,))
    return admin


async def insert_user(name, secret_key):
    await postgres_do_query("INSERT INTO users (name, balance, secret_key) VALUES (%s, 0, %s);",
                            (name, secret_key,))


async def update_user_user_id(user_id, secret_key):
    await postgres_do_query("UPDATE users SET user_id = %s WHERE secret_key = %s;",
                            (user_id, secret_key,))


async def update_user_name(user_id, name):
    await postgres_do_query("UPDATE users SET name = %s WHERE user_id = %s;",
                            (name, user_id,))


async def update_user_balance_by_user_id(user_id, balance):
    await postgres_do_query("UPDATE users SET balance = balance + %s WHERE user_id = %s;",
                            (balance, user_id,))


async def update_user_balance_by_name(name, balance):
    await postgres_do_query("UPDATE users SET balance = balance + %s WHERE name = %s;",
                            (balance, name,))


async def get_secret_key(secret_key):
    return await postgres_select_one("SELECT * FROM users WHERE secret_key = %s;",
                                     (secret_key,))


async def get_user_by_user_id(user_id):
    return await postgres_select_one("SELECT * FROM users WHERE user_id = %s;",
                                     (user_id,))


async def get_user_by_user_name(user_name):
    return await postgres_select_one("SELECT * FROM users WHERE name = %s;",
                                     (user_name,))


async def get_all_users_id():
    return await postgres_select_all("SELECT * FROM users;", None)


async def insert_company(name):
    await postgres_do_query("INSERT INTO companies (name, status) VALUES (%s, true);",
                            (name,))


async def update_company_name(company_id, name):
    await postgres_do_query("UPDATE companies SET name = %s WHERE company_id = %s;",
                            (name, company_id,))


async def update_company_status(company_id):
    await postgres_do_query("UPDATE companies SET status = not status WHERE company_id = %s;",
                            (company_id,))


async def update_company_delete(company_id):
    await postgres_do_query("UPDATE companies SET status = null WHERE company_id = %s;",
                            (company_id,))


async def get_company(company_id):
    return await postgres_select_one("SELECT * FROM companies WHERE company_id = %s;",
                                     (company_id,))


async def get_companies_by_status(status):
    if status == "active":
        status = True
    elif status == "close":
        status = False
    if type(status) == bool:
        return await postgres_select_all("SELECT * FROM companies WHERE status = %s ORDER BY name;",
                                         (status,))
    else:
        return await postgres_select_all("SELECT * FROM companies WHERE status IS NOT NULL "
                                         "ORDER BY status DESC, name;",
                                         None)


async def insert_object(name, company_id):
    await postgres_do_query("INSERT INTO objects (name, status, company_id) VALUES (%s, true, %s);",
                            (name, company_id,))


async def update_object_name(object_id, name):
    await postgres_do_query("UPDATE objects SET name = %s WHERE object_id = %s;",
                            (name, object_id,))


async def update_object_status(object_id):
    await postgres_do_query(f"UPDATE objects SET status = not status WHERE object_id = %s;",
                            (object_id,))


async def update_object_delete(object_id):
    await postgres_do_query("UPDATE objects SET status = null WHERE object_id = %s;",
                            (object_id,))


async def get_object(object_id):
    return await postgres_select_one("SELECT * FROM objects WHERE object_id = %s;",
                                     (object_id,))


async def get_objects_by_status(status, company_id):
    if status == "active":
        status = True
    elif status == "close":
        status = False
    if type(status) == bool:
        return await postgres_select_all("SELECT * FROM objects WHERE status = %s and company_id = %s "
                                         "ORDER BY name;",
                                         (status, company_id,))
    else:
        return await postgres_select_all("SELECT * FROM objects WHERE company_id = %s "
                                         "AND status IS NOT NULL ORDER BY status DESC, name;",
                                         (company_id,))


async def get_purpose_types():
    types = await postgres_select_all("SELECT DISTINCT type FROM purpose ORDER BY type;",
                                      None)
    return types


async def get_purposes(purpose_type):
    purposes = await postgres_select_all("SELECT * FROM purpose WHERE type = %s ORDER BY name;",
                                         (purpose_type,))
    return purposes


async def get_purpose(purpose_id):
    purpose = await postgres_select_one("SELECT * FROM purpose WHERE id = %s;",
                                        (purpose_id,))
    return purpose


async def insert_payment(creator, object_id, amount, date, purpose_id, user_name, comment):
    data = await postgres_select_one("INSERT INTO payments (creator, object_id, amount, date, purpose_id, user_name, comment) "
                                     "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING payment_id;",
                                     (creator, object_id, amount, date, purpose_id, user_name, comment,))
    return data["payment_id"]


async def get_payment(payment_id):
    return await postgres_select_one("SELECT payment_id, admins.name as creator, companies.name as company, "
                                     "objects.name as object, amount, date, purpose.type as purpose_type, purpose.name as purpose_name, user_name, comment "
                                     "FROM payments, objects, companies, admins, purpose WHERE payment_id = %s  "
                                     "AND payments.object_id = objects.object_id "
                                     "AND objects.company_id = companies.company_id "
                                     "AND payments.creator = admins.user_id "
                                     "AND payments.purpose_id = purpose.id;",
                                     (payment_id,))


async def get_company_payments_in_interval(date_from, date_to, company_id):
    return await postgres_select_all("SELECT payments.payment_id, companies.name AS company, "
                                     "objects.name AS object, admins.name AS creator, payments.date, payments.spent_for, "
                                     "payments.user_name, payments.amount, payments.comment "
                                     "FROM companies, objects, payments, admins "
                                     "WHERE companies.company_id = objects.company_id AND "
                                     "payments.object_id = objects.object_id AND payments.creator = admins.user_id "
                                     "AND date >= %s AND date <= %s AND companies.company_id = %s "
                                     "ORDER BY company, object, date, payments.creator, payment_id;",
                                     (date_from, date_to, company_id,))


async def get_object_payments_in_interval(date_from, date_to, object_id):
    return await postgres_select_all("SELECT payments.payment_id, companies.name AS company, "
                                     "objects.name AS object, admins.name AS creator, payments.date, payments.spent_for, "
                                     "payments.user_name, payments.amount, payments.comment "
                                     "FROM companies, objects, payments, admins "
                                     "WHERE companies.company_id = objects.company_id AND "
                                     "payments.object_id = objects.object_id AND payments.creator = admins.user_id "
                                     "AND date >= %s AND date <= %s AND objects.object_id = %s "
                                     "ORDER BY company, object, date, payments.creator, payment_id;",
                                     (date_from, date_to, object_id,))


async def get_all_payments_in_interval(date_from, date_to):
    return await postgres_select_all("SELECT DISTINCT companies.name AS company, objects.name AS object, "
                                     "SUM(payments.amount) AS amount FROM companies, objects, payments "
                                     "WHERE companies.company_id = objects.company_id AND "
                                     "payments.object_id = objects.object_id AND date >= %s AND date <= %s "
                                     "GROUP BY company, object;",
                                     (date_from, date_to,))

