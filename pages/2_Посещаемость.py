import streamlit as st
import pandas as pd
from datetime import date
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from crud import get_all_children, add_attendance, get_attendance_by_date, get_all_attendance
from auth_guard import require_login, render_sidebar_user
from i18n import (t, ATTENDANCE_STATUSES, ATTENDANCE_DISPLAY, att_display,
                  CHILD_GROUPS, CHILD_GROUP_DISPLAY, group_display, get_lang)

require_login()
render_sidebar_user()
st.title(t("attendance_title"))


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
att_display_map = ATTENDANCE_DISPLAY[lang]
att_options_display = [att_display_map[s] for s in ATTENDANCE_STATUSES]
group_display_map = CHILD_GROUP_DISPLAY[lang]
group_options_display = [group_display_map[g] for g in CHILD_GROUPS]

tab_mark, tab_log = st.tabs([t("mark_tab"), t("log_tab")])

with tab_mark:
    col_date, col_group = st.columns(2)
    with col_date:
        selected_date = st.date_input(t("date_label"), value=date.today())
    with col_group:
        group_filter_options = [t("group_all")] + group_options_display
        selected_group = st.selectbox(t("group_label"), options=group_filter_options, key="att_group")

    raw_children = get_all_children()
    active_children = [c for c in to_dict_list(raw_children) if c.get("status") == "активный"]

    if selected_group != t("group_all"):
        group_value = CHILD_GROUPS[group_options_display.index(selected_group)]
        active_children = [c for c in active_children if c.get("group") == group_value]

    if active_children:
        existing_raw = get_attendance_by_date(selected_date)
        att_dict = {row["child_id"]: row["status"] for row in to_dict_list(existing_raw)}

        with st.form("att_form"):
            selections = {}
            for child in active_children:
                col1, col2 = st.columns([2, 3])
                grp = group_display(child.get("group", CHILD_GROUPS[0]))
                col1.write(f"{child.get('last_name')} {child.get('first_name')} *({grp})*")
                current_status = att_dict.get(child["id"], ATTENDANCE_STATUSES[0])
                current_display = att_display_map.get(current_status, att_options_display[0])
                cur_idx = att_options_display.index(current_display) if current_display in att_options_display else 0
                selected_display = col2.radio(
                    t("att_status_label"),
                    att_options_display,
                    index=cur_idx,
                    key=f"c_{child['id']}",
                    horizontal=True,
                    label_visibility="collapsed"
                )
                selections[child["id"]] = ATTENDANCE_STATUSES[att_options_display.index(selected_display)]

            if st.form_submit_button(t("save_att_btn")):
                for c_id, stat in selections.items():
                    add_attendance(c_id, selected_date, stat)
                st.success(t("att_saved"))
                st.rerun()
    else:
        st.info(t("no_children"))

with tab_log:
    history = get_all_attendance()
    if history:
        df = pd.DataFrame(history)
        if "status" in df.columns:
            df["status"] = df["status"].apply(att_display)
        # Add group column if children data available
        raw_children = get_all_children()
        children_dict = {c.id: c.group for c in raw_children if hasattr(c, "group")}
        if children_dict:
            df["group"] = df["child_id"].map(children_dict).apply(
                lambda g: group_display(g) if g else "")
        st.dataframe(df, use_container_width=True)
