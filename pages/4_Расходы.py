import streamlit as st
import pandas as pd
from crud import get_all_expenses, add_expense, delete_expense
import datetime

st.set_page_config(page_title="Учет расходов", layout="wide")

st.title("💰 Учет финансовых расходов")

# Создаем вкладки
tab_add, tab_list = st.tabs(["➕ Добавить расход", "📋 История расходов"])

with tab_add:
    st.subheader("Добавить новую запись")
    with st.form("expense_form", clear_on_submit=True):
        date = st.date_input("Дата", datetime.date.today())
        category = st.selectbox("Категория", ["Еда", "Транспорт", "Жилье", "Развлечения", "Связь", "Другое"])
        amount = st.number_input("Сумма", min_value=0.0, step=0.01)
        description = st.text_input("Описание (на что потратили)")
        comment = st.text_area("Комментарий (необязательно)")
        
        submitted = st.form_submit_button("Добавить расход")
        if submitted:
            if amount > 0:
                add_expense(date, category, amount, description, comment)
                st.success("Расход успешно добавлен!")
                st.rerun()
            else:
                st.error("Сумма должна быть больше нуля")

with tab_list:
    st.subheader("Все финансовые расходы")
    
    # 1. Загружаем данные из базы
    expenses_raw = get_all_expenses()

    # 2. Превращаем объекты в список словарей
    expenses_list = []
    if expenses_raw:
        for e in expenses_raw:
            row = {col.name: getattr(e, col.name) for col in e.__table__.columns}
            expenses_list.append(row)

    # 3. Создаем DataFrame
    if expenses_list:
        df = pd.DataFrame(expenses_list)
    else:
        df = pd.DataFrame(columns=['id', 'date', 'category', 'amount', 'description', 'comment'])

    # 4. Фильтры
    col1, col2 = st.columns(2)
    with col1:
        categories = df['category'].unique() if not df.empty else []
        cat_filters = st.multiselect("Фильтр по категориям", options=categories)
    
    with col2:
        if not df.empty and 'date' in df.columns:
            df['year_month'] = df['date'].apply(lambda x: x.strftime('%Y-%m') if hasattr(x, 'strftime') else str(x)[:7])
            months = sorted(df['year_month'].unique(), reverse=True)
        else:
            months = []
        month_filters = st.multiselect("Фильтр по месяцам", options=months)

    # Применение фильтров
    filtered_df = df.copy()
    if cat_filters:
        filtered_df = filtered_df[filtered_df['category'].isin(cat_filters)]
    if month_filters:
        filtered_df = filtered_df[filtered_df['year_month'].isin(month_filters)]

    # Вывод таблицы
    if not filtered_df.empty:
        st.dataframe(filtered_df.drop(columns=['year_month']) if 'year_month' in filtered_df.columns else filtered_df, use_container_width=True)
        
        # Удаление записей
        expense_to_delete = st.selectbox("Выберите ID для удаления", filtered_df['id'])
        if st.button("Удалить выбранную запись"):
            delete_expense(expense_to_delete)
            st.warning(f"Запись ID {expense_to_delete} удалена")
            st.rerun()
    else:
        st.info("Данных пока нет или они не соответствуют фильтрам.")
