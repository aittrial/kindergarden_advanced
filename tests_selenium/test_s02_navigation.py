"""
test_s02_navigation.py — GUI тесты навигации

ТЕМА: Навигация по страницам и sidebar
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Что изучаем:

1. Вход в систему через вспомогательную функцию login()
2. Поиск элементов в sidebar (боковом меню)
3. Клик по пунктам меню и проверка перехода

ВАЖНО о структуре Streamlit приложения:
  - После входа суперадмин видит список садиков
  - Sidebar появляется СРАЗУ после входа (содержит email + настройки)
  - Пункты навигации (Дети, Посещаемость...) появляются только ПОСЛЕ входа в садик
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
from selenium.webdriver.common.by import By

from conftest import APP_URL, TEST_EMAIL, wait_for, login


def login_and_enter_kindergarten(driver):
    """
    Входим в систему и входим в первый садик.
    Используется в тестах, которым нужен полный dashboard с навигацией.
    """
    login(driver)
    time.sleep(3)

    # Ищем кнопку "Войти →" для первого садика
    try:
        enter_btn = wait_for(driver, By.XPATH,
            "//button[.//p[contains(text(), '→')]]", timeout=8)
        enter_btn.click()
        time.sleep(4)
    except Exception:
        pass  # Уже в садике


class TestSidebarNavigation:
    """Тесты навигации через боковое меню."""

    def test_sidebar_visible_after_login(self, driver):
        """
        ТЕСТ 1: После входа боковое меню (sidebar) отображается.

        В Streamlit sidebar находится в div с data-testid="stSidebar".
        Sidebar виден сразу после входа — ещё на экране выбора садика.
        """
        login(driver)
        time.sleep(3)

        sidebar = wait_for(driver, By.XPATH,
            "//*[@data-testid='stSidebar']", timeout=15)

        assert sidebar.is_displayed(), "Sidebar не отображается после входа"
        print("\n✅ Sidebar отображается")

    def test_user_email_in_sidebar(self, driver):
        """
        ТЕСТ 2: Email пользователя отображается в sidebar.

        После входа в sidebar показывается email текущего пользователя.
        """
        login(driver)
        time.sleep(3)

        sidebar = wait_for(driver, By.XPATH,
            "//*[@data-testid='stSidebar']", timeout=15)

        # Даём время на полный рендер sidebar
        time.sleep(2)
        sidebar_text = sidebar.text

        assert TEST_EMAIL in sidebar_text, (
            f"Email '{TEST_EMAIL}' не найден в sidebar.\n"
            f"Содержимое sidebar: '{sidebar_text[:300]}'"
        )
        print(f"\n✅ Email пользователя в sidebar: {TEST_EMAIL}")

    def test_logout_button_in_sidebar(self, driver):
        """
        ТЕСТ 3: Кнопка выхода есть в sidebar.

        В sidebar должна быть кнопка "Выйти" или "Sign Out".
        """
        login(driver)
        time.sleep(3)

        logout_btn = wait_for(driver, By.XPATH,
            "//button[.//p[contains(text(), 'Выйти') or contains(text(), 'Sign Out')]]",
            timeout=15)

        assert logout_btn.is_displayed()
        print(f"\n✅ Кнопка выхода найдена")

    def test_logout_works(self, driver):
        """
        ТЕСТ 4: Нажатие "Выйти" возвращает на страницу входа.
        """
        login(driver)
        time.sleep(3)

        logout_btn = wait_for(driver, By.XPATH,
            "//button[.//p[contains(text(), 'Выйти') or contains(text(), 'Sign Out')]]",
            timeout=15)
        logout_btn.click()
        time.sleep(3)

        page_src = driver.page_source
        assert (
            "Войти" in page_src or "Sign In" in page_src
        ), "После выхода не показывается страница входа"
        print("\n✅ Выход из системы работает")

    def test_kindergarten_list_visible_for_superadmin(self, driver):
        """
        ТЕСТ 5: Суперадмин видит список садиков после входа.

        Суперадмин после входа попадает на страницу выбора садика.
        Там отображаются карточки с названиями садиков из seed.py.
        """
        login(driver)
        time.sleep(4)

        page_src = driver.page_source

        has_kindergartens = (
            "Войти" in page_src or
            "Enter" in page_src or
            "Солнышко" in page_src or
            "Радуга" in page_src or
            "Звёздочка" in page_src or
            "садик" in page_src.lower()
        )
        assert has_kindergartens, (
            "Суперадмин не видит список садиков.\n"
            f"Содержимое страницы (первые 500 символов):\n{page_src[:500]}"
        )
        print("\n✅ Список садиков отображается")

    def test_enter_kindergarten(self, driver):
        """
        ТЕСТ 6: Суперадмин может войти в садик нажав "Войти →".
        """
        login(driver)
        time.sleep(3)

        enter_btn = wait_for(driver, By.XPATH,
            "//button[.//p[contains(text(), '→')]]", timeout=10)
        enter_btn.click()
        time.sleep(4)

        page_src = driver.page_source
        in_dashboard = (
            "Добро пожаловать" in page_src or
            "Welcome" in page_src or
            "Посещаемость" in page_src or
            "Attendance" in page_src or
            "Дети" in page_src
        )
        assert in_dashboard, "Не попали в dashboard садика"
        print("\n✅ Вход в садик работает")

    def test_navigation_menu_items(self, driver):
        """
        ТЕСТ 7: После входа в садик в sidebar появляются пункты навигации.

        Пункты меню: Дети, Посещаемость, Продукты, Расходы, Отчёты, Оплата.
        """
        login_and_enter_kindergarten(driver)

        sidebar = wait_for(driver, By.XPATH,
            "//*[@data-testid='stSidebar']", timeout=15)
        time.sleep(2)
        sidebar_text = sidebar.text

        expected_items = ["Дети", "Посещаемость", "Продукты", "Расходы"]
        found = [item for item in expected_items if item in sidebar_text]

        assert len(found) >= 2, (
            f"Ожидали пункты меню {expected_items}, нашли только: {found}.\n"
            f"Sidebar содержит: '{sidebar_text[:400]}'"
        )
        print(f"\n✅ Найдены пункты меню: {found}")
