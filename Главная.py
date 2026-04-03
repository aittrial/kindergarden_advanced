import streamlit as st
import database
from database import engine, Base
import models
from auth import hash_password, verify_password
from crud import get_user_by_email, create_user, superadmin_exists

# Create all tables (including users)
Base.metadata.create_all(bind=engine)

st.set_page_config(
    page_title="Kindergarten Management System",
    page_icon="🏫",
    layout="wide"
)

# --- Session state init ---
if "user" not in st.session_state:
    st.session_state.user = None  # None = not logged in


def logout():
    st.session_state.user = None
    st.rerun()


def login_page():
    st.title("Kindergarten Management System 🏫")

    no_superadmin = not superadmin_exists()

    if no_superadmin:
        tab_login, tab_signup = st.tabs(["🔑 Войти", "🆕 Регистрация Superadmin"])
    else:
        (tab_login,) = st.tabs(["🔑 Войти"])
        tab_signup = None

    with tab_login:
        st.subheader("Вход в систему")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            submitted = st.form_submit_button("Войти", type="primary")

        if submitted:
            if not email or not password:
                st.error("Введите email и пароль")
            else:
                user = get_user_by_email(email.strip().lower())
                if user and verify_password(password, user.password_hash):
                    st.session_state.user = {"email": user.email, "role": user.role}
                    st.rerun()
                else:
                    st.error("Неверный email или пароль")

    if tab_signup is not None:
        with tab_signup:
            st.subheader("Создать аккаунт Superadmin")
            st.info("Superadmin создаётся только один раз — пока ни одного нет в системе.")
            with st.form("signup_form"):
                email = st.text_input("Email Superadmin")
                password = st.text_input("Пароль", type="password")
                password2 = st.text_input("Повторите пароль", type="password")
                submitted2 = st.form_submit_button("Создать Superadmin", type="primary")

            if submitted2:
                if not email or not password:
                    st.error("Заполните все поля")
                elif password != password2:
                    st.error("Пароли не совпадают")
                elif len(password) < 6:
                    st.error("Пароль должен быть минимум 6 символов")
                else:
                    ok = create_user(email.strip().lower(), hash_password(password), "superadmin")
                    if ok:
                        st.success("Superadmin создан! Войдите в систему.")
                    else:
                        st.error("Ошибка: такой email уже существует")


def main_page():
    user = st.session_state.user
    st.title("Kindergarten Management System (KMS) 🏫")

    with st.sidebar:
        st.markdown(f"**{user['email']}**")
        st.caption(f"Роль: {'Superadmin' if user['role'] == 'superadmin' else 'Admin'}")
        st.divider()
        if st.button("Выйти", use_container_width=True):
            logout()

    st.write("Добро пожаловать в систему учета деятельности частного детского сада!")
    st.info("Используйте меню слева для навигации по разделам:")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Основные разделы:
        - 👦 **Дети** – учет воспитанников, добавление и редактирование данных
        - 📅 **Посещаемость** – журнал присутствия детей
        """)
    with col2:
        st.markdown("""
        ### Склад и Финансы:
        - 🍎 **Продукты** – складской учет продуктов питания
        - 💰 **Расходы** – учет финансовых затрат
        - 📊 **Отчеты** – аналитика и выгрузка данных в Excel
        """)
        if user['role'] == 'superadmin':
            st.markdown("- 👤 **Управление админами** – добавление и удаление администраторов")

    st.divider()
    st.caption("Разработано для эффективного управления частным детским садом.")


# --- Router ---
if st.session_state.user is None:
    login_page()
else:
    main_page()
