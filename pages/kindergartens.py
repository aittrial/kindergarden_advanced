import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from auth_guard import require_login, render_sidebar_user, is_superadmin
from crud import get_all_kindergartens, add_kindergarten, update_kindergarten, delete_kindergarten
from i18n import t

require_login()
render_sidebar_user()

if not is_superadmin():
    st.error(t("access_denied"))
    st.stop()

st.title(t("kindergartens_title"))

# ── SEED BUTTON (one-time setup) ─────────────────────────────────────────────
with st.expander("🛠 Инициализация базы данных", expanded=False):
    st.warning("**Внимание:** сбросит ВСЕ данные и создаст тестовые садики!")
    col1, col2 = st.columns([2, 1])
    with col1:
        new_email = st.text_input("Email суперадмина после сброса", value="admin@kms.com")
        new_pass = st.text_input("Пароль", value="admin123", type="password")
    with col2:
        st.write("")
        st.write("")
        run_seed = st.button("🗑 Сбросить и заполнить", type="secondary")
    if run_seed:
        import importlib.util
        from pathlib import Path as _Path
        spec = importlib.util.spec_from_file_location(
            "seed", _Path(__file__).resolve().parent.parent / "seed.py")
        # Override credentials before running seed
        import builtins
        _orig_input = builtins.__dict__.get("input")
        # Patch seed constants via environment
        import os
        os.environ["SEED_EMAIL"] = new_email
        os.environ["SEED_PASSWORD"] = new_pass
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            st.success("✅ База данных инициализирована! Войдите заново.")
            st.session_state.user = None
            st.rerun()
        except Exception as e:
            st.error(f"Ошибка: {e}")

tab_list, tab_add = st.tabs([t("kindergartens_list_tab"), t("add_kindergarten_tab")])

with tab_list:
    kgs = get_all_kindergartens()
    if not kgs:
        st.info(t("no_kindergartens"))
    else:
        for kg in kgs:
            with st.expander(f"🏫 {kg.name}", expanded=False):
                col_info, col_actions = st.columns([3, 1])
                with col_info:
                    if kg.address:
                        st.write(f"📍 {kg.address}")
                    if kg.phone:
                        st.write(f"📞 {kg.phone}")
                    if kg.logo_url:
                        st.image(kg.logo_url, width=80)

                with col_actions:
                    if st.button(t("enter_kindergarten"), key=f"enter_{kg.id}",
                                 type="primary", use_container_width=True):
                        st.session_state.active_kindergarten_id = kg.id
                        st.rerun()

                # Edit form
                with st.form(f"edit_kg_{kg.id}"):
                    st.markdown(f"**{t('edit_kindergarten')}**")
                    new_name = st.text_input(t("kg_name"), value=kg.name or "")
                    new_addr = st.text_input(t("kg_address"), value=kg.address or "")
                    new_phone = st.text_input(t("kg_phone"), value=kg.phone or "")
                    new_logo = st.text_input(t("kg_logo"), value=kg.logo_url or "")
                    if st.form_submit_button(t("save_kindergarten")):
                        update_kindergarten(kg.id, new_name, new_addr, new_phone, new_logo)
                        st.success(t("kindergarten_updated"))
                        st.rerun()

                st.divider()
                if st.button(f"🗑 {t('delete')} «{kg.name}»",
                             key=f"del_kg_{kg.id}", type="secondary"):
                    delete_kindergarten(kg.id)
                    st.warning(t("kindergarten_deleted"))
                    st.rerun()

with tab_add:
    with st.form("add_kg_form", clear_on_submit=True):
        name = st.text_input(t("kg_name"))
        address = st.text_input(t("kg_address"))
        phone = st.text_input(t("kg_phone"))
        logo_url = st.text_input(t("kg_logo"))
        if st.form_submit_button(t("add_kindergarten_btn"), type="primary"):
            if name:
                add_kindergarten(name, address, phone, logo_url)
                st.success(t("kindergarten_added"))
                st.rerun()
            else:
                st.error(t("fill_required"))
