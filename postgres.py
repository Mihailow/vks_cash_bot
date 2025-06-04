from postgres_queries import *


async def get_admin(tg_id):
    admin = await postgres_select_one("SELECT * FROM admins WHERE tg_id = %s AND cash_bot IS NOT NULL;",
                                      (tg_id,))
    return admin


async def get_admins():
    admins = await postgres_select_all("SELECT * FROM admins WHERE cash_bot IS NOT NULL;",
                                       None)
    return admins



####################################################################


async def insert_user(name, secret_key):
    user_id = await postgres_select_one("INSERT INTO report_users (name, balance, secret_key, status) "
                                        "VALUES (%s, 0, %s, true) RETURNING user_id;",
                                        (name, secret_key,))
    return user_id["user_id"]


# async def update_user_name(user_id, name):
#     await postgres_do_query("UPDATE report_users SET name = %s WHERE user_id = %s;",
#                             (name, user_id,))


async def update_user_balance(user_id, balance):
    await postgres_do_query("UPDATE report_users SET balance = balance + %s WHERE user_id = %s;",
                            (balance, user_id,))


async def update_user_clear_balance(user_id):
    await postgres_do_query("UPDATE report_users SET balance = 0 WHERE user_id = %s;",
                            (user_id,))


async def update_user_delete(user_id):
    await postgres_do_query("UPDATE report_users SET status = null WHERE user_id = %s;",
                            (user_id,))


async def get_secret_key(secret_key):
    secret_key = await postgres_select_one("SELECT * FROM report_users WHERE secret_key = %s;",
                                           (secret_key,))
    return secret_key


async def get_user(user_id):
    user = await postgres_select_one("SELECT * FROM report_users WHERE user_id = %s;",
                                     (user_id,))
    return user


async def get_user_by_user_name(user_name):
    user = await postgres_select_one("SELECT * FROM report_users WHERE name = %s AND status IS NOT NULL;",
                                     (user_name,))
    return user


async def get_users_by_status(status):
    if status == "active":
        status = True
    elif status == "close":
        status = False
    if type(status) is bool:
        users = await postgres_select_all("SELECT * FROM report_users WHERE status = %s ORDER BY name;",
                                          (status,))
    else:
        users = await postgres_select_all("SELECT * FROM report_users WHERE status IS NOT NULL ORDER BY name;",
                                          None)
    return users


####################################################################


async def insert_company(name):
    await postgres_do_query("INSERT INTO companies (name, status) VALUES (%s, true);",
                            (name,))


# async def update_company_name(company_id, name):
#     await postgres_do_query("UPDATE companies SET name = %s WHERE company_id = %s;",
#                             (name, company_id,))


async def update_company_status(company_id):
    await postgres_do_query("UPDATE companies SET status = not status WHERE company_id = %s;",
                            (company_id,))


async def update_company_delete(company_id):
    await postgres_do_query("UPDATE companies SET status = null WHERE company_id = %s;",
                            (company_id,))


async def get_company(company_id):
    company = await postgres_select_one("SELECT * FROM companies WHERE company_id = %s;",
                                        (company_id,))
    return company


async def get_companies_by_status(status):
    if status == "active":
        status = True
    elif status == "close":
        status = False
    if type(status) is bool:
        companies = await postgres_select_all("SELECT * FROM companies WHERE status = %s ORDER BY name;",
                                              (status,))
    else:
        companies = await postgres_select_all("SELECT * FROM companies WHERE status IS NOT NULL "
                                              "ORDER BY status DESC, name;",
                                              None)
    return companies


async def get_company_by_name(name):
    company = await postgres_select_one("SELECT * FROM companies WHERE name = %s AND status IS NOT NULL;",
                                        (name,))
    return company


####################################################################


async def insert_facility(name, company_id):
    await postgres_do_query("INSERT INTO facilities (name, status, company_id) VALUES (%s, true, %s);",
                            (name, company_id,))


# async def update_facility_name(facility_id, name):
#     await postgres_do_query("UPDATE facilities SET name = %s WHERE facility_id = %s;",
#                             (name, facility_id,))


async def update_facility_status(facility_id):
    await postgres_do_query(f"UPDATE facilities SET status = not status WHERE facility_id = %s;",
                            (facility_id,))


