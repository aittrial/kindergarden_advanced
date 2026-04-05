import streamlit as st
import pandas as pd
from datetime import date, datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from crud import add_child, get_all_children, update_child
from auth_guard import require_login, render_sidebar_user
from i18n import (t, CHILD_STATUSES, CHILD_STATUS_DISPLAY, child_status_display,
                  CHILD_GROUPS, CHILD_GROUP_DISPLAY, group_display, get_lang)

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
            selected_status_display = st.selectbox(t("status"), options=status_options_display)
            status_value = CHILD_STATUSES[status_options_display.index(selected_status_display)]
        with col4:
            selected_group_display = st.selectbox(t("group_label"), options=group_options_display)
            group_value = CHILD_GROUPS[group_options_display.index(selected_group_display)]

        if st.form_submit_button(t("add_btn"), type="primary"):
            if first_name and last_name and parent_name:
                add_child(first_name, last_name, birth_date, parent_name,
                          parent_phone, enrollment_date, status_value)
                # update group separately since add_child doesn't have group param yet
                from crud import get_all_children, update_child_group
                all_c = to_dict_list(get_all_children())
                new_child = next((c for c in reversed(all_c)
                                  if c["first_name"] == first_name and c["last_name"] == last_name), None)
                if new_child:
                    update_child_group(new_child["id"], group_value)
                st.success(t("child_added").format(name=first_name))
                st.rerun()
            else:
                st.error(t("fill_required"))

with tab_list:
    st.subheader(t("all_children"))
    raw_children = get_all_children()
    children = to_dict_list(raw_children)

    if children:
        # Group filter
        group_filter_options = [t("group_all")] + group_options_display
        selected_group_filter = st.selectbox(t("group_label"), options=group_filter_options, key="group_filter")

        if selected_group_filter != t("group_all"):
            group_value_filter = CHILD_GROUPS[group_options_display.index(selected_group_filter)]
            children_filtered = [c for c in children if c.get("group") == group_value_filter]
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
            format_func=lambda x: next(f"{c['last_name']} {c['first_name']}" for c in children if c["id"] == x)
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
                    cur_status_disp = status_display.get(cur_status, status_options_display[0])
                    cur_status_idx = status_options_display.index(cur_status_disp) if cur_status_disp in status_options_display else 0
                    new_status_display = st.selectbox(t("status"), options=status_options_display, index=cur_status_idx)
                    new_status = CHILD_STATUSES[status_options_display.index(new_status_display)]

                    cur_group = child.get("group", CHILD_GROUPS[0])
                    cur_group_disp = group_display_map.get(cur_group, group_options_display[0])
                    cur_group_idx = group_options_display.index(cur_group_disp) if cur_group_disp in group_options_display else 0
                    new_group_display = st.selectbox(t("group_label"), options=group_options_display, index=cur_group_idx)
                    new_group = CHILD_GROUPS[group_options_display.index(new_group_display)]

                if st.form_submit_button(t("save_btn")):
                    from crud import update_child_group
                    update_child(selected_id, fn, ln, new_bd, child.get("parent_name"),
                                 child.get("parent_phone"), child.get("enrollment_date"), new_status)
                    update_child_group(selected_id, new_group)
                    st.success(t("updated"))
                    st.rerun()
    else:
        st.info(t("no_children"))
