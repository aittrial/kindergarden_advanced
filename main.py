import streamlit as st
import database
import os
from database import engine, Base
import models

# Эта строка автоматически создаст таблицы в любой подключенной базе
Base.metadata.create_all(bind=engine)

st.set_page_config(
    page_title="Kindergarten Management System",
    page_icon="🏫",
    layout="wide"
)

# Initialize database
try:
    database.init_db()
except Exception as e:
    st.error(f"Ошибка инициализации базы данных: {e}")

st.title("Kindergarten Management System (KMS) 🏫")
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
    
st.divider()
st.caption("Разработано для эффективного управления частным детским садом.")