async def update_facility_delete(facility_id):
    await postgres_do_query("UPDATE facilities SET status = null WHERE facility_id = %s;",
                            (facility_id,))


async def get_facility(facility_id):
    facility = await postgres_select_one("SELECT * FROM facilities WHERE facility_id = %s;",
                                         (facility_id,))
    return facility


async def get_facility_by_name(name, company_id):
    facility = await postgres_select_one("SELECT * FROM facilities WHERE name = %s AND company_id = %s "
                                         "AND status IS NOT NULL;",
                                         (name, company_id,))
    return facility


async def get_facilities_by_status(status, company_id):
    if status == "active":
        status = True
    elif status == "close":
        status = False
    if type(status) is bool:
        facilities = await postgres_select_all("SELECT * FROM facilities WHERE status = %s and company_id = %s "
                                               "ORDER BY name;",
                                               (status, company_id,))
    else:
        facilities = await postgres_select_all("SELECT * FROM facilities WHERE company_id = %s "
                                               "AND status IS NOT NULL ORDER BY status DESC, name;",
                                               (company_id,))
    return facilities


####################################################################


async def insert_purpose_type(name):
    await postgres_do_query("INSERT INTO cash_payment_purpose_types (name, status) VALUES (%s, true);",
                            (name,))


async def update_purpose_type_status(type_id):
    await postgres_do_query("UPDATE cash_payment_purpose_types SET status = not status WHERE type_id = %s;",
                            (type_id,))


async def update_purpose_type_delete(type_id):
    await postgres_do_query("UPDATE cash_payment_purpose_types SET status = null WHERE type_id = %s;",
                            (type_id,))


async def get_purpose_type(type_id):
    purpose_type = await postgres_select_one("SELECT * FROM cash_payment_purpose_types WHERE type_id = %s;",
                                        (type_id,))
    return purpose_type


async def get_purpose_types_by_status(status):
    if status == "active":
        status = True
    elif status == "close":
        status = False
    if type(status) is bool:
        types = await postgres_select_all("SELECT * FROM cash_payment_purpose_types "
                                          "WHERE status = %s ORDER BY name;",
                                          (status,))
    else:
        types = await postgres_select_all("SELECT * FROM cash_payment_purpose_types "
                                          "WHERE status IS NOT NULL ORDER BY status DESC, name;",
                                          None)
    return types


async def get_purpose_type_by_name(name):
    purpose_type = await postgres_select_one("SELECT * FROM cash_payment_purpose_types "
                                             "WHERE name = %s AND status IS NOT NULL;",
                                             (name,))
    return purpose_type


####################################################################


async def insert_purpose(name, type_id):
    await postgres_do_query("INSERT INTO cash_payment_purposes (name, type, status) VALUES (%s, %s, true);",
                            (name, type_id,))


async def update_purpose_status(purpose_id):
    await postgres_do_query("UPDATE cash_payment_purposes SET status = not status WHERE purpose_id = %s;",
                            (purpose_id,))


async def update_purpose_delete(purpose_id):
    await postgres_do_query("UPDATE cash_payment_purposes SET status = null WHERE purpose_id = %s;",
                            (purpose_id,))


async def get_purpose(purpose_id):
    purpose = await postgres_select_one("SELECT * FROM cash_payment_purposes WHERE purpose_id = %s;",
                                        (purpose_id,))
    return purpose


async def get_purposes_by_status(status, purpose_type):
    if status == "active":
        status = True
    elif status == "close":
        status = False
    if type(status) is bool:
        purposes = await postgres_select_all("SELECT * FROM cash_payment_purposes "
                                             "WHERE type = %s AND status = %s ORDER BY name;",
                                             (purpose_type, status))
    else:
        purposes = await postgres_select_all("SELECT * FROM cash_payment_purposes WHERE type = %s "
                                             "AND status IS NOT NULL ORDER BY status DESC, name;",
                                             (purpose_type,))
    return purposes


async def get_purpose_by_name(name, type_id):
    purpose = await postgres_select_one("SELECT * FROM cash_payment_purposes WHERE name = %s AND type = %s "
                                        "AND status IS NOT NULL;",
                                        (name, type_id,))
    return purpose


####################################################################


