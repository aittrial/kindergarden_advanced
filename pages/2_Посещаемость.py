import streamlit as st
import pandas as pd
from datetime import date
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from crud import get_all_children, add_attendance, get_attendance_by_date, get_all_attendance
from auth_guard import require_login, render_sidebar_user

st.set_page_config(page_title="Посещаемость", layout="wide")
require_login()
render_sidebar_user()
st.title("Учет посещаемости 📅")

def to_dict_list(query_results):
    data = []
    if query_results:
        for item in query_results:
            try:
                row = {col.name: getattr(item, col.name) for col in item.__table__.columns}
                data.append(row)
            except: continue
    return data

tab_mark, tab_log = st.tabs(["📍 Отметить", "📖 Журнал"])

with tab_mark:
    selected_date = st.date_input("Дата", value=date.today())
    
    # Вызов БЕЗ аргументов (как в новом crud)
    raw_children = get_all_children() 
    active_children = [c for c in to_dict_list(raw_children) if c.get('status') == 'активный']
    
    if active_children:
        # Вызов С аргументом даты
        existing_raw = get_attendance_by_date(selected_date)
        att_dict = {row['child_id']: row['status'] for row in to_dict_list(existing_raw)}
        
        with st.form("att_form"):
            selections = {}
            for child in active_children:
                col1, col2 = st.columns([2, 3])
                col1.write(f"{child.get('last_name')} {child.get('first_name')}")
                val = att_dict.get(child['id'], "присутствовал")
                selections[child['id']] = col2.radio("Статус", ["присутствовал", "отсутствовал", "болел"], 
                                                   index=["присутствовал", "отсутствовал", "болел"].index(val),
                                                   key=f"c_{child['id']}", horizontal=True, label_visibility="collapsed")
            
            if st.form_submit_button("Сохранить"):
                for c_id, stat in selections.items():
                    add_attendance(c_id, selected_date, stat)
                st.success("Готово!")
                st.rerun()

with tab_log:
    history = get_all_attendance()
    if history:
        st.dataframe(pd.DataFrame(history), use_container_width=True)
