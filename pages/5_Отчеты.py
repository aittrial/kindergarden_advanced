import streamlit as st
import pandas as pd
from io import BytesIO
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from crud import get_all_children, get_all_attendance, get_product_inventory, get_all_expenses
from auth_guard import require_login, render_sidebar_user, get_active_kindergarten_id
from i18n import t, format_amount, att_display, child_status_display, expense_cat_display, unit_display

require_login()
render_sidebar_user()
kg_id = get_active_kindergarten_id()
st.title(t("reports_title"))


def to_dict_list(query_results):
    data = []
    if query_results:
        for item in query_results:
            try:
                data.append(item if isinstance(item, dict) else
                            {col.name: getattr(item, col.name) for col in item.__table__.columns})
            except Exception:
                continue
    return data


def to_excel(df_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()


tab_summary, tab_children, tab_att, tab_prod, tab_fin = st.tabs([
    t("summary_tab"), t("children_rep_tab"), t("att_rep_tab"),
    t("products_rep_tab"), t("finance_rep_tab")
])

with tab_summary:
    st.subheader(t("summary_header"))
    col1, col2, col3 = st.columns(3)
    children_count = len(to_dict_list(get_all_children(kg_id)))
    expenses_total = sum(e.amount for e in get_all_expenses(kg_id))
    col1.metric(t("total_children"), children_count)
    col2.metric(t("total_expenses"), format_amount(expenses_total))
    col3.metric(t("system_status"), t("online"))

with tab_children:
    kids = to_dict_list(get_all_children(kg_id))
    if kids:
        df_kids = pd.DataFrame(kids)
        if "status" in df_kids.columns:
            df_kids["status"] = df_kids["status"].apply(child_status_display)
        df_kids = df_kids.drop(columns=["kindergarten_id"], errors="ignore")
        st.dataframe(df_kids, use_container_width=True)
        st.download_button(t("download_children"), to_excel({"Children": df_kids}), "children.xlsx")

with tab_att:
    att = get_all_attendance(kg_id)
    if att:
        df_att = pd.DataFrame(att)
        if "status" in df_att.columns:
            df_att["status"] = df_att["status"].apply(att_display)
        st.dataframe(df_att, use_container_width=True)
        st.download_button(t("download_attendance"), to_excel({"Attendance": df_att}), "attendance.xlsx")

with tab_prod:
    st.subheader(t("warehouse_report"))
    inv = get_product_inventory(kg_id)
    if inv:
        df_inv = pd.DataFrame(inv)
        if "unit" in df_inv.columns:
            df_inv["unit"] = df_inv["unit"].apply(unit_display)
        st.dataframe(df_inv, use_container_width=True)
        st.download_button(t("download_inventory"), to_excel({"Inventory": df_inv}), "inventory.xlsx")

with tab_fin:
    st.subheader(t("finance_report"))
    exp = to_dict_list(get_all_expenses(kg_id))
    if exp:
        df_exp = pd.DataFrame(exp)
        if "category" in df_exp.columns:
            df_exp["category"] = df_exp["category"].apply(expense_cat_display)
        if "amount" in df_exp.columns:
            df_exp["amount"] = df_exp["amount"].apply(format_amount)
        df_exp = df_exp.drop(columns=["kindergarten_id"], errors="ignore")
        st.dataframe(df_exp, use_container_width=True)
        st.download_button(t("download_expenses"), to_excel({"Expenses": df_exp}), "expenses.xlsx")
