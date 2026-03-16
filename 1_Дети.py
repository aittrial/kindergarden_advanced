import streamlit as st
import pandas as pd
from datetime import date
import datetime

# Ensure root directory is in path for imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from crud import add_child, get_all_children, update_child, delete_child

st.set_page_config(page_title="Дети", page_icon="👦", layout="wide")
st.title("Учет детей 👦")

tab_list, tab_add = st.tabs(["📋 Список детей", "➕ Добавить ребенка"])

with tab_add:
    st.subheader("Новый ребенок")
    with st.form("add_child_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("Имя*")
            last_name = st.text_input("Фамилия*")
            birth_date = st.date_input("Дата рождения*", min_value=date(2015,1,1), max_value=date.today())
        with col2:
            parent_name = st.text_input("Имя родителя*")
            parent_phone = st.text_input("Телефон родителя")
            enrollment_date = st.date_input("Дата поступления*")
            
        status = st.selectbox("Статус", ["активный", "выбыл"])
        
        submitted = st.form_submit_button("Добавить", type="primary")
        if submitted:
            if first_name and last_name and parent_name:
                add_child(first_name, last_name, birth_date, parent_name, parent_phone, enrollment_date, status)
                st.success(f"Ребенок {first_name} {last_name} успешно добавлен!")
                st.rerun()
            else:
                st.error("Пожалуйста, заполните обязательные поля (*)")

with tab_list:
    st.subheader("Все дети")
    children = get_all_children()
    if children:
        df = pd.DataFrame(children)
        
        # Calculate age
        df['birth_date'] = pd.to_datetime(df['birth_date'])
        # Current age in years
        df['Возраст'] = (pd.to_datetime('today') - df['birth_date']).dt.days // 365
        
        display_df = df[['id', 'last_name', 'first_name', 'Возраст', 'parent_name', 'parent_phone', 'status', 'enrollment_date']].copy()
        display_df.columns = ['ID', 'Фамилия', 'Имя', 'Возраст', 'Родитель', 'Телефон', 'Статус', 'Дата пост.']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("Редактирование / Удаление")
        
        # Selectbox with nice labels
        child_options = {c['id']: f"{c['id']} - {c['last_name']} {c['first_name']}" for c in children}
        selected_id = st.selectbox("Выберите ребенка для изменения данных", options=list(child_options.keys()), format_func=lambda x: child_options[x])
        
        if selected_id:
            child = next(c for c in children if c['id'] == selected_id)
            with st.form("edit_child_form"):
                col1, col2 = st.columns(2)
                with col1:
                    first_name_edit = st.text_input("Имя*", value=child['first_name'])
                    last_name_edit = st.text_input("Фамилия*", value=child['last_name'])
                    
                    if isinstance(child['birth_date'], str):
                        bd = datetime.datetime.strptime(child['birth_date'].split()[0], '%Y-%m-%d').date()
                    else:
                        bd = child['birth_date']
                        
                    birth_date_edit = st.date_input("Дата рождения*", value=bd)
                with col2:
                    parent_name_edit = st.text_input("Имя родителя*", value=child['parent_name'])
                    parent_phone_edit = st.text_input("Телефон родителя", value=child['parent_phone'] if child['parent_phone'] else "")
                    
                    if isinstance(child['enrollment_date'], str):
                        ed = datetime.datetime.strptime(child['enrollment_date'].split()[0], '%Y-%m-%d').date()
                    else:
                        ed = child['enrollment_date']
                        
                    enrollment_date_edit = st.date_input("Дата поступления*", value=ed)
                
                status_edit = st.selectbox("Статус", ["активный", "выбыл"], index=0 if child['status']=='активный' else 1)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submit_edit = st.form_submit_button("Сохранить изменения", type="primary")
                with col_btn2:
                    submit_del = st.form_submit_button("⚠️ Удалить запись")
                
                if submit_edit:
                    update_child(selected_id, first_name_edit, last_name_edit, birth_date_edit, parent_name_edit, parent_phone_edit, enrollment_date_edit, status_edit)
                    st.success("Данные успешно обновлены!")
                    st.rerun()
                if submit_del:
                    delete_child(selected_id)
                    st.warning("Запись о ребенке удалена!")
                    st.rerun()
    else:
        st.info("Нет записей о детях. Перейдите во вкладку 'Добавить ребенка'.")
