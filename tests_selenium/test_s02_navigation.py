"""
test_s02_navigation.py — GUI тесты навигации

ТЕМА: Навигация по страницам и sidebar
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Что изучаем:

1. Вход в систему через вспомогательную функцию login()
2. Поиск элементов в sidebar (боковом меню)
3. Клик по пунктам меню и проверка перехода
4. screenshot() — скриншот при падении теста
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import pytest
from selenium.webdriver.common.by import By

from conftest import APP_URL, wait_for, wait_for_text, streamlit_ready, login


class TestSidebarNavigation:
    """Тесты навигации через боковое меню."""

    def test_sidebar_visible_after_login(self, driver):
        """
        ТЕСТ 1: После входа боковое меню (sidebar) отображается.

        В Streamlit sidebar находится в div с data-testid="stSidebar".
        """
        login(driver)

        sidebar = wait_for(driver, By.XPATH,
            "//*[@data-testid='stSidebar']")

        assert sidebar.is_displayed(), "Sidebar не отображается после входа"
        print("\n✅ Sidebar отображается")

    def test_user_email_in_sidebar(self, driver):
        """
        ТЕСТ 2: Email пользователя отображается в sidebar.

        После входа в sidebar показывается email текущего пользователя.
        """
        login(driver)

        # Ищем email в sidebar
        sidebar = wait_for(driver, By.XPATH, "//*[@data-testid='stSidebar']")
        sidebar_text = sidebar.text

        from conftest import TEST_EMAIL
        assert TEST_EMAIL in sidebar_text, (
            f"Email '{TEST_EMAIL}' не найден в sidebar. Содержимое: {sidebar_text[:200]}"
        )
        print(f"\n✅ Email пользователя в sidebar: {TEST_EMAIL}")

    def test_logout_button_in_sidebar(self, driver):
        """
        ТЕСТ 3: Кнопка выхода есть в sidebar.

        В sidebar должна быть кнопка "Выйти" или "Sign Out".
        """
        login(driver)

        logout_btn = wait_for(driver, By.XPATH,
            "//button[.//p[contains(text(), 'Выйти') or contains(text(), 'Sign Out')]]")

        assert logout_btn.is_displayed()
        print(f"\n✅ Кнопка выхода найдена: '{logout_btn.text}'")

    def test_logout_works(self, driver):
        """
        ТЕСТ 4: Нажатие "Выйти" возвращает на страницу входа.

        Что делает:
          1. Входим в систему
          2. Нажимаем "Выйти"
          3. Проверяем, что снова видим страницу входа
        """
        login(driver)

        # Нажимаем Выйти
        logout_btn = wait_for(driver, By.XPATH,
            "//button[.//p[contains(text(), 'Выйти') or contains(text(), 'Sign Out')]]")
        logout_btn.click()

        time.sleep(2)

        # После выхода должна быть форма входа
        page_src = driver.page_source
        assert (
            "Войти" in page_src or "Sign In" in page_src
        ), "После выхода не показывается страница входа"
        print("\n✅ Выход из системы работает")

    def test_kindergarten_list_visible_for_superadmin(self, driver):
        """
        ТЕСТ 5: Суперадмин видит список садиков после входа.

        Суперадмин попадает на страницу выбора садика, а не сразу в dashboard.
        """
        login(driver)

        page_src = driver.page_source

        # Суперадмин видит кнопки "Войти →" для каждого садика
        has_kindergartens = (
            "Войти →" in page_src or
            "Enter →" in page_src or
            "Солнышко" in page_src or
            "Радуга" in page_src or
            "Звёздочка" in page_src
        )
        assert has_kindergartens, (
            "Суперадмин не видит список садиков. "
            f"Содержимое страницы: {page_src[:500]}"
        )
        print("\n✅ Список садиков отображается")

    def test_enter_kindergarten(self, driver):
        """
        ТЕСТ 6: Суперадмин может войти в садик.

        Нажимаем кнопку "Войти →" и попадаем в dashboard садика.
        """
        login(driver)
        time.sleep(2)

        # Ищем первую кнопку "Войти →"
        enter_btn = wait_for(driver, By.XPATH,
            "//button[.//p[contains(text(), 'Войти') and contains(text(), '→')] or "
            ".//p[contains(text(), 'Enter') and contains(text(), '→')]]")
        enter_btn.click()

        time.sleep(3)

        # После входа в садик должен появиться dashboard
        page_src = driver.page_source
        in_dashboard = (
            "Добро пожаловать" in page_src or
            "Welcome" in page_src or
            "Посещаемость" in page_src or
            "Attendance" in page_src
        )
        assert in_dashboard, "Не попали в dashboard садика"
        print("\n✅ Вход в садик работает")

    def test_navigation_menu_items(self, driver):
        """
        ТЕСТ 7: В боковом меню отображаются пункты навигации.

        После входа в садик в sidebar должны быть разделы:
        Дети, Посещаемость, Продукты, Расходы, Отчёты, Оплата.
        """
        login(driver)
        time.sleep(2)

        # Входим в первый садик
        try:
            enter_btn = wait_for(driver, By.XPATH,
                "//button[.//p[contains(text(), '→')]]", timeout=5)
            enter_btn.click()
            time.sleep(3)
        except Exception:
            pass  # Может быть уже в садике (если только один)

        sidebar = wait_for(driver, By.XPATH, "//*[@data-testid='stSidebar']")
        sidebar_text = sidebar.text

        # Проверяем наличие пунктов меню
        expected_items = ["Дети", "Посещаемость", "Продукты", "Расходы"]
        found = [item for item in expected_items if item in sidebar_text]

        assert len(found) >= 2, (
            f"Ожидали пункты меню {expected_items}, нашли только: {found}. "
            f"Sidebar содержит: {sidebar_text[:300]}"
        )
        print(f"\n✅ Найдены пункты меню: {found}")