async def insert_payment(creator, facility_id, amount, date, purpose_id, user_id, comment):
    data = await postgres_select_one("INSERT INTO cash_payments (creator, facility_id, amount, date, purpose_id, "
                                     "user_id, comment) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING payment_id;",
                                     (creator, facility_id, amount, date, purpose_id, user_id, comment,))
    return data["payment_id"]


async def get_payment(payment_id):
    payment = await postgres_select_one("SELECT companies.name AS company, facilities.name AS facility, "
                                        "amount, date, cash_payment_purpose_types.name AS purpose_type, "
                                        "cash_payment_purposes.name AS purpose_name, report_users.name AS user_name, "
                                        "comment FROM cash_payments LEFT JOIN facilities ON cash_payments.facility_id "
                                        "= facilities.facility_id LEFT JOIN companies ON facilities.company_id = "
                                        "companies.company_id LEFT JOIN cash_payment_purposes ON "
                                        "cash_payments.purpose_id = cash_payment_purposes.purpose_id LEFT JOIN "
                                        "cash_payment_purpose_types ON cash_payment_purpose_types.type_id = "
                                        "cash_payment_purposes.type LEFT JOIN report_users ON cash_payments.user_id "
                                        "= report_users.user_id WHERE payment_id = %s;",
                                        (payment_id,))
    return payment


####################################################################


async def get_company_payments_in_interval(date_from, date_to, company_id):
    payments = await postgres_select_all("SELECT companies.name AS company, facilities.name AS facility, "
                                         "admins.name as creator, cash_payments.amount, cash_payments.date, "
                                         "CONCAT(cash_payment_purpose_types.name, ' ', "
                                         "cash_payment_purposes.name) AS purpose, '' AS type, "
                                         "report_users.name AS user_name, cash_payments.comment "
                                         "FROM cash_payments LEFT JOIN facilities ON cash_payments.facility_id "
                                         "= facilities.facility_id LEFT JOIN companies ON facilities.company_id "
                                         "= companies.company_id LEFT JOIN admins ON cash_payments.creator = "
                                         "admins.tg_id LEFT JOIN cash_payment_purposes ON "
                                         "cash_payments.purpose_id = cash_payment_purposes.purpose_id "
                                         "LEFT JOIN cash_payment_purpose_types ON "
                                         "cash_payment_purpose_types.type_id = cash_payment_purposes.type "
                                         "LEFT JOIN report_users ON cash_payments.user_id = report_users.user_id "
                                         "WHERE companies.company_id = %s AND cash_payments.date >= %s "
                                         "AND cash_payments.date <= %s UNION ALL SELECT companies.name "
                                         "AS company, facilities.name AS facility, report_users.name as creator, "
                                         "reports.amount, reports.date, '' AS purpose, CONCAT(reports.type, ' ', "
                                         "reports.upd_type) as type, '' AS user_name, reports.purpose AS comment "
                                         "FROM reports LEFT JOIN facilities ON reports.facility_id = "
                                         "facilities.facility_id LEFT JOIN companies ON facilities.company_id = "
                                         "companies.company_id LEFT JOIN report_users ON reports.user_id = "
                                         "report_users.user_id WHERE (reports.type = 'без чека' OR "
                                         "upd_type = 'ЭДО' OR received IS NOT NULL) AND companies.company_id = "
                                         "%s AND reports.date >= %s AND reports.date <= %s ORDER BY date, "
                                         "company, facility, creator;",
                                         (company_id, date_from, date_to, company_id, date_from, date_to,))
    return payments


