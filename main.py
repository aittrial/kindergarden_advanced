import streamlit as st
import database
from database import engine, Base, run_migrations
import models
from auth import hash_password, verify_password
from crud import (get_user_by_email, create_user, superadmin_exists,
                  update_user_preferences, get_debtors, get_product_inventory)
from i18n import t, CURRENCIES

Base.metadata.create_all(bind=engine)
run_migrations()

st.set_page_config(
    page_title="Kindergarten Management System",
    page_icon="🏫",
    layout="wide"
)

if "user" not in st.session_state:
    st.session_state.user = None
if "lang" not in st.session_state:
    st.session_state.lang = "ru"
if "currency" not in st.session_state:
    st.session_state.currency = "ILS"


def logout():
    st.session_state.user = None
    st.rerun()


def render_settings_sidebar(user):
    with st.sidebar:
        st.markdown(f"**{user['email']}**")
        role_label = t("superadmin") if user["role"] == "superadmin" else t("admin")
        st.caption(f"{t('role')}: {role_label}")
        st.divider()

        st.markdown(f"**{t('settings_header')}**")
        lang_options = ["ru", "en"]
        cur_lang = st.session_state.get("lang", "ru")
        new_lang = st.selectbox(
            t("language"),
            options=lang_options,
            format_func=lambda x: "Русский" if x == "ru" else "English",
            index=lang_options.index(cur_lang) if cur_lang in lang_options else 0,
            key="main_lang"
        )
        cur_keys = list(CURRENCIES.keys())
        cur_currency = st.session_state.get("currency", "ILS")
        cur_key = "name_ru" if cur_lang == "ru" else "name_en"
        new_currency = st.selectbox(
            t("currency"),
            options=cur_keys,
            format_func=lambda x: CURRENCIES[x][cur_key],
            index=cur_keys.index(cur_currency) if cur_currency in cur_keys else 0,
            key="main_currency"
        )
        if st.button(t("save"), key="save_prefs_main", use_container_width=True):
            st.session_state.lang = new_lang
            st.session_state.currency = new_currency
            update_user_preferences(user["email"], new_lang, new_currency)
            st.rerun()

        st.divider()
        if st.button(t("sign_out"), use_container_width=True):
            logout()


def login_page():
    col_lang, col_cur, _ = st.columns([1, 1, 4])
    with col_lang:
        lang = st.selectbox(
            "🌐",
            options=["ru", "en"],
            format_func=lambda x: "Русский" if x == "ru" else "English",
            index=0 if st.session_state.lang == "ru" else 1,
            key="pre_login_lang",
            label_visibility="collapsed"
        )
        if lang != st.session_state.lang:
            st.session_state.lang = lang
            st.rerun()
    with col_cur:
        cur_key = "name_ru" if st.session_state.lang == "ru" else "name_en"
        currency = st.selectbox(
            "💰",
            options=list(CURRENCIES.keys()),
            format_func=lambda x: CURRENCIES[x][cur_key],
            index=list(CURRENCIES.keys()).index(st.session_state.currency),
            key="pre_login_currency",
            label_visibility="collapsed"
        )
        if currency != st.session_state.currency:
            st.session_state.currency = currency
            st.rerun()

    st.title(f"{t('app_title')} 🏫")

    no_superadmin = not superadmin_exists()
    if no_superadmin:
        tab_login, tab_signup = st.tabs([t("login_tab"), t("register_tab")])
    else:
        (tab_login,) = st.tabs([t("login_tab")])
        tab_signup = None

    with tab_login:
        st.subheader(t("login_title"))
        with st.form("login_form"):
            email = st.text_input(t("email"))
            password = st.text_input(t("password"), type="password")
            submitted = st.form_submit_button(t("sign_in"), type="primary")

        if submitted:
            if not email or not password:
                st.error(t("fill_credentials"))
            else:
                user = get_user_by_email(email.strip().lower())
                if user and verify_password(password, user.password_hash):
                    st.session_state.user = {"email": user.email, "role": user.role}
                    st.session_state.lang = user.language or "ru"
                    st.session_state.currency = user.currency or "ILS"
                    st.rerun()
                else:
                    st.error(t("invalid_credentials"))

    if tab_signup is not None:
        with tab_signup:
            st.subheader(t("create_superadmin_title"))
            st.info(t("superadmin_info"))
            with st.form("signup_form"):
                email = st.text_input("Email Superadmin")
                password = st.text_input(t("password"), type="password")
                password2 = st.text_input(t("confirm_password"), type="password")
                submitted2 = st.form_submit_button(t("create_superadmin_btn"), type="primary")

            if submitted2:
                if not email or not password:
                    st.error(t("fill_all_fields"))
                elif password != password2:
                    st.error(t("passwords_mismatch"))
                elif len(password) < 6:
                    st.error(t("password_too_short"))
                else:
                    ok = create_user(email.strip().lower(), hash_password(password), "superadmin")
                    if ok:
                        st.success(t("superadmin_created"))
                    else:
                        st.error(t("email_exists"))


def main_page():
    user = st.session_state.user
    render_settings_sidebar(user)

    st.title(f"{t('app_title')} 🏫")

    # --- Alerts ---
    from datetime import date
    today = date.today()
    debtors = get_debtors(today.year, today.month)
    inventory = get_product_inventory()
    low_stock = [p for p in inventory if p["current_stock"] < p["min_stock"]]

    if debtors:
        st.warning(t("alert_debtors").format(n=len(debtors)))
    if low_stock:
        names = ", ".join(p["name"] for p in low_stock)
        st.warning(t("alert_low_stock").format(n=len(low_stock)) + f": {names}")

    st.write(t("welcome"))
    st.info(t("use_menu"))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(t("main_sections"))
        st.markdown(t("children_desc"))
        st.markdown(t("attendance_desc"))
    with col2:
        st.markdown(t("warehouse_finance"))
        st.markdown(t("products_desc"))
        st.markdown(t("expenses_desc"))
        st.markdown(t("reports_desc"))
        if user["role"] == "superadmin":
            st.markdown(t("admins_desc"))

    st.divider()
    st.caption(t("footer"))


# --- Build navigation with translated page titles ---
if st.session_state.user is not None:
    user = st.session_state.user
    home_page = st.Page(main_page, title=t("app_title"), icon="🏫", default=True)
    pages = [
        home_page,
        st.Page("pages/1_Дети.py", title=t("nav_children"), icon="👦"),
        st.Page("pages/2_Посещаемость.py", title=t("nav_attendance"), icon="📅"),
        st.Page("pages/3_Продукты.py", title=t("nav_products"), icon="🍎"),
        st.Page("pages/4_Расходы.py", title=t("nav_expenses"), icon="💰"),
        st.Page("pages/5_Отчеты.py", title=t("nav_reports"), icon="📊"),
        st.Page("pages/7_Оплата.py", title=t("nav_payments"), icon="💳"),
    ]
    if user["role"] == "superadmin":
        pages.append(st.Page("pages/6_Админы.py", title=t("nav_admins"), icon="👤"))

    pg = st.navigation(pages)
    pg.run()
else:
    # No navigation when not logged in
    st.navigation([st.Page(login_page, title="Login", icon="🔑", default=True)]).run()
