import streamlit as st
from i18n import t, CURRENCIES
from crud import update_user_preferences, get_kindergarten_by_id


def require_login():
    if "user" not in st.session_state or st.session_state.user is None:
        st.error(t("login_required"))
        st.stop()


def current_user():
    return st.session_state.get("user")


def is_superadmin():
    user = current_user()
    return user is not None and user["role"] == "superadmin"


def get_active_kindergarten_id():
    user = current_user()
    if user is None:
        return None
    if user["role"] == "superadmin":
        return st.session_state.get("active_kindergarten_id")
    return user.get("kindergarten_id")


def render_sidebar_user():
    user = current_user()
    if not user:
        return

    with st.sidebar:
        # Show active kindergarten context for superadmin
        if user["role"] == "superadmin":
            kg_id = st.session_state.get("active_kindergarten_id")
            if kg_id:
                kg = get_kindergarten_by_id(kg_id)
                if kg:
                    st.markdown(f"🏫 **{kg.name}**")
                if st.button(t("back_to_list"), use_container_width=True, key="back_to_kg_list"):
                    st.session_state.active_kindergarten_id = None
                    st.rerun()
                st.divider()

        st.markdown(f"**{user['email']}**")
        role_label = t("superadmin") if user["role"] == "superadmin" else t("admin")
        st.caption(f"{t('role')}: {role_label}")
        st.divider()

        # Language & currency settings
        st.markdown(f"**{t('settings_header')}**")
        lang_options = ["ru", "en"]
        cur_lang = st.session_state.get("lang", "ru")
        new_lang = st.selectbox(
            t("language"), options=lang_options,
            format_func=lambda x: "Русский" if x == "ru" else "English",
            index=lang_options.index(cur_lang) if cur_lang in lang_options else 0,
            key="sidebar_lang"
        )
        cur_keys = list(CURRENCIES.keys())
        cur_currency = st.session_state.get("currency", "ILS")
        cur_key = "name_ru" if cur_lang == "ru" else "name_en"
        new_currency = st.selectbox(
            t("currency"), options=cur_keys,
            format_func=lambda x: CURRENCIES[x][cur_key],
            index=cur_keys.index(cur_currency) if cur_currency in cur_keys else 0,
            key="sidebar_currency"
        )
        if st.button(t("save"), key="save_prefs", use_container_width=True):
            st.session_state.lang = new_lang
            st.session_state.currency = new_currency
            update_user_preferences(user["email"], new_lang, new_currency)
            st.rerun()

        st.divider()
        if st.button(t("sign_out"), use_container_width=True, key="sidebar_logout"):
            st.session_state.user = None
            st.session_state.active_kindergarten_id = None
            st.rerun()