async def get_facility_payments_in_interval(date_from, date_to, facility_id):
    payments = await postgres_select_all("SELECT companies.name AS company, facilities.name AS facility, "
                                                 "admins.name as creator, cash_payments.amount, cash_payments.date, "
                                                 "CONCAT(cash_payment_purpose_types.name, ' ', "
                                                 "cash_payment_purposes.name) AS purpose, '' AS type, "
                                                 "report_users.name AS user_name, cash_payments.comment "
                                                 "FROM cash_payments LEFT JOIN facilities ON cash_payments.facility_id "
                                                 "= facilities.facility_id LEFT JOIN companies ON facilities.company_id "
                                                 "= companies.company_id LEFT JOIN admins ON cash_payments.creator = "
                                                 "admins.tg_id LEFT JOIN cash_payment_purposes ON "
                                                 "cash_payments.purpose_id = cash_payment_purposes.purpose_id "
                                                 "LEFT JOIN cash_payment_purpose_types ON "
                                                 "cash_payment_purpose_types.type_id = cash_payment_purposes.type "
                                                 "LEFT JOIN report_users ON cash_payments.user_id = report_users.user_id "
                                                 "WHERE facilities.facility_id = %s AND cash_payments.date >= %s "
                                                 "AND cash_payments.date <= %s UNION ALL SELECT companies.name "
                                                 "AS company, facilities.name AS facility, report_users.name as creator, "
                                                 "reports.amount, reports.date, '' AS purpose, CONCAT(reports.type, ' ', "
                                                 "reports.upd_type) as type, '' AS user_name, reports.purpose AS comment "
                                                 "FROM reports LEFT JOIN facilities ON reports.facility_id = "
                                                 "facilities.facility_id LEFT JOIN companies ON facilities.company_id = "
                                                 "companies.company_id LEFT JOIN report_users ON reports.user_id = "
                                                 "report_users.user_id WHERE (reports.type = 'без чека' OR "
                                                 "upd_type = 'ЭДО' OR received IS NOT NULL) AND facilities.facility_id = "
                                                 "%s AND reports.date >= %s AND reports.date <= %s ORDER BY date, "
                                                  "company, facility, creator;",
                                                 (facility_id, date_from, date_to, facility_id, date_from, date_to,))
    return payments


async def get_purpose_types_payments_in_interval(date_from, date_to, type_id):
    payments = await postgres_select_all("SELECT companies.name AS company, facilities.name AS facility, "
                                                 "admins.name as creator, cash_payments.amount, cash_payments.date, "
                                                 "CONCAT(cash_payment_purpose_types.name, ' ', "
                                                 "cash_payment_purposes.name) AS purpose, '' AS type, "
                                                 "report_users.name AS user_name, cash_payments.comment "
                                                 "FROM cash_payments LEFT JOIN facilities ON cash_payments.facility_id "
                                                 "= facilities.facility_id LEFT JOIN companies ON facilities.company_id "
                                                 "= companies.company_id LEFT JOIN admins ON cash_payments.creator = "
                                                 "admins.tg_id LEFT JOIN cash_payment_purposes ON "
                                                 "cash_payments.purpose_id = cash_payment_purposes.purpose_id "
                                                 "LEFT JOIN cash_payment_purpose_types ON "
                                                 "cash_payment_purpose_types.type_id = cash_payment_purposes.type "
                                                 "LEFT JOIN report_users ON cash_payments.user_id = report_users.user_id "
                                                 "WHERE cash_payment_purpose_types.type_id = %s AND cash_payments.date >= %s "
                                                 "AND cash_payments.date <= %s ORDER BY date, company, facility, creator;",
                                                 (type_id, date_from, date_to,))
    return payments


async def get_purposes_payments_in_interval(date_from, date_to, purpose_id):
    payments = await postgres_select_all("SELECT companies.name AS company, facilities.name AS facility, "
                                                 "admins.name as creator, cash_payments.amount, cash_payments.date, "
                                                 "CONCAT(cash_payment_purpose_types.name, ' ', "
                                                 "cash_payment_purposes.name) AS purpose, '' AS type, "
                                                 "report_users.name AS user_name, cash_payments.comment "
                                                 "FROM cash_payments LEFT JOIN facilities ON cash_payments.facility_id "
                                                 "= facilities.facility_id LEFT JOIN companies ON facilities.company_id "
                                                 "= companies.company_id LEFT JOIN admins ON cash_payments.creator = "
                                                 "admins.tg_id LEFT JOIN cash_payment_purposes ON "
                                                 "cash_payments.purpose_id = cash_payment_purposes.purpose_id "
                                                 "LEFT JOIN cash_payment_purpose_types ON "
                                                 "cash_payment_purpose_types.type_id = cash_payment_purposes.type "
                                                 "LEFT JOIN report_users ON cash_payments.user_id = report_users.user_id "
                                                 "WHERE cash_payment_purposes.purpose_id = %s AND cash_payments.date >= %s "
                                                 "AND cash_payments.date <= %s ORDER BY date, company, facility, creator;",
                                                 (purpose_id, date_from, date_to,))
    return payments


