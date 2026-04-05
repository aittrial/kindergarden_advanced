import streamlit as st
import pandas as pd
from datetime import date
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from crud import (get_all_children, get_all_payments, add_payment,
                  delete_payment, get_debtors, update_child_fee)
from auth_guard import require_login, render_sidebar_user, get_active_kindergarten_id
from i18n import t, MONTHS, format_amount, get_lang, group_display, month_name

require_login()
render_sidebar_user()
kg_id = get_active_kindergarten_id()
st.title(t("payments_title"))


def to_dict_list(query_results):
    if not query_results:
        return []
    if isinstance(query_results[0], dict):
        return query_results
    return [{col.name: getattr(item, col.name) for col in item.__table__.columns}
            for item in query_results]


lang = get_lang()
months_list = MONTHS[lang]
today = date.today()

tab_add, tab_history, tab_debtors = st.tabs([
    t("add_payment_tab"), t("payment_history_tab"), t("debtors_tab")
])

with tab_add:
    children = to_dict_list(get_all_children(kg_id))
    active = [c for c in children if c.get("status") == "активный"]

    if not active:
        st.info(t("no_children"))
    else:
        col_pay, col_fee = st.columns(2)

        with col_pay:
            st.subheader(t("add_payment_tab"))
            with st.form("payment_form", clear_on_submit=True):
                child_id = st.selectbox(
                    t("child_label"),
                    options=[c["id"] for c in active],
                    format_func=lambda x: next(
                        f"{c['last_name']} {c['first_name']}" for c in active if c["id"] == x)
                )
                col1, col2 = st.columns(2)
                with col1:
                    year = st.number_input(t("year_label"), min_value=2020,
                                           max_value=today.year + 1, value=today.year)
                with col2:
                    month_display = st.selectbox(t("month_label"), options=months_list,
                                                 index=today.month - 1)
                    month = months_list.index(month_display) + 1
                amount = st.number_input(t("amount_label"), min_value=0.0, step=10.0)
                paid_date = st.date_input(t("paid_date_label"), value=today)
                comment = st.text_input(t("comment_label"))
                if st.form_submit_button(t("add_payment_btn"), type="primary"):
                    if amount > 0:
                        add_payment(child_id, int(year), month, amount, paid_date, comment)
                        st.success(t("payment_added"))
                        st.rerun()
                    else:
                        st.error(t("amount_positive"))

        with col_fee:
            st.subheader(t("monthly_fee_label"))
            with st.form("fee_form"):
                fee_child_id = st.selectbox(
                    t("child_label"),
                    options=[c["id"] for c in children],
                    format_func=lambda x: next(
                        f"{c['last_name']} {c['first_name']}" for c in children if c["id"] == x),
                    key="fee_child"
                )
                sel = next((c for c in children if c["id"] == fee_child_id), None)
                cur_fee = float(sel.get("monthly_fee") or 0) if sel else 0.0
                new_fee = st.number_input(t("monthly_fee_label"), min_value=0.0,
                                          step=10.0, value=cur_fee)
                if st.form_submit_button(t("set_fee_btn")):
                    update_child_fee(fee_child_id, new_fee)
                    st.success(t("fee_updated"))
                    st.rerun()

with tab_history:
    payments = get_all_payments(kg_id)
    if payments:
        df = pd.DataFrame(payments)
        df["month"] = df["month"].apply(lambda m: month_name(m))
        df["amount"] = df["amount"].apply(format_amount)
        st.dataframe(df.drop(columns=["child_id"]), use_container_width=True, hide_index=True)
        pay_to_delete = st.selectbox(
            t("select_delete_id"), [p["id"] for p in payments],
            format_func=lambda x: next(
                f"#{x} — {p['child_name']} {p['year']}/{p['month']}"
                for p in payments if p["id"] == x))
        if st.button(t("delete_payment_btn"), type="secondary"):
            delete_payment(pay_to_delete)
            st.success(t("payment_deleted"))
            st.rerun()
    else:
        st.info(t("no_payments"))

with tab_debtors:
    col1, col2 = st.columns(2)
    with col1:
        check_year = st.number_input(t("year_label"), min_value=2020,
                                     max_value=today.year + 1, value=today.year, key="debt_year")
    with col2:
        month_disp = st.selectbox(t("debtor_month"), options=months_list,
                                  index=today.month - 1, key="debt_month")
        check_month = months_list.index(month_disp) + 1

    debtors = get_debtors(kg_id, int(check_year), check_month)
    if debtors:
        st.error(f"**{t('debtors_header')} — {month_disp} {int(check_year)}**")
        data = []
        for d in debtors:
            data.append({
                t("child_label"): f"{d.last_name} {d.first_name}",
                t("group_label"): group_display(d.group or "младшая"),
                t("parent_name"): d.parent_name,
                t("parent_phone"): d.parent_phone,
                t("monthly_fee_label"): format_amount(d.monthly_fee or 0),
                t("debt_amount"): format_amount(getattr(d, "_debt_amount", d.monthly_fee or 0)),
            })
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.success(t("no_debtors"))
