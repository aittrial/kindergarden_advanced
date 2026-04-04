import streamlit as st
import pandas as pd
from datetime import date
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from crud import add_product, get_all_products, delete_product, add_product_income, add_product_expense, get_product_inventory
from auth_guard import require_login, render_sidebar_user
from i18n import t, PRODUCT_UNITS, PRODUCT_UNIT_DISPLAY, unit_display, get_lang

require_login()
render_sidebar_user()
st.title(t("products_title"))


def to_dict_list(query_results):
    if not query_results:
        return []
    if isinstance(query_results[0], dict):
        return query_results
    return [{col.name: getattr(item, col.name) for col in item.__table__.columns} for item in query_results]


lang = get_lang()
unit_display_map = PRODUCT_UNIT_DISPLAY[lang]
units_display = [unit_display_map[u] for u in PRODUCT_UNITS]

tab_inv, tab_inc, tab_exp, tab_dict = st.tabs([
    t("inventory_tab"), t("income_tab"), t("expense_tab"), t("dict_tab")
])

with tab_inv:
    st.subheader(t("current_stock"))
    inventory = get_product_inventory()
    if inventory:
        df = pd.DataFrame(inventory)
        df["unit"] = df["unit"].apply(unit_display)
        df.columns = [t("col_id"), t("col_name"), t("col_unit"), t("col_stock"), t("col_min_stock")]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info(t("warehouse_empty"))

with tab_inc:
    st.subheader(t("receive_stock_header"))
    prods = to_dict_list(get_all_products())
    if prods:
        with st.form("inc_form"):
            p_id = st.selectbox(t("product_label"), options=[p["id"] for p in prods],
                                format_func=lambda x: next(p["name"] for p in prods if p["id"] == x))
            qty = st.number_input(t("quantity_label"), min_value=0.1)
            if st.form_submit_button(t("add_income_btn")):
                add_product_income(p_id, date.today(), qty)
                st.success(t("income_done"))
                st.rerun()

with tab_exp:
    st.subheader(t("write_off_header"))
    prods = to_dict_list(get_all_products())
    if prods:
        with st.form("exp_form"):
            p_id = st.selectbox(t("product_label"), options=[p["id"] for p in prods],
                                format_func=lambda x: next(p["name"] for p in prods if p["id"] == x))
            qty = st.number_input(t("quantity_label"), min_value=0.1)
            if st.form_submit_button(t("write_off_btn")):
                add_product_expense(p_id, date.today(), qty)
                st.success(t("written_off"))
                st.rerun()

with tab_dict:
    st.subheader(t("nomenclature"))
    with st.form("add_prod_form"):
        n = st.text_input(t("product_name_label"))
        selected_unit_display = st.selectbox(t("unit_label"), options=units_display)
        unit_value = PRODUCT_UNITS[units_display.index(selected_unit_display)]
        if st.form_submit_button(t("add_to_dict_btn")):
            add_product(n, unit_value, 1.0)
            st.rerun()

    all_p = to_dict_list(get_all_products())
    if all_p:
        df_p = pd.DataFrame(all_p)[["id", "name", "unit"]]
        df_p["unit"] = df_p["unit"].apply(unit_display)
        st.dataframe(df_p, use_container_width=True)
