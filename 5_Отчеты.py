import streamlit as st
import pandas as pd
from io import BytesIO
import datetime
import sys
from pathlib import Path

# Ensure root directory is in path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from crud import get_all_children, get_all_attendance, get_product_inventory, get_all_expenses

st.set_page_config(page_title="Отчеты", page_icon="📊", layout="wide")
st.title("Отчеты и аналитика 📊")

def to_excel(df_dict):
    """Utility to convert a dictionary of DataFrames to an Excel file with multiple sheets."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, index=False, sheet_name=sheet_name)
    processed_data = output.getvalue()
    return processed_data

st.markdown("Здесь вы можете просмотреть агрегированную информацию и **скачать отчеты в формате Excel** прямо на свой компьютер.")

tab_summary, tab_children, tab_att, tab_prod, tab_fin = st.tabs([
    "📈 Главная сводка", 
    "👦 Дети", 
    "📅 Посещаемость", 
    "🍎 Продукты", 
    "💰 Финансы"
])

# SUMMARY TAB
with tab_summary:
    st.subheader("Краткая сводка детского сада")
    
    col1, col2, col3, col4 = st.columns(4)
    
    c_list = get_all_children()
    active_count = len([c for c in c_list if c['status'] == 'активный']) if c_list else 0
    col1.metric("Активных детей", active_count)
    
    a_list = get_all_attendance()
    today = datetime.date.today().strftime('%Y-%m-%d')
    today_att = len([a for a in a_list if a['date'] == today and a['status'] == 'присутствовал']) if a_list else 0
    col2.metric("Присутствуют сегодня", today_att)
    
    p_inv = get_product_inventory()
    low_stock = len([p for p in p_inv if p['is_low_stock']]) if p_inv else 0
    col3.metric("Продуктов (мало на складе)", low_stock, delta=-low_stock if low_stock > 0 else 0, delta_color="inverse")
    
    e_list = get_all_expenses()
    total_exp = sum(e['amount'] for e in e_list) if e_list else 0.0
    col4.metric("Всего расходов (руб)", f"{total_exp:,.0f}".replace(',', ' '))

# CHILDREN TAB
with tab_children:
    st.subheader("Отчет по детям")
    children = get_all_children()
    if children:
        df = pd.DataFrame(children)
        df['birth_date'] = pd.to_datetime(df['birth_date'])
        df['Возраст'] = (pd.to_datetime('today') - df['birth_date']).dt.days // 365
        
        display_df = df[['id', 'last_name', 'first_name', 'Возраст', 'status', 'parent_name', 'parent_phone']].copy()
        display_df.columns = ['ID', 'Фамилия', 'Имя', 'Возраст', 'Статус', 'Родитель', 'Телефон']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        excel_data = to_excel({"Детки": display_df})
        st.download_button("📥 Скачать список детей (Excel)", data=excel_data, file_name='children_report.xlsx', type="primary")
    else:
        st.info("Нет данных по детям.")

# ATTENDANCE TAB
with tab_att:
    st.subheader("Отчет по посещаемости")
    att = get_all_attendance()
    if att:
        df = pd.DataFrame(att)
        
        # Display raw journal
        st.write("**Журнал посещаемости:**")
        display_df = df[['date', 'last_name', 'first_name', 'status']].copy()
        display_df.columns = ['Дата', 'Фамилия', 'Имя', 'Статус']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Pivot table
        st.write("**Сводка посещений по каждому ребенку (все время):**")
        pivot_df = pd.pivot_table(df, values='id', index=['last_name', 'first_name'], columns='status', aggfunc='count', fill_value=0)
        st.dataframe(pivot_df, use_container_width=True)
        
        excel_data = to_excel({"Журнал": display_df, "Сводка": pivot_df.reset_index()})
        st.download_button("📥 Скачать отчет (Excel)", data=excel_data, file_name='attendance_report.xlsx', type="primary")
    else:
        st.info("Нет данных посещаемости.")

# PRODUCTS TAB
with tab_prod:
    st.subheader("Складской отчет (Остатки продуктов)")
    inv = get_product_inventory()
    if inv:
        df = pd.DataFrame(inv)
        
        display_df = df[['name', 'unit', 'current_stock', 'min_stock', 'total_income', 'total_expense']].copy()
        display_df.columns = ['Название', 'Ед. изм.', 'Текущий остаток', 'Мин. остаток', 'Приход (всего)', 'Расход (всего)']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        excel_data = to_excel({"Остатки Склада": display_df})
        st.download_button("📥 Скачать отчет по складу (Excel)", data=excel_data, file_name='inventory_report.xlsx', type="primary")
    else:
        st.info("Склад пуст.")

# FINANCE TAB
with tab_fin:
    st.subheader("Финансовый отчет")
    exp = get_all_expenses()
    if exp:
        df = pd.DataFrame(exp)
        
        # Group by category
        cat_sum = df.groupby('category')['amount'].sum().reset_index()
        cat_sum.columns = ['Категория', 'Сумма (руб)']
        
        # Two columns for better layout
        col_c1, col_c2 = st.columns([1, 2])
        with col_c1:
            st.write("**Сумма по категориям:**")
            st.dataframe(cat_sum, use_container_width=True, hide_index=True)
        with col_c2:
            st.write("**Все записи расходов:**")
            display_df = df[['date', 'category', 'description', 'amount']].copy()
            display_df.columns = ['Дата', 'Категория', 'Описание', 'Сумма (руб)']
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        excel_data = to_excel({"Все расходы": display_df, "По категориям": cat_sum})
        st.download_button("📥 Скачать финансовый отчет (Excel)", data=excel_data, file_name='expenses_report.xlsx', type="primary")
    else:
        st.info("Нет записей о расходах.")
