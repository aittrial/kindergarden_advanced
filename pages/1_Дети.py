import streamlit as st
import pandas as pd
from datetime import date, datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from crud import add_child, get_all_children, update_child, delete_child
from auth_guard import require_login, render_sidebar_user
from i18n import t, CHILD_STATUSES, CHILD_STATUS_DISPLAY, child_status_display, get_lang

st.set_page_config(page_title="Children", page_icon="👦", layout="wide")
require_login()
render_sidebar_user()
st.title(t("children_title"))


def to_dict_list(query_results):
    data = []
    if query_results:
        for item in query_results:
            try:
                row = {col.name: getattr(item, col.name) for col in item.__table__.columns}
                data.append(row)
            except Exception:
                continue
    return data


tab_list, tab_add = st.tabs([t("children_list_tab"), t("add_child_tab")])

lang = get_lang()
status_display = CHILD_STATUS_DISPLAY[lang]
status_options_display = [status_display[s] for s in CHILD_STATUSES]

with tab_add:
    st.subheader(t("new_child"))
    with st.form("add_child_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input(t("first_name"))
            last_name = st.text_input(t("last_name"))
            birth_date = st.date_input(t("birth_date"), min_value=date(2010, 1, 1), max_value=date.today())
        with col2:
            parent_name = st.text_input(t("parent_name"))
            parent_phone = st.text_input(t("parent_phone"))
            enrollment_date = st.date_input(t("enrollment_date"))

        selected_display = st.selectbox(t("status"), options=status_options_display)
        status_value = CHILD_STATUSES[status_options_display.index(selected_display)]

        if st.form_submit_button(t("add_btn"), type="primary"):
            if first_name and last_name and parent_name:
                add_child(first_name, last_name, birth_date, parent_name, parent_phone, enrollment_date, status_value)
                st.success(t("child_added").format(name=first_name))
                st.rerun()
            else:
                st.error(t("fill_required"))

with tab_list:
    st.subheader(t("all_children"))
    raw_children = get_all_children()
    children = to_dict_list(raw_children)

    if children:
        df = pd.DataFrame(children)
        df["status"] = df["status"].apply(child_status_display)
        display_cols = ["id", "last_name", "first_name", "birth_date", "parent_name", "status"]
        existing = [c for c in display_cols if c in df.columns]
        st.dataframe(df[existing], use_container_width=True, hide_index=True)

        st.divider()
        selected_id = st.selectbox(
            t("select_to_edit"),
            options=[c["id"] for c in children],
            format_func=lambda x: next(f"{c['last_name']} {c['first_name']}" for c in children if c["id"] == x)
        )

        child = next((c for c in children if c["id"] == selected_id), None)
        if child:
            with st.form("edit_form"):
                fn = st.text_input(t("first_name_field"), value=child.get("first_name", ""))
                ln = st.text_input(t("last_name_field"), value=child.get("last_name", ""))

                bd = child.get("birth_date", date.today())
                if isinstance(bd, str):
                    bd = datetime.strptime(bd.split()[0], "%Y-%m-%d").date()
                new_bd = st.date_input(t("birth_date_field"), value=bd)

                cur_status = child.get("status", CHILD_STATUSES[0])
                cur_display = status_display.get(cur_status, status_options_display[0])
                cur_idx = status_options_display.index(cur_display) if cur_display in status_options_display else 0
                new_status_display = st.selectbox(t("status"), options=status_options_display, index=cur_idx)
                new_status = CHILD_STATUSES[status_options_display.index(new_status_display)]

                if st.form_submit_button(t("save_btn")):
                    update_child(selected_id, fn, ln, new_bd, child.get("parent_name"), child.get("parent_phone"), child.get("enrollment_date"), new_status)
                    st.success(t("updated"))
                    st.rerun()
    else:
        st.info(t("no_children"))
