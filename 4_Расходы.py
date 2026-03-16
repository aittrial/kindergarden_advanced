import streamlit as st
import pandas as pd
from datetime import date
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from crud import add_expense, get_all_expenses, delete_expense

st.set_page_config(page_title="Расходы", page_icon="💰", layout="wide")
st.title("Учет расходов 💰")

tab_list, tab_add = st.tabs(["📊 История расходов", "➕ Добавить расход"])

with tab_add:
    st.subheader("Новая запись о расходе")
    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            expense_date = st.date_input("Дата*", value=date.today())
            category = st.selectbox("Категория*", ["продукты", "аренда", "зарплата", "коммунальные услуги", "игрушки", "прочее"])
            amount = st.number_input("Сумма (руб)*", min_value=0.01, value=1000.0)
        with col2:
            description = st.text_input("Описание (название товара/услуги)*")
            comment = st.text_area("Дополнительный комментарий")
            
        submitted = st.form_submit_button("Добавить расход", type="primary")
        if submitted:
            if description:
                add_expense(expense_date, category, description, amount, comment)
                st.success(f"Расход на сумму {amount} руб. успешно зарегистрирован!")
                st.rerun()
            else:
                st.error("Поле 'Описание' обязательно для заполнения.")

with tab_list:
    st.subheader("Все финансовые расходы")
    expenses = get_all_expenses()
    if expenses:
        df = pd.DataFrame(expenses)
        
        # Add basic filters
        col1, col2 = st.columns(2)
        with col1:
            cat_filters = st.multiselect("Фильтр по категориям", options=df['category'].unique())
        with col2:
            # simple year-month filter string like "2023-10"
            df['year_month'] = df['date'].str[:7]
            month_filters = st.multiselect("Фильтр по месяцам", options=sorted(df['year_month'].unique(), reverse=True))
            
        filtered_df = df.copy()
        if cat_filters:
            filtered_df = filtered_df[filtered_df['category'].isin(cat_filters)]
        if month_filters:
            filtered_df = filtered_df[filtered_df['year_month'].isin(month_filters)]
            
        # Display sum block
        st.metric("Итоговая сумма расходов (по фильтрам)", f"{filtered_df['amount'].sum():,.2f} руб.".replace(',', ' '))
            
        # Display data
        display_df = filtered_df[['id', 'date', 'category', 'description', 'amount', 'comment']].copy()
        display_df.columns = ['ID', 'Дата', 'Категория', 'Описание', 'Сумма (руб)', 'Комментарий']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("**Удаление записи**")
        with st.form("delete_expense_form"):
            exp_options = {e['id']: f"{e['date']} | {e['category']} | {e['description']} ({e['amount']} руб.)" for e in expenses}
            del_id = st.selectbox("Выберите запись для удаления", options=list(exp_options.keys()), format_func=lambda x: exp_options[x], key="del_exp")
            del_sub = st.form_submit_button("⚠️ Удалить запись")
            if del_sub:
                delete_expense(del_id)
                st.warning("Запись о расходе удалена из базы.")
                st.rerun()
    else:
        st.info("История расходов пуста.")
