import streamlit as st
import pandas as pd
from datetime import date, datetime
import sys
from pathlib import Path

# Добавляем путь для импортов
sys.path.append(str(Path(__file__).resolve().parent.parent))
from crud import add_child, get_all_children, update_child, delete_child

st.set_page_config(page_title="Дети", page_icon="👦", layout="wide")
st.title("Учет детей 👦")

# Функция-конвертер (убирает ошибки PostgreSQL)
def to_dict_list(query_results):
    data = []
    if query_results:
        for item in query_results:
            try:
                row = {col.name: getattr(item, col.name) for col in item.__table__.columns}
                data.append(row)
            except Exception:
                continue
    return data

tab_list, tab_add = st.tabs(["📋 Список детей", "➕ Добавить ребенка"])

with tab_add:
    st.subheader("Новый ребенок")
    with st.form("add_child_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("Имя*")
            last_name = st.text_input("Фамилия*")
            birth_date = st.date_input("Дата рождения*", min_value=date(2010,1,1), max_value=date.today())
        with col2:
            parent_name = st.text_input("Имя родителя*")
            parent_phone = st.text_input("Телефон родителя")
            enrollment_date = st.date_input("Дата поступления*")
            
        status = st.selectbox("Статус", ["активный", "выбыл"])
        
        if st.form_submit_button("Добавить", type="primary"):
            if first_name and last_name and parent_name:
                # ВАЖНО: вызываем без db
                add_child(first_name, last_name, birth_date, parent_name, parent_phone, enrollment_date, status)
                st.success(f"Ребенок {first_name} добавлен!")
                st.rerun()
            else:
                st.error("Заполните обязательные поля")

with tab_list:
    st.subheader("Список всех детей")
    
    # ИСПРАВЛЕНИЕ ТУТ: вызываем без скобок (db)
    raw_children = get_all_children() 
    children = to_dict_list(raw_children)
    
    if children:
        df = pd.DataFrame(children)
        display_cols = ['id', 'last_name', 'first_name', 'birth_date', 'parent_name', 'status']
        existing = [c for c in display_cols if c in df.columns]
        st.dataframe(df[existing], use_container_width=True, hide_index=True)
        
        st.divider()
        selected_id = st.selectbox("Выберите ребенка для правки", 
                                   options=[c['id'] for c in children],
                                   format_func=lambda x: next(f"{c['last_name']} {c['first_name']}" for c in children if c['id'] == x))
        
        child = next((c for c in children if c['id'] == selected_id), None)
        if child:
            with st.form("edit_form"):
                fn = st.text_input("Имя", value=child.get('first_name', ''))
                ln = st.text_input("Фамилия", value=child.get('last_name', ''))
                
                # Защита даты
                bd = child.get('birth_date', date.today())
                if isinstance(bd, str): bd = datetime.strptime(bd.split()[0], '%Y-%m-%d').date()
                
                new_bd = st.date_input("Дата рождения", value=bd)
                
                if st.form_submit_button("Сохранить"):
                    update_child(selected_id, fn, ln, new_bd, child.get('parent_name'), child.get('parent_phone'), child.get('enrollment_date'), child.get('status'))
                    st.success("Обновлено")
                    st.rerun()
    else:
        st.info("Пока никого нет.")
