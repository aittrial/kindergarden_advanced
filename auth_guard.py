import streamlit as st


def require_login():
    """Call at the top of every page. Stops rendering if not logged in."""
    if "user" not in st.session_state or st.session_state.user is None:
        st.error("Пожалуйста, войдите в систему.")
        st.stop()


def current_user():
    return st.session_state.get("user")


def is_superadmin():
    user = current_user()
    return user is not None and user["role"] == "superadmin"


def render_sidebar_user():
    user = current_user()
    if user:
        with st.sidebar:
            st.markdown(f"**{user['email']}**")
            st.caption(f"Роль: {'Superadmin' if user['role'] == 'superadmin' else 'Admin'}")
            st.divider()
            if st.button("Выйти", use_container_width=True, key="sidebar_logout"):
                st.session_state.user = None
                st.rerun()