async def get_user_payments_in_interval(date_from, date_to, user_id):
    payments = await postgres_select_all("SELECT companies.name AS company, facilities.name AS facility, "
                                                 "admins.name as creator, cash_payments.amount, cash_payments.date, "
                                                 "CONCAT(cash_payment_purpose_types.name, ' ', "
                                                 "cash_payment_purposes.name) AS purpose, '' AS type, "
                                                 "report_users.name AS user_name, cash_payments.comment "
                                                 "FROM cash_payments LEFT JOIN facilities ON cash_payments.facility_id "
                                                 "= facilities.facility_id LEFT JOIN companies ON facilities.company_id "
                                                 "= companies.company_id LEFT JOIN admins ON cash_payments.creator = "
                                                 "admins.tg_id LEFT JOIN cash_payment_purposes ON "
                                                 "cash_payments.purpose_id = cash_payment_purposes.purpose_id "
                                                 "LEFT JOIN cash_payment_purpose_types ON "
                                                 "cash_payment_purpose_types.type_id = cash_payment_purposes.type "
                                                 "LEFT JOIN report_users ON cash_payments.user_id = report_users.user_id "
                                                 "WHERE report_users.user_id = %s AND cash_payments.date >= %s "
                                                 "AND cash_payments.date <= %s UNION ALL SELECT companies.name "
                                                 "AS company, facilities.name AS facility, report_users.name as creator, "
                                                 "reports.amount, reports.date, '' AS purpose, CONCAT(reports.type, ' ', "
                                                 "reports.upd_type) as type, '' AS user_name, reports.purpose AS comment "
                                                 "FROM reports LEFT JOIN facilities ON reports.facility_id = "
                                                 "facilities.facility_id LEFT JOIN companies ON facilities.company_id = "
                                                 "companies.company_id LEFT JOIN report_users ON reports.user_id = "
                                                 "report_users.user_id WHERE (reports.type = 'без чека' OR "
                                                 "upd_type = 'ЭДО' OR received IS NOT NULL) AND report_users.user_id = "
                                                 "%s AND reports.date >= %s AND reports.date <= %s ORDER BY date, "
                                                  "company, facility, creator;",
                                                 (user_id, date_from, date_to, user_id, date_from, date_to,))
    return payments


async def get_creator_payments_in_interval(date_from, date_to, tg_id):

    payments = await postgres_select_all("SELECT companies.name AS company, facilities.name AS facility, "
                                                 "admins.name as creator, cash_payments.amount, cash_payments.date, "
                                                 "CONCAT(cash_payment_purpose_types.name, ' ', "
                                                 "cash_payment_purposes.name) AS purpose, '' AS type, "
                                                 "report_users.name AS user_name, cash_payments.comment "
                                                 "FROM cash_payments LEFT JOIN facilities ON cash_payments.facility_id "
                                                 "= facilities.facility_id LEFT JOIN companies ON facilities.company_id "
                                                 "= companies.company_id LEFT JOIN admins ON cash_payments.creator = "
                                                 "admins.tg_id LEFT JOIN cash_payment_purposes ON "
                                                 "cash_payments.purpose_id = cash_payment_purposes.purpose_id "
                                                 "LEFT JOIN cash_payment_purpose_types ON "
                                                 "cash_payment_purpose_types.type_id = cash_payment_purposes.type "
                                                 "LEFT JOIN report_users ON cash_payments.user_id = report_users.user_id "
                                                 "WHERE admins.tg_id = %s AND cash_payments.date >= %s "
                                                 "AND cash_payments.date <= %s ORDER BY date, company, facility, creator;",
                                                 (tg_id, date_from, date_to,))
    return payments


async def get_all_payments_in_interval(date_from, date_to):
    payments = await postgres_select_all("SELECT DISTINCT companies.name AS company, facilities.name AS facility, "
                                         "SUM(cash_payments.amount) AS amount FROM companies, facilities, cash_payments "
                                         "WHERE companies.company_id = facilities.company_id AND "
                                         "cash_payments.facility_id = facilities.facility_id AND date >= %s AND date <= %s "
                                         "GROUP BY company, facility;",
                                         (date_from, date_to,))
    return payments
