import streamlit as st
from i18n import t, CURRENCIES, get_lang, get_currency
from crud import update_user_preferences


def require_login():
    if "user" not in st.session_state or st.session_state.user is None:
        st.error(t("login_required"))
        st.stop()


def current_user():
    return st.session_state.get("user")


def is_superadmin():
    user = current_user()
    return user is not None and user["role"] == "superadmin"


def render_sidebar_user():
    user = current_user()
    if not user:
        return
    with st.sidebar:
        st.markdown(f"**{user['email']}**")
        role_label = t("superadmin") if user["role"] == "superadmin" else t("admin")
        st.caption(f"{t('role')}: {role_label}")
        st.divider()

        st.markdown(f"**{t('settings_header')}**")
        lang = st.session_state.get("lang", "ru")
        currency = st.session_state.get("currency", "ILS")

        new_lang = st.selectbox(
            t("language"),
            options=["ru", "en"],
            format_func=lambda x: "Русский" if x == "ru" else "English",
            index=0 if lang == "ru" else 1,
            key="sidebar_lang"
        )
        lang_options = list(CURRENCIES.keys())
        cur_key = "name_ru" if lang == "ru" else "name_en"
        new_currency = st.selectbox(
            t("currency"),
            options=lang_options,
            format_func=lambda x: CURRENCIES[x][cur_key],
            index=lang_options.index(currency) if currency in lang_options else 0,
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
            st.rerun()
