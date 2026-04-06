"""
test_s01_login.py — GUI тесты страницы входа

ТЕМА: Базовые Selenium операции
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Что изучаем:

1. driver.get(url)          — открыть страницу
2. find_element / By.XPATH  — найти элемент на странице
3. element.send_keys()      — ввести текст
4. element.click()          — кликнуть
5. driver.page_source        — HTML страницы для проверки текста
6. WebDriverWait             — ждать появления элемента

ВАЖНО: Streamlit — React-приложение.
Элементы загружаются асинхронно — всегда используй wait_for()!
Никогда не используй find_element() напрямую без ожидания.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from conftest import APP_URL, TEST_EMAIL, TEST_PASSWORD, wait_for, wait_for_text, streamlit_ready


class TestLoginPage:
    """Тесты страницы входа."""

    def test_page_loads(self, driver):
        """
        ТЕСТ 1: Страница открывается и показывает заголовок.

        Что делает:
          1. Открывает http://localhost:8501
          2. Ждёт появления заголовка приложения

        Проверяет: заголовок содержит "детским садом" или "Kindergarten"
        """
        driver.get(APP_URL)
        streamlit_ready(driver)

        # Ищем заголовок — он содержит название системы
        title_element = wait_for(driver, By.XPATH,
            "//h1[contains(text(), 'детским садом') or contains(text(), 'Kindergarten')]")

        assert title_element is not None, "Заголовок приложения не найден"
        print(f"\n✅ Заголовок: {title_element.text}")

    def test_login_form_visible(self, driver):
        """
        ТЕСТ 2: Форма входа отображается на странице.

        Что делает:
          1. Открывает страницу
          2. Ищет поля Email и Password

        Проверяет: оба поля присутствуют на странице
        """
        driver.get(APP_URL)
        streamlit_ready(driver)

        # Ищем поле Email
        email_field = wait_for(driver, By.XPATH,
            "//input[@aria-label='Email' or @placeholder='Email']")
        assert email_field.is_displayed(), "Поле Email не отображается"

        # Ищем поле Password (type="password" — скрывает символы)
        pass_field = wait_for(driver, By.XPATH, "//input[@type='password']")
        assert pass_field.is_displayed(), "Поле Password не отображается"

        print("\n✅ Форма входа отображается корректно")

    def test_login_button_visible(self, driver):
        """
        ТЕСТ 3: Кнопка входа отображается.

        Streamlit рендерит кнопки как <button> с текстом внутри <p>.
        Поэтому ищем button, внутри которого есть текст "Войти" или "Sign In".
        """
        driver.get(APP_URL)
        streamlit_ready(driver)

        btn = wait_for(driver, By.XPATH,
            "//button[.//p[contains(text(), 'Войти') or contains(text(), 'Sign In')]]")

        assert btn.is_displayed(), "Кнопка входа не отображается"
        print(f"\n✅ Кнопка входа найдена: '{btn.text}'")

    def test_successful_login(self, driver):
        """
        ТЕСТ 4: Успешный вход в систему.

        Что делает:
          1. Вводит правильный email и пароль
          2. Нажимает кнопку входа
          3. Проверяет, что мы попали на следующую страницу

        Предусловие: суперадмин admin@kms.com с паролем admin123 должен существовать.
        Создаётся через seed.py.
        """
        driver.get(APP_URL)
        streamlit_ready(driver)

        # Вводим email
        email_field = wait_for(driver, By.XPATH,
            "//input[@aria-label='Email' or @placeholder='Email']")
        email_field.clear()
        email_field.send_keys(TEST_EMAIL)

        # Вводим пароль
        pass_field = wait_for(driver, By.XPATH, "//input[@type='password']")
        pass_field.clear()
        pass_field.send_keys(TEST_PASSWORD)

        # Кликаем Войти
        login_btn = wait_for(driver, By.XPATH,
            "//button[.//p[contains(text(), 'Войти') or contains(text(), 'Sign In')]]")
        login_btn.click()

        # Ждём загрузки — должны увидеть страницу управления садиками
        time.sleep(3)

        # После входа суперадмин видит "Управление садиками" или список садиков
        page_src = driver.page_source
        logged_in = (
            "садик" in page_src.lower() or
            "kindergarten" in page_src.lower() or
            "Войти →" in page_src or
            "Enter →" in page_src
        )
        assert logged_in, "После входа не видно главной страницы"
        print(f"\n✅ Вход выполнен успешно, URL: {driver.current_url}")

    def test_wrong_password_shows_error(self, driver):
        """
        ТЕСТ 5: Неправильный пароль — показывается сообщение об ошибке.

        Что делает:
          1. Вводит правильный email, но НЕПРАВИЛЬНЫЙ пароль
          2. Нажимает кнопку входа
          3. Проверяет, что появилось сообщение об ошибке

        Streamlit показывает ошибки в компоненте st.error() —
        они отображаются в div с атрибутом data-testid="stAlert".
        """
        driver.get(APP_URL)
        streamlit_ready(driver)

        email_field = wait_for(driver, By.XPATH,
            "//input[@aria-label='Email' or @placeholder='Email']")
        email_field.clear()
        email_field.send_keys(TEST_EMAIL)

        pass_field = wait_for(driver, By.XPATH, "//input[@type='password']")
        pass_field.clear()
        pass_field.send_keys("НЕПРАВИЛЬНЫЙ_ПАРОЛЬ_999")

        login_btn = wait_for(driver, By.XPATH,
            "//button[.//p[contains(text(), 'Войти') or contains(text(), 'Sign In')]]")
        login_btn.click()

        time.sleep(2)

        # Streamlit показывает ошибки в alert-блоке
        error_element = wait_for(driver, By.XPATH,
            "//*[@data-testid='stAlert' or contains(@class, 'error')]")

        assert error_element is not None, "Сообщение об ошибке не появилось"
        print(f"\n✅ Ошибка отображается: '{error_element.text[:50]}'")

    def test_empty_fields_shows_error(self, driver):
        """
        ТЕСТ 6: Пустые поля при входе — показывается ошибка.

        Что делает:
          1. Ничего не вводит
          2. Нажимает кнопку входа
          3. Проверяет наличие ошибки
        """
        driver.get(APP_URL)
        streamlit_ready(driver)

        # Кликаем сразу, без ввода данных
        login_btn = wait_for(driver, By.XPATH,
            "//button[.//p[contains(text(), 'Войти') or contains(text(), 'Sign In')]]")
        login_btn.click()

        time.sleep(2)

        # Должна появиться ошибка
        error = wait_for(driver, By.XPATH,
            "//*[@data-testid='stAlert']")
        assert error is not None
        print(f"\n✅ Валидация пустых полей работает")

    def test_language_selector_visible(self, driver):
        """
        ТЕСТ 7: Переключатель языка доступен ДО входа в систему.

        На странице входа в левом углу есть выпадающий список для выбора языка.
        Проверяем, что он виден и доступен.
        """
        driver.get(APP_URL)
        streamlit_ready(driver)

        # Streamlit selectbox рендерится как div с role="combobox"
        selects = driver.find_elements(By.XPATH, "//div[@data-baseweb='select']")

        assert len(selects) >= 1, "Переключатель языка не найден"
        print(f"\n✅ Найдено {len(selects)} выпадающих списков на странице входа")


class TestPageTitle:
    """Тесты заголовка и метаданных страницы."""

    def test_browser_tab_title(self, driver):
        """
        ТЕСТ 8: Заголовок вкладки браузера правильный.

        driver.title — возвращает текст из <title> HTML документа.
        В Streamlit это задаётся через st.set_page_config(page_title=...).
        """
        driver.get(APP_URL)
        streamlit_ready(driver)

        title = driver.title
        assert "Kindergarten" in title or "детск" in title.lower(), (
            f"Неожиданный заголовок вкладки: '{title}'"
        )
        print(f"\n✅ Заголовок вкладки: '{title}'")

    def test_page_url(self, driver):
        """
        ТЕСТ 9: URL страницы входа правильный.
        """
        driver.get(APP_URL)
        streamlit_ready(driver)

        assert "localhost:8501" in driver.current_url
        print(f"\n✅ URL: {driver.current_url}")
