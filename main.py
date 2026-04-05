import streamlit as st
import database
from database import engine, Base
import models
from auth import hash_password, verify_password
from crud import (get_user_by_email, create_user, superadmin_exists,
                  update_user_preferences, get_debtors, get_product_inventory,
                  get_all_kindergartens)
from i18n import t, CURRENCIES

Base.metadata.create_all(bind=engine)

st.set_page_config(
    page_title="Kindergarten Management System",
    page_icon="🏫",
    layout="wide"
)

# Session state defaults
for key, val in [("user", None), ("lang", "ru"), ("currency", "ILS"),
                 ("active_kindergarten_id", None)]:
    if key not in st.session_state:
        st.session_state[key] = val


def logout():
    st.session_state.user = None
    st.session_state.active_kindergarten_id = None
    st.rerun()


def render_settings_sidebar(user):
    with st.sidebar:
        # Superadmin: show active kindergarten + back button
        if user["role"] == "superadmin":
            kg_id = st.session_state.get("active_kindergarten_id")
            if kg_id:
                from crud import get_kindergarten_by_id
                kg = get_kindergarten_by_id(kg_id)
                if kg:
                    st.markdown(f"🏫 **{kg.name}**")
                if st.button(t("back_to_list"), use_container_width=True, key="back_btn"):
                    st.session_state.active_kindergarten_id = None
                    st.rerun()
                st.divider()

        st.markdown(f"**{user['email']}**")
        role_label = t("superadmin") if user["role"] == "superadmin" else t("admin")
        st.caption(f"{t('role')}: {role_label}")
        st.divider()

        st.markdown(f"**{t('settings_header')}**")
        lang_options = ["ru", "en"]
        cur_lang = st.session_state.get("lang", "ru")
        new_lang = st.selectbox(
            t("language"), options=lang_options,
            format_func=lambda x: "Русский" if x == "ru" else "English",
            index=lang_options.index(cur_lang) if cur_lang in lang_options else 0,
            key="main_lang"
        )
        cur_keys = list(CURRENCIES.keys())
        cur_currency = st.session_state.get("currency", "ILS")
        cur_key = "name_ru" if cur_lang == "ru" else "name_en"
        new_currency = st.selectbox(
            t("currency"), options=cur_keys,
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
            "🌐", options=["ru", "en"],
            format_func=lambda x: "Русский" if x == "ru" else "English",
            index=0 if st.session_state.lang == "ru" else 1,
            key="pre_login_lang", label_visibility="collapsed"
        )
        if lang != st.session_state.lang:
            st.session_state.lang = lang
            st.rerun()
    with col_cur:
        cur_key = "name_ru" if st.session_state.lang == "ru" else "name_en"
        currency = st.selectbox(
            "💰", options=list(CURRENCIES.keys()),
            format_func=lambda x: CURRENCIES[x][cur_key],
            index=list(CURRENCIES.keys()).index(st.session_state.currency),
            key="pre_login_currency", label_visibility="collapsed"
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
                    st.session_state.user = {
                        "email": user.email, "role": user.role,
                        "kindergarten_id": user.kindergarten_id
                    }
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


def superadmin_home():
    """Superadmin sees list of kindergartens to choose from."""
    render_settings_sidebar(st.session_state.user)
    st.title(t("kindergartens_title"))
    kgs = get_all_kindergartens()

    if not kgs:
        st.info(t("no_kindergartens"))
        st.markdown("---")
        st.markdown(f"**{t('add_kindergarten_tab')}** — {t('nav_kindergartens')}")
    else:
        cols = st.columns(3)
        for i, kg in enumerate(kgs):
            with cols[i % 3]:
                with st.container(border=True):
                    if kg.logo_url:
                        st.image(kg.logo_url, width=60)
                    st.subheader(kg.name)
                    if kg.address:
                        st.caption(f"📍 {kg.address}")
                    if kg.phone:
                        st.caption(f"📞 {kg.phone}")
                    if st.button(t("enter_kindergarten"), key=f"enter_{kg.id}",
                                 type="primary", use_container_width=True):
                        st.session_state.active_kindergarten_id = kg.id
                        st.rerun()


def main_dashboard():
    """Dashboard shown inside a kindergarten context."""
    user = st.session_state.user
    render_settings_sidebar(user)

    from auth_guard import get_active_kindergarten_id
    from crud import get_kindergarten_by_id
    kg_id = get_active_kindergarten_id()
    kg = get_kindergarten_by_id(kg_id) if kg_id else None

    title = kg.name if kg else t("app_title")
    st.title(f"🏫 {title}")

    # Alerts
    from datetime import date
    today = date.today()
    debtors = get_debtors(kg_id, today.year, today.month)
    inventory = get_product_inventory(kg_id)
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
        st.markdown(t("payments_title"))
    st.divider()
    st.caption(t("footer"))


# ── ROUTING ──────────────────────────────────────────────────────────────────

if st.session_state.user is None:
    st.navigation([st.Page(login_page, title="Login", icon="🔑", default=True)]).run()

else:
    user = st.session_state.user
    is_super = user["role"] == "superadmin"
    kg_id = st.session_state.get("active_kindergarten_id") if is_super else user.get("kindergarten_id")
    in_kindergarten = kg_id is not None

    if is_super and not in_kindergarten:
        # Superadmin: kindergarten selection screen + management pages
        pages = [
            st.Page(superadmin_home, title=t("nav_kindergartens"), icon="🏫", default=True),
            st.Page("pages/kindergartens.py", title=t("kindergartens_title"), icon="⚙️"),
            st.Page("pages/6_Админы.py", title=t("nav_admins"), icon="👤"),
        ]
    else:
        # Admin or superadmin inside a kindergarten
        home_page = st.Page(main_dashboard, title=t("app_title"), icon="🏠", default=True)
        pages = [
            home_page,
            st.Page("pages/1_Дети.py", title=t("nav_children"), icon="👦"),
            st.Page("pages/2_Посещаемость.py", title=t("nav_attendance"), icon="📅"),
            st.Page("pages/3_Продукты.py", title=t("nav_products"), icon="🍎"),
            st.Page("pages/4_Расходы.py", title=t("nav_expenses"), icon="💰"),
            st.Page("pages/5_Отчеты.py", title=t("nav_reports"), icon="📊"),
            st.Page("pages/7_Оплата.py", title=t("nav_payments"), icon="💳"),
        ]
        if is_super:
            pages.append(st.Page("pages/6_Админы.py", title=t("nav_admins"), icon="👤"))

    st.navigation(pages).run()
