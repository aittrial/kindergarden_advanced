import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from auth_guard import require_login, render_sidebar_user, is_superadmin
from auth import hash_password
from crud import get_all_admins, create_user, delete_user_by_email, get_user_by_email

st.set_page_config(page_title="Управление админами", page_icon="👤", layout="wide")
require_login()
render_sidebar_user()

if not is_superadmin():
    st.error("Доступ запрещен. Только для Superadmin.")
    st.stop()

st.title("Управление администраторами 👤")

tab_list, tab_add = st.tabs(["📋 Список админов", "➕ Добавить админа"])

with tab_add:
    st.subheader("Добавить нового администратора")
    with st.form("add_admin_form", clear_on_submit=True):
        email = st.text_input("Email нового администратора")
        password = st.text_input("Пароль", type="password")
        password2 = st.text_input("Повторите пароль", type="password")
        submitted = st.form_submit_button("Добавить", type="primary")

    if submitted:
        if not email or not password:
            st.error("Заполните все поля")
        elif password != password2:
            st.error("Пароли не совпадают")
        elif len(password) < 6:
            st.error("Пароль должен быть минимум 6 символов")
        elif get_user_by_email(email.strip().lower()):
            st.error("Пользователь с таким email уже существует")
        else:
            ok = create_user(email.strip().lower(), hash_password(password), "admin")
            if ok:
                st.success(f"Администратор {email} добавлен!")
                st.rerun()
            else:
                st.error("Ошибка при создании пользователя")

with tab_list:
    st.subheader("Текущие администраторы")
    admins = get_all_admins()
    if admins:
        for admin in admins:
            col1, col2 = st.columns([4, 1])
            col1.write(admin.email)
            if col2.button("Удалить", key=f"del_{admin.id}", type="secondary"):
                delete_user_by_email(admin.email)
                st.success(f"Администратор {admin.email} удален")
                st.rerun()
    else:
        st.info("Администраторов пока нет.")
