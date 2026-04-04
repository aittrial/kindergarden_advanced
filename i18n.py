import streamlit as st

TRANSLATIONS = {
    "ru": {
        "app_title": "Система управления детским садом",
        "sign_in": "Войти",
        "sign_out": "Выйти",
        "email": "Email",
        "password": "Пароль",
        "save": "Сохранить",
        "add": "Добавить",
        "delete": "Удалить",
        "role": "Роль",
        "superadmin": "Superadmin",
        "admin": "Admin",
        "language": "Язык",
        "currency": "Валюта",
        # Login
        "login_tab": "🔑 Войти",
        "register_tab": "🆕 Регистрация Superadmin",
        "login_title": "Вход в систему",
        "confirm_password": "Повторите пароль",
        "create_superadmin_btn": "Создать Superadmin",
        "create_superadmin_title": "Создать аккаунт Superadmin",
        "superadmin_info": "Superadmin создаётся только один раз — пока ни одного нет в системе.",
        "fill_credentials": "Введите email и пароль",
        "invalid_credentials": "Неверный email или пароль",
        "fill_all_fields": "Заполните все поля",
        "passwords_mismatch": "Пароли не совпадают",
        "password_too_short": "Пароль должен быть минимум 6 символов",
        "superadmin_created": "Superadmin создан! Войдите в систему.",
        "email_exists": "Ошибка: такой email уже существует",
        # Main dashboard
        "welcome": "Добро пожаловать в систему учета деятельности частного детского сада!",
        "use_menu": "Используйте меню слева для навигации по разделам:",
        "main_sections": "### Основные разделы:",
        "children_desc": "👦 **Дети** – учет воспитанников, добавление и редактирование данных",
        "attendance_desc": "📅 **Посещаемость** – журнал присутствия детей",
        "warehouse_finance": "### Склад и Финансы:",
        "products_desc": "🍎 **Продукты** – складской учет продуктов питания",
        "expenses_desc": "💰 **Расходы** – учет финансовых затрат",
        "reports_desc": "📊 **Отчеты** – аналитика и выгрузка данных в Excel",
        "admins_desc": "👤 **Управление админами** – добавление и удаление администраторов",
        "footer": "Разработано для эффективного управления частным детским садом.",
        # Navigation
        "nav_children": "Дети",
        "nav_attendance": "Посещаемость",
        "nav_products": "Продукты",
        "nav_expenses": "Расходы",
        "nav_reports": "Отчеты",
        "nav_admins": "Админы",
        # Sidebar settings
        "settings_header": "⚙️ Настройки",
        "preferences_saved": "Настройки сохранены",
        "login_required": "Пожалуйста, войдите в систему.",
        # Children page
        "children_title": "Учет детей 👦",
        "children_list_tab": "📋 Список детей",
        "add_child_tab": "➕ Добавить ребенка",
        "new_child": "Новый ребенок",
        "first_name": "Имя*",
        "last_name": "Фамилия*",
        "birth_date": "Дата рождения*",
        "parent_name": "Имя родителя*",
        "parent_phone": "Телефон родителя",
        "enrollment_date": "Дата поступления*",
        "status": "Статус",
        "add_btn": "Добавить",
        "child_added": "Ребенок {name} добавлен!",
        "fill_required": "Заполните обязательные поля",
        "all_children": "Список всех детей",
        "select_to_edit": "Выберите ребенка для правки",
        "first_name_field": "Имя",
        "last_name_field": "Фамилия",
        "birth_date_field": "Дата рождения",
        "save_btn": "Сохранить",
        "updated": "Обновлено",
        "no_children": "Пока никого нет.",
        # Attendance page
        "attendance_title": "Учет посещаемости 📅",
        "mark_tab": "📍 Отметить",
        "log_tab": "📖 Журнал",
        "date_label": "Дата",
        "att_status_label": "Статус",
        "save_att_btn": "Сохранить",
        "att_saved": "Готово!",
        # Products page
        "products_title": "Склад продуктов 🍎",
        "inventory_tab": "📦 Остатки",
        "income_tab": "📥 Приход",
        "expense_tab": "📤 Списание",
        "dict_tab": "📖 Справочник",
        "current_stock": "Текущие запасы",
        "product_label": "Продукт",
        "quantity_label": "Количество",
        "add_income_btn": "Добавить",
        "income_done": "Приход оформлен",
        "write_off_btn": "Списать",
        "written_off": "Списано",
        "nomenclature": "Номенклатура",
        "product_name_label": "Название",
        "unit_label": "Ед. изм.",
        "add_to_dict_btn": "Добавить в справочник",
        "warehouse_empty": "Склад пуст.",
        "receive_stock_header": "Пополнение склада",
        "write_off_header": "Расход продуктов",
        "col_id": "ID",
        "col_name": "Название",
        "col_unit": "Ед. изм.",
        "col_stock": "Остаток",
        "col_min_stock": "Мин. запас",
        # Expenses page
        "expenses_title": "💰 Учет финансовых расходов",
        "add_expense_tab": "➕ Добавить расход",
        "expense_list_tab": "📋 История расходов",
        "add_expense_header": "Добавить новую запись",
        "date_field": "Дата",
        "category_field": "Категория",
        "amount_field": "Сумма",
        "description_field": "Описание (на что потратили)",
        "comment_field": "Комментарий (необязательно)",
        "add_expense_btn": "Добавить расход",
        "expense_added": "Расход успешно добавлен!",
        "amount_positive": "Сумма должна быть больше нуля",
        "all_expenses_header": "Все финансовые расходы",
        "filter_category": "Фильтр по категориям",
        "filter_month": "Фильтр по месяцам",
        "select_delete_id": "Выберите ID для удаления",
        "delete_record_btn": "Удалить выбранную запись",
        "deleted_record": "Запись ID {id} удалена",
        "no_data": "Данных пока нет или они не соответствуют фильтрам.",
        # Reports page
        "reports_title": "Отчеты и аналитика 📊",
        "summary_tab": "📈 Главная сводка",
        "children_rep_tab": "👦 Дети",
        "att_rep_tab": "📅 Посещаемость",
        "products_rep_tab": "🍎 Продукты",
        "finance_rep_tab": "💰 Финансы",
        "summary_header": "Краткая сводка",
        "total_children": "Всего детей",
        "total_expenses": "Общие расходы",
        "system_status": "Статус системы",
        "online": "Online",
        "download_children": "Скачать список детей",
        "download_attendance": "Скачать журнал",
        "warehouse_report": "Отчет по складу",
        "download_inventory": "Скачать остатки",
        "finance_report": "Финансовый отчет",
        "download_expenses": "Скачать расходы",
        # Admins page
        "admins_title": "Управление администраторами 👤",
        "admins_list_tab": "📋 Список админов",
        "add_admin_tab": "➕ Добавить админа",
        "add_admin_header": "Добавить нового администратора",
        "new_admin_email": "Email нового администратора",
        "add_admin_btn": "Добавить",
        "access_denied": "Доступ запрещен. Только для Superadmin.",
        "current_admins": "Текущие администраторы",
        "no_admins": "Администраторов пока нет.",
        "admin_added": "Администратор {email} добавлен!",
        "admin_deleted": "Администратор {email} удален",
        "email_already_exists": "Пользователь с таким email уже существует",
        "error_creating_user": "Ошибка при создании пользователя",
    },
    "en": {
        "app_title": "Kindergarten Management System",
        "sign_in": "Sign In",
        "sign_out": "Sign Out",
        "email": "Email",
        "password": "Password",
        "save": "Save",
        "add": "Add",
        "delete": "Delete",
        "role": "Role",
        "superadmin": "Superadmin",
        "admin": "Admin",
        "language": "Language",
        "currency": "Currency",
        # Login
        "login_tab": "🔑 Sign In",
        "register_tab": "🆕 Register Superadmin",
        "login_title": "Sign In",
        "confirm_password": "Confirm password",
        "create_superadmin_btn": "Create Superadmin",
        "create_superadmin_title": "Create Superadmin Account",
        "superadmin_info": "Superadmin is created only once — while none exists in the system.",
        "fill_credentials": "Enter email and password",
        "invalid_credentials": "Invalid email or password",
        "fill_all_fields": "Fill in all fields",
        "passwords_mismatch": "Passwords do not match",
        "password_too_short": "Password must be at least 6 characters",
        "superadmin_created": "Superadmin created! Sign in.",
        "email_exists": "Error: this email already exists",
        # Main dashboard
        "welcome": "Welcome to the private kindergarten management system!",
        "use_menu": "Use the left menu to navigate sections:",
        "main_sections": "### Main Sections:",
        "children_desc": "👦 **Children** – manage students, add and edit records",
        "attendance_desc": "📅 **Attendance** – daily attendance journal",
        "warehouse_finance": "### Warehouse & Finance:",
        "products_desc": "🍎 **Products** – food inventory tracking",
        "expenses_desc": "💰 **Expenses** – financial expense tracking",
        "reports_desc": "📊 **Reports** – analytics and Excel export",
        "admins_desc": "👤 **Admin Management** – add and remove administrators",
        "footer": "Developed for effective management of a private kindergarten.",
        # Navigation
        "nav_children": "Children",
        "nav_attendance": "Attendance",
        "nav_products": "Products",
        "nav_expenses": "Expenses",
        "nav_reports": "Reports",
        "nav_admins": "Admins",
        # Sidebar settings
        "settings_header": "⚙️ Settings",
        "preferences_saved": "Settings saved",
        "login_required": "Please sign in.",
        # Children page
        "children_title": "Children Management 👦",
        "children_list_tab": "📋 Children List",
        "add_child_tab": "➕ Add Child",
        "new_child": "New Child",
        "first_name": "First Name*",
        "last_name": "Last Name*",
        "birth_date": "Date of Birth*",
        "parent_name": "Parent Name*",
        "parent_phone": "Parent Phone",
        "enrollment_date": "Enrollment Date*",
        "status": "Status",
        "add_btn": "Add",
        "child_added": "Child {name} added!",
        "fill_required": "Fill in required fields",
        "all_children": "All Children",
        "select_to_edit": "Select a child to edit",
        "first_name_field": "First Name",
        "last_name_field": "Last Name",
        "birth_date_field": "Date of Birth",
        "save_btn": "Save",
        "updated": "Updated",
        "no_children": "No children yet.",
        # Attendance page
        "attendance_title": "Attendance Tracking 📅",
        "mark_tab": "📍 Mark",
        "log_tab": "📖 Journal",
        "date_label": "Date",
        "att_status_label": "Status",
        "save_att_btn": "Save",
        "att_saved": "Done!",
        # Products page
        "products_title": "Product Warehouse 🍎",
        "inventory_tab": "📦 Stock",
        "income_tab": "📥 Receive",
        "expense_tab": "📤 Write-off",
        "dict_tab": "📖 Catalog",
        "current_stock": "Current Stock",
        "product_label": "Product",
        "quantity_label": "Quantity",
        "add_income_btn": "Add",
        "income_done": "Stock received",
        "write_off_btn": "Write Off",
        "written_off": "Written off",
        "nomenclature": "Nomenclature",
        "product_name_label": "Name",
        "unit_label": "Unit",
        "add_to_dict_btn": "Add to catalog",
        "warehouse_empty": "Warehouse is empty.",
        "receive_stock_header": "Receive Stock",
        "write_off_header": "Product Write-off",
        "col_id": "ID",
        "col_name": "Name",
        "col_unit": "Unit",
        "col_stock": "Stock",
        "col_min_stock": "Min Stock",
        # Expenses page
        "expenses_title": "💰 Financial Expenses",
        "add_expense_tab": "➕ Add Expense",
        "expense_list_tab": "📋 Expense History",
        "add_expense_header": "Add New Record",
        "date_field": "Date",
        "category_field": "Category",
        "amount_field": "Amount",
        "description_field": "Description (what was spent on)",
        "comment_field": "Comment (optional)",
        "add_expense_btn": "Add Expense",
        "expense_added": "Expense added successfully!",
        "amount_positive": "Amount must be greater than zero",
        "all_expenses_header": "All Financial Expenses",
        "filter_category": "Filter by category",
        "filter_month": "Filter by month",
        "select_delete_id": "Select ID to delete",
        "delete_record_btn": "Delete selected record",
        "deleted_record": "Record ID {id} deleted",
        "no_data": "No data yet or does not match filters.",
        # Reports page
        "reports_title": "Reports & Analytics 📊",
        "summary_tab": "📈 Summary",
        "children_rep_tab": "👦 Children",
        "att_rep_tab": "📅 Attendance",
        "products_rep_tab": "🍎 Products",
        "finance_rep_tab": "💰 Finance",
        "summary_header": "Quick Summary",
        "total_children": "Total Children",
        "total_expenses": "Total Expenses",
        "system_status": "System Status",
        "online": "Online",
        "download_children": "Download children list",
        "download_attendance": "Download journal",
        "warehouse_report": "Warehouse Report",
        "download_inventory": "Download stock",
        "finance_report": "Financial Report",
        "download_expenses": "Download expenses",
        # Admins page
        "admins_title": "Administrator Management 👤",
        "admins_list_tab": "📋 Admin List",
        "add_admin_tab": "➕ Add Admin",
        "add_admin_header": "Add New Administrator",
        "new_admin_email": "New administrator email",
        "add_admin_btn": "Add",
        "access_denied": "Access denied. Superadmin only.",
        "current_admins": "Current Administrators",
        "no_admins": "No administrators yet.",
        "admin_added": "Administrator {email} added!",
        "admin_deleted": "Administrator {email} deleted",
        "email_already_exists": "User with this email already exists",
        "error_creating_user": "Error creating user",
    }
}

