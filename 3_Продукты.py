import streamlit as st
import pandas as pd
from datetime import date
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from crud import add_product, get_all_products, delete_product, add_product_income, add_product_expense, get_product_inventory

st.set_page_config(page_title="Продукты", page_icon="🍎", layout="wide")
st.title("Склад продуктов 🍎")

# Define tabs
tab_inventory, tab_income, tab_expense, tab_dict = st.tabs([
    "📦 Текущие остатки", 
    "📥 Приход", 
    "📤 Списание", 
    "📖 Справочник номенклатуры"
])

# INVENTORY TAB
with tab_inventory:
    st.subheader("Текущие запасы")
    inventory = get_product_inventory()
    if inventory:
        df = pd.DataFrame(inventory)
        display_df = df[['name', 'unit', 'current_stock', 'min_stock', 'total_income', 'total_expense', 'is_low_stock']].copy()
        display_df.columns = ['Название', 'Ед. изм.', 'Остаток', 'Мин. запас', 'Всего приход', 'Всего расход', 'Низкий запас']
        
        # Color specific statuses for pandas > 1.3
        def highlight_low_stock(row):
            if row['Низкий запас']:
                return ['background-color: #ffe6e6'] * len(row)
            return [''] * len(row)
            
        st.dataframe(display_df.style.apply(highlight_low_stock, axis=1), use_container_width=True, hide_index=True)
        
        # Warnings
        low_stock_items = [item['name'] for item in inventory if item['is_low_stock']]
        if low_stock_items:
            st.error(f"⚠️ Внимание! Запасы истощены у: **{', '.join(low_stock_items)}**")
            
        # Refresh btn
        if st.button("🔄 Обновить склад"):
            st.rerun()
    else:
        st.info("Склад пуст. Предварительно добавьте продукты в разделе 'Справочник'.")


# INCOME TAB
with tab_income:
    st.subheader("Регистрация прихода (закупка)")
    products = get_all_products()
    if products:
        with st.form("income_form", clear_on_submit=True):
            prod_options = {p['id']: f"{p['name']} ({p['unit']})" for p in products}
            selected_prod_id = st.selectbox("Выберите продукт*", options=list(prod_options.keys()), format_func=lambda x: prod_options[x])
            
            col1, col2 = st.columns(2)
            with col1:
                income_date = st.date_input("Дата прихода*", value=date.today())
                quantity = st.number_input("Количество*", min_value=0.01, value=1.0)
            with col2:
                price = st.number_input("Цена за единицу (руб)*", min_value=0.01, value=100.0)
                supplier = st.text_input("Поставщик")
                
            submitted = st.form_submit_button("📥 Зарегистрировать приход", type="primary")
            if submitted:
                add_product_income(selected_prod_id, income_date, quantity, price, supplier)
                st.success(f"Приход успешно зарегистрирован! (+{quantity})")
                st.rerun()
    else:
        st.warning("Сначала добавьте продукты во вкладке 'Справочник'!")


# EXPENSE TAB
with tab_expense:
    st.subheader("Списание продуктов (расход)")
    products = get_all_products()
    if products:
        with st.form("expense_form", clear_on_submit=True):
            prod_options = {p['id']: f"{p['name']} ({p['unit']})" for p in products}
            selected_prod_id = st.selectbox("Укажите продукт*", options=list(prod_options.keys()), format_func=lambda x: prod_options[x])
            
            col1, col2 = st.columns(2)
            with col1:
                expense_date = st.date_input("Дата расхода*", value=date.today())
                quantity = st.number_input("Количество для списания*", min_value=0.01, value=1.0)
            with col2:
                purpose = st.selectbox("Назначение*", ["Завтрак", "Обед", "Полдник", "Ужин", "Списание (порча)", "Иное"])
                
            submitted = st.form_submit_button("📤 Списать со склада", type="primary")
            if submitted:
                add_product_expense(selected_prod_id, expense_date, quantity, purpose)
                st.success(f"Продукт успешно списан! (-{quantity})")
                st.rerun()
    else:
        st.warning("Сначала добавьте продукты во вкладке 'Справочник'!")


# DICTIONARY TAB
with tab_dict:
    st.subheader("Добавление новой номенклатуры")
    with st.form("add_product_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            name = st.text_input("Название продукта*")
        with col2:
            unit = st.selectbox("Единица измерения*", ["кг", "литры", "штуки", "упаковки", "банки"])
            
        min_stock = st.number_input("Мин. остаток (для оповещений)", min_value=0.0, value=1.0)
            
        submitted = st.form_submit_button("➕ Добавить в базу")
        if submitted and name:
            add_product(name, unit, min_stock)
            st.success(f"Продукт '{name}' добавлен в справочник!")
            st.rerun()
            
    products = get_all_products()
    if products:
        st.divider()
        st.markdown("**Существующая номенклатура:**")
        df = pd.DataFrame(products)
        display_df = df[['id', 'name', 'unit', 'min_stock']]
        display_df.columns = ['ID', 'Название', 'Ед. изм.', 'Мин. остаток']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown("**Удаление продукта**")
        st.caption("Удаление продукта приведет к удалению всей истории его приходов и расходов (каскадное удаление).")
        
        with st.form("delete_product_form"):
            prod_options = {p['id']: f"{p['id']} - {p['name']}" for p in products}
            del_id = st.selectbox("Выберите продукт", options=list(prod_options.keys()), format_func=lambda x: prod_options[x], key="del_prod")
            del_submitted = st.form_submit_button("⚠️ Удалить продукт")
            if del_submitted:
                delete_product(del_id)
                st.warning("Продукт и связанные записи удалены из базы.")
                st.rerun()
