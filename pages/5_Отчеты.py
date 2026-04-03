import streamlit as st
import pandas as pd
from io import BytesIO
import datetime
import sys
from pathlib import Path

# Добавляем путь для импортов
sys.path.append(str(Path(__file__).resolve().parent.parent))
from crud import get_all_children, get_all_attendance, get_product_inventory, get_all_expenses
from auth_guard import require_login, render_sidebar_user

st.set_page_config(page_title="Отчеты", page_icon="📊", layout="wide")
require_login()
render_sidebar_user()
st.title("Отчеты и аналитика 📊")

# Функция-конвертер для SQLAlchemy объектов
def to_dict_list(query_results):
    data = []
    if query_results:
        for item in query_results:
            try:
                if isinstance(item, dict):
                    data.append(item)
                else:
                    row = {col.name: getattr(item, col.name) for col in item.__table__.columns}
                    data.append(row)
            except: continue
    return data

def to_excel(df_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

tab_summary, tab_children, tab_att, tab_prod, tab_fin = st.tabs([
    "📈 Главная сводка", "👦 Дети", "📅 Посещаемость", "🍎 Продукты", "💰 Финансы"
])

# 1. ГЛАВНАЯ СВОДКА
with tab_summary:
    st.subheader("Краткая сводка")
    col1, col2, col3 = st.columns(3)
    
    children_count = len(to_dict_list(get_all_children()))
    expenses_total = sum(e.amount for e in get_all_expenses())
    
    col1.metric("Всего детей", children_count)
    col2.metric("Общие расходы", f"{expenses_total:,.2f} руб")
    col3.metric("Статус системы", "Online")

# 2. ДЕТИ
with tab_children:
    kids = to_dict_list(get_all_children())
    if kids:
        df_kids = pd.DataFrame(kids)
        st.dataframe(df_kids, use_container_width=True)
        st.download_button("Скачать список детей", to_excel({"Дети": df_kids}), "children.xlsx")

# 3. ПОСЕЩАЕМОСТЬ
with tab_att:
    att = get_all_attendance() # Эта функция в crud уже возвращает список словарей
    if att:
        df_att = pd.DataFrame(att)
        st.dataframe(df_att, use_container_width=True)
        st.download_button("Скачать журнал", to_excel({"Посещаемость": df_att}), "attendance.xlsx")

# 4. ПРОДУКТЫ
with tab_prod:
    st.subheader("Отчет по складу")
    inv = get_product_inventory() # Вызов БЕЗ db
    if inv:
        df_inv = pd.DataFrame(inv)
        st.dataframe(df_inv, use_container_width=True)
        st.download_button("Скачать остатки", to_excel({"Склад": df_inv}), "inventory.xlsx")

# 5. ФИНАНСЫ
with tab_fin:
    st.subheader("Финансовый отчет")
    exp = to_dict_list(get_all_expenses())
    if exp:
        df_exp = pd.DataFrame(exp)
        st.dataframe(df_exp, use_container_width=True)
        st.download_button("Скачать расходы", to_excel({"Расходы": df_exp}), "expenses.xlsx")