CURRENCIES = {
    "ILS": {"symbol": "₪", "name_ru": "Шекели", "name_en": "Shekels"},
    "USD": {"symbol": "$", "name_ru": "Доллары", "name_en": "Dollars"},
    "EUR": {"symbol": "€", "name_ru": "Евро", "name_en": "Euros"},
}

# Internal DB values — always stored in Russian, translated for display
ATTENDANCE_STATUSES = ["присутствовал", "отсутствовал", "болел"]
ATTENDANCE_DISPLAY = {
    "ru": {"присутствовал": "присутствовал", "отсутствовал": "отсутствовал", "болел": "болел"},
    "en": {"присутствовал": "present", "отсутствовал": "absent", "болел": "sick"},
}

CHILD_STATUSES = ["активный", "выбыл"]
CHILD_STATUS_DISPLAY = {
    "ru": {"активный": "активный", "выбыл": "выбыл"},
    "en": {"активный": "active", "выбыл": "left"},
}

EXPENSE_CATEGORIES = ["Еда", "Транспорт", "Жилье", "Развлечения", "Связь", "Другое"]
EXPENSE_CATEGORY_DISPLAY = {
    "ru": {"Еда": "Еда", "Транспорт": "Транспорт", "Жилье": "Жилье",
           "Развлечения": "Развлечения", "Связь": "Связь", "Другое": "Другое"},
    "en": {"Еда": "Food", "Транспорт": "Transport", "Жилье": "Housing",
           "Развлечения": "Entertainment", "Связь": "Communication", "Другое": "Other"},
}

