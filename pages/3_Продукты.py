import streamlit as st
import pandas as pd
from datetime import date
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from crud import add_product, get_all_products, delete_product, add_product_income, add_product_expense, get_product_inventory

st.set_page_config(page_title="Продукты", page_icon="🍎", layout="wide")
st.title("Склад продуктов 🍎")

def to_dict_list(query_results):
    if not query_results: return []
    if isinstance(query_results[0], dict): return query_results
    return [{col.name: getattr(item, col.name) for col in item.__table__.columns} for item in query_results]

tab_inv, tab_inc, tab_exp, tab_dict = st.tabs(["📦 Остатки", "📥 Приход", "📤 Списание", "📖 Справочник"])

# ТАБ 1: ОСТАТКИ
with tab_inv:
    st.subheader("Текущие запасы")
    inventory = get_product_inventory() # Возвращает список словарей
    if inventory:
        df = pd.DataFrame(inventory)
        df.columns = ['ID', 'Название', 'Ед. изм.', 'Остаток', 'Мин. запас']
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Склад пуст.")

# ТАБ 2: ПРИХОД
with tab_inc:
    st.subheader("Пополнение склада")
    prods = to_dict_list(get_all_products())
    if prods:
        with st.form("inc_form"):
            p_id = st.selectbox("Продукт", options=[p['id'] for p in prods], format_func=lambda x: next(p['name'] for p in prods if p['id']==x))
            qty = st.number_input("Количество", min_value=0.1)
            if st.form_submit_button("Добавить"):
                add_product_income(p_id, date.today(), qty)
                st.success("Приход оформлен")
                st.rerun()

# ТАБ 3: СПИСАНИЕ
with tab_exp:
    st.subheader("Расход продуктов")
    prods = to_dict_list(get_all_products())
    if prods:
        with st.form("exp_form"):
            p_id = st.selectbox("Продукт ", options=[p['id'] for p in prods], format_func=lambda x: next(p['name'] for p in prods if p['id']==x))
            qty = st.number_input("Количество ", min_value=0.1)
            if st.form_submit_button("Списать"):
                add_product_expense(p_id, date.today(), qty)
                st.success("Списано")
                st.rerun()

# ТАБ 4: СПРАВОЧНИК
with tab_dict:
    st.subheader("Номенклатура")
    with st.form("add_prod_form"):
        n = st.text_input("Название")
        u = st.selectbox("Ед. изм.", ["кг", "литры", "штуки"])
        if st.form_submit_button("Добавить в справочник"):
            add_product(n, u, 1.0)
            st.rerun()
    
    all_p = to_dict_list(get_all_products())
    if all_p:
        st.dataframe(pd.DataFrame(all_p)[['id', 'name', 'unit']], use_container_width=True)
