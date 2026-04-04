import streamlit as st
import pandas as pd
from crud import get_all_expenses, add_expense, delete_expense
import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from auth_guard import require_login, render_sidebar_user
from i18n import t, EXPENSE_CATEGORIES, EXPENSE_CATEGORY_DISPLAY, expense_cat_display, format_amount, get_lang

st.set_page_config(page_title="Expenses", layout="wide")
require_login()
render_sidebar_user()

st.title(t("expenses_title"))

lang = get_lang()
cat_display_map = EXPENSE_CATEGORY_DISPLAY[lang]
cats_display = [cat_display_map[c] for c in EXPENSE_CATEGORIES]

tab_add, tab_list = st.tabs([t("add_expense_tab"), t("expense_list_tab")])

with tab_add:
    st.subheader(t("add_expense_header"))
    with st.form("expense_form", clear_on_submit=True):
        exp_date = st.date_input(t("date_field"), datetime.date.today())
        selected_cat_display = st.selectbox(t("category_field"), options=cats_display)
        category = EXPENSE_CATEGORIES[cats_display.index(selected_cat_display)]
        amount = st.number_input(t("amount_field"), min_value=0.0, step=0.01)
        description = st.text_input(t("description_field"))
        comment = st.text_area(t("comment_field"))

        submitted = st.form_submit_button(t("add_expense_btn"))
        if submitted:
            if amount > 0:
                add_expense(exp_date, category, amount, description, comment)
                st.success(t("expense_added"))
                st.rerun()
            else:
                st.error(t("amount_positive"))

with tab_list:
    st.subheader(t("all_expenses_header"))

    expenses_raw = get_all_expenses()
    expenses_list = []
    if expenses_raw:
        for e in expenses_raw:
            row = {col.name: getattr(e, col.name) for col in e.__table__.columns}
            expenses_list.append(row)

    if expenses_list:
        df = pd.DataFrame(expenses_list)
        df["category"] = df["category"].apply(expense_cat_display)
        df["amount"] = df["amount"].apply(format_amount)
    else:
        df = pd.DataFrame(columns=["id", "date", "category", "amount", "description", "comment"])

    col1, col2 = st.columns(2)
    with col1:
        categories = df["category"].unique() if not df.empty else []
        cat_filters = st.multiselect(t("filter_category"), options=categories)
    with col2:
        if not df.empty and "date" in df.columns:
            df["year_month"] = df["date"].apply(lambda x: x.strftime("%Y-%m") if hasattr(x, "strftime") else str(x)[:7])
            months = sorted(df["year_month"].unique(), reverse=True)
        else:
            months = []
        month_filters = st.multiselect(t("filter_month"), options=months)

    filtered_df = df.copy()
    if cat_filters:
        filtered_df = filtered_df[filtered_df["category"].isin(cat_filters)]
    if month_filters:
        filtered_df = filtered_df[filtered_df["year_month"].isin(month_filters)]

    if not filtered_df.empty:
        st.dataframe(
            filtered_df.drop(columns=["year_month"]) if "year_month" in filtered_df.columns else filtered_df,
            use_container_width=True
        )
        expense_to_delete = st.selectbox(t("select_delete_id"), filtered_df["id"])
        if st.button(t("delete_record_btn")):
            delete_expense(expense_to_delete)
            st.warning(t("deleted_record").format(id=expense_to_delete))
            st.rerun()
    else:
        st.info(t("no_data"))