PRODUCT_UNITS = ["кг", "литры", "штуки"]
PRODUCT_UNIT_DISPLAY = {
    "ru": {"кг": "кг", "литры": "литры", "штуки": "штуки"},
    "en": {"кг": "kg", "литры": "liters", "штуки": "pieces"},
}


def get_lang():
    return st.session_state.get("lang", "ru")


def get_currency():
    return st.session_state.get("currency", "ILS")


def t(key):
    lang = get_lang()
    return TRANSLATIONS.get(lang, TRANSLATIONS["ru"]).get(key, key)


def currency_symbol():
    return CURRENCIES.get(get_currency(), CURRENCIES["ILS"])["symbol"]


def format_amount(amount):
    sym = currency_symbol()
    return f"{sym}{amount:,.2f}"


def att_display(status):
    lang = get_lang()
    return ATTENDANCE_DISPLAY.get(lang, ATTENDANCE_DISPLAY["ru"]).get(status, status)


def child_status_display(status):
    lang = get_lang()
    return CHILD_STATUS_DISPLAY.get(lang, CHILD_STATUS_DISPLAY["ru"]).get(status, status)


def expense_cat_display(cat):
    lang = get_lang()
    return EXPENSE_CATEGORY_DISPLAY.get(lang, EXPENSE_CATEGORY_DISPLAY["ru"]).get(cat, cat)


def unit_display(unit):
    lang = get_lang()
    return PRODUCT_UNIT_DISPLAY.get(lang, PRODUCT_UNIT_DISPLAY["ru"]).get(unit, unit)
