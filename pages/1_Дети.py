import streamlit as st
import pandas as pd
from datetime import date, datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from crud import add_child, get_all_children, update_child, update_child_group
from auth_guard import require_login, render_sidebar_user, get_active_kindergarten_id
from i18n import (t, CHILD_STATUSES, CHILD_STATUS_DISPLAY, child_status_display,
                  CHILD_GROUPS, CHILD_GROUP_DISPLAY, group_display, get_lang)

require_login()
render_sidebar_user()
kg_id = get_active_kindergarten_id()
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


lang = get_lang()
status_display = CHILD_STATUS_DISPLAY[lang]
status_options_display = [status_display[s] for s in CHILD_STATUSES]
group_display_map = CHILD_GROUP_DISPLAY[lang]
group_options_display = [group_display_map[g] for g in CHILD_GROUPS]

tab_list, tab_add = st.tabs([t("children_list_tab"), t("add_child_tab")])

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

        col3, col4 = st.columns(2)
        with col3:
            sel_status = st.selectbox(t("status"), options=status_options_display)
            status_value = CHILD_STATUSES[status_options_display.index(sel_status)]
        with col4:
            sel_group = st.selectbox(t("group_label"), options=group_options_display)
            group_value = CHILD_GROUPS[group_options_display.index(sel_group)]

        if st.form_submit_button(t("add_btn"), type="primary"):
            if first_name and last_name and parent_name:
                add_child(kg_id, first_name, last_name, birth_date,
                          parent_name, parent_phone, enrollment_date, status_value, group_value)
                st.success(t("child_added").format(name=first_name))
                st.rerun()
            else:
                st.error(t("fill_required"))

with tab_list:
    st.subheader(t("all_children"))
    children = to_dict_list(get_all_children(kg_id))

    if children:
        group_filter_options = [t("group_all")] + group_options_display
        sel_group_filter = st.selectbox(t("group_label"), options=group_filter_options, key="group_filter")

        if sel_group_filter != t("group_all"):
            gv = CHILD_GROUPS[group_options_display.index(sel_group_filter)]
            children_filtered = [c for c in children if c.get("group") == gv]
        else:
            children_filtered = children

        df = pd.DataFrame(children_filtered)
        if "status" in df.columns:
            df["status"] = df["status"].apply(child_status_display)
        if "group" in df.columns:
            df["group"] = df["group"].apply(group_display)
        display_cols = ["id", "last_name", "first_name", "birth_date", "parent_name", "group", "status"]
        existing = [c for c in display_cols if c in df.columns]
        st.dataframe(df[existing], use_container_width=True, hide_index=True)

        st.divider()
        selected_id = st.selectbox(
            t("select_to_edit"),
            options=[c["id"] for c in children],
            format_func=lambda x: next(
                f"{c['last_name']} {c['first_name']}" for c in children if c["id"] == x)
        )
        child = next((c for c in children if c["id"] == selected_id), None)
        if child:
            with st.form("edit_form"):
                col1, col2 = st.columns(2)
                with col1:
                    fn = st.text_input(t("first_name_field"), value=child.get("first_name", ""))
                    ln = st.text_input(t("last_name_field"), value=child.get("last_name", ""))
                    bd = child.get("birth_date", date.today())
                    if isinstance(bd, str):
                        bd = datetime.strptime(bd.split()[0], "%Y-%m-%d").date()
                    new_bd = st.date_input(t("birth_date_field"), value=bd)
                with col2:
                    cur_status = child.get("status", CHILD_STATUSES[0])
                    cur_s_disp = status_display.get(cur_status, status_options_display[0])
                    cur_s_idx = status_options_display.index(cur_s_disp) if cur_s_disp in status_options_display else 0
                    new_s_disp = st.selectbox(t("status"), options=status_options_display, index=cur_s_idx)
                    new_status = CHILD_STATUSES[status_options_display.index(new_s_disp)]

                    cur_group = child.get("group", CHILD_GROUPS[0])
                    cur_g_disp = group_display_map.get(cur_group, group_options_display[0])
                    cur_g_idx = group_options_display.index(cur_g_disp) if cur_g_disp in group_options_display else 0
                    new_g_disp = st.selectbox(t("group_label"), options=group_options_display, index=cur_g_idx)
                    new_group = CHILD_GROUPS[group_options_display.index(new_g_disp)]

                if st.form_submit_button(t("save_btn")):
                    update_child(selected_id, fn, ln, new_bd, child.get("parent_name"),
                                 child.get("parent_phone"), child.get("enrollment_date"), new_status)
                    update_child_group(selected_id, new_group)
                    st.success(t("updated"))
                    st.rerun()
    else:
        st.info(t("no_children"))
