import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from auth_guard import require_login, render_sidebar_user, is_superadmin
from auth import hash_password
from crud import get_all_admins, create_user, delete_user_by_email, get_user_by_email
from i18n import t

st.set_page_config(page_title="Admins", page_icon="👤", layout="wide")
require_login()
render_sidebar_user()

if not is_superadmin():
    st.error(t("access_denied"))
    st.stop()

st.title(t("admins_title"))

tab_list, tab_add = st.tabs([t("admins_list_tab"), t("add_admin_tab")])

with tab_add:
    st.subheader(t("add_admin_header"))
    with st.form("add_admin_form", clear_on_submit=True):
        email = st.text_input(t("new_admin_email"))
        password = st.text_input(t("password"), type="password")
        password2 = st.text_input(t("confirm_password"), type="password")
        submitted = st.form_submit_button(t("add_admin_btn"), type="primary")

    if submitted:
        if not email or not password:
            st.error(t("fill_all_fields"))
        elif password != password2:
            st.error(t("passwords_mismatch"))
        elif len(password) < 6:
            st.error(t("password_too_short"))
        elif get_user_by_email(email.strip().lower()):
            st.error(t("email_already_exists"))
        else:
            ok = create_user(email.strip().lower(), hash_password(password), "admin")
            if ok:
                st.success(t("admin_added").format(email=email))
                st.rerun()
            else:
                st.error(t("error_creating_user"))

with tab_list:
    st.subheader(t("current_admins"))
    admins = get_all_admins()
    if admins:
        for admin in admins:
            col1, col2 = st.columns([4, 1])
            col1.write(admin.email)
            if col2.button(t("delete"), key=f"del_{admin.id}", type="secondary"):
                delete_user_by_email(admin.email)
                st.success(t("admin_deleted").format(email=admin.email))
                st.rerun()
    else:
        st.info(t("no_admins"))
