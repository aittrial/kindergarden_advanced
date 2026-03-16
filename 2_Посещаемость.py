import streamlit as st
import pandas as pd
from datetime import date
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from crud import get_all_children, add_attendance, get_attendance_by_date, get_all_attendance

st.set_page_config(page_title="Посещаемость", page_icon="📅", layout="wide")
st.title("Учет посещаемости 📅")

tab_mark, tab_log = st.tabs(["📍 Отметить присутствие", "📖 Журнал посещаемости"])

with tab_mark:
    st.subheader("Ежедневная отметка")
    selected_date = st.date_input("Выберите дату", value=date.today(), key="mark_date")
    
    # We only mark attendance for active children
    children = [c for c in get_all_children() if c['status'] == 'активный']
    
    if children:
        # Get existing attendance for this date to pre-fill the form
        existing_att = get_attendance_by_date(selected_date)
        att_dict = {row['child_id']: row['status'] for row in existing_att}
        
        with st.form("attendance_form"):
            st.write(f"Отметка для **{selected_date.strftime('%d.%m.%Y')}**")
            st.caption("По умолчанию выбран статус 'присутствовал'")
            
            status_selections = {}
            
            # Header
            col1, col2 = st.columns([2, 3])
            col1.markdown("**ФИО Ребенка**")
            col2.markdown("**Статус**")
            st.divider()
            
            for child in children:
                c1, c2 = st.columns([2, 3])
                c1.write(f"👦 {child['last_name']} {child['first_name']}")
                
                current_status = att_dict.get(child['id'], "присутствовал")
                status_index = ["присутствовал", "отсутствовал", "болел"].index(current_status)
                
                with c2:
                    status_selections[child['id']] = st.radio(
                        f"Status for {child['id']}", 
                        ["присутствовал", "отсутствовал", "болел"],
                        index=status_index,
                        key=f"status_{child['id']}",
                        horizontal=True,
                        label_visibility="collapsed"
                    )
            
            st.divider()
            submitted = st.form_submit_button("💾 Сохранить журнал за день", type="primary")
            if submitted:
                for child_id, status in status_selections.items():
                    add_attendance(child_id, selected_date, status)
                st.success("✅ Журнал посещаемости успешно сохранен!")
                st.rerun()
    else:
        st.info("Нет активных детей для составления журнала. Добавьте детей в разделе 'Дети'.")

with tab_log:
    st.subheader("Журнал (все записи)")
    attendance_records = get_all_attendance()
    if attendance_records:
        df = pd.DataFrame(attendance_records)
        display_df = df[['date', 'last_name', 'first_name', 'status']].copy()
        display_df.columns = ['Дата', 'Фамилия', 'Имя', 'Статус']
        
        # Sort by date descending
        display_df = display_df.sort_values(by=['Дата', 'Фамилия'], ascending=[False, True])
        
        # Color specific statuses
        def highlight_status(val):
            color = ''
            if val == 'отсутствовал':
                color = '#ffcccc'
            elif val == 'болел':
                color = '#ffebd6'
            elif val == 'присутствовал':
                color = '#d6f5d6'
            return f'background-color: {color}'
            
        st.dataframe(display_df.style.map(highlight_status, subset=['Статус']), use_container_width=True, hide_index=True)
    else:
        st.info("Журнал посещаемости пуст.")

