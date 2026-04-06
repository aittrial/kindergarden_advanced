"""
test_s03_children.py — GUI тесты страницы "Дети"

ТЕМА: Работа с формами и таблицами
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Что изучаем:

1. Клик по вкладкам (tabs) в Streamlit
2. Заполнение форм с несколькими полями
3. Проверка появления данных на странице
4. driver.find_elements() — поиск нескольких элементов
5. Скроллинг страницы — element.location_once_scrolled_into_view
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from conftest import APP_URL, wait_for, streamlit_ready, login


def go_to_children_page(driver):
    """
    Вспомогательная функция: войти в систему и перейти на страницу Дети.

    Используется в нескольких тестах, поэтому выделена в отдельную функцию.
    """
    login(driver)
    time.sleep(2)

    # Входим в первый садик (нажимаем "Войти →")
    try:
        enter_btn = wait_for(driver, By.XPATH,
            "//button[.//p[contains(text(), '→')]]", timeout=5)
        enter_btn.click()
        time.sleep(3)
    except Exception:
        pass

    # Ищем пункт "Дети" в боковом меню и кликаем
    children_link = wait_for(driver, By.XPATH,
        "//*[@data-testid='stSidebar']//*[contains(text(), 'Дети') or contains(text(), 'Children')]")
    children_link.click()
    time.sleep(2)


class TestChildrenPage:
    """Тесты страницы управления детьми."""

    def test_children_page_loads(self, driver):
        """
        ТЕСТ 1: Страница "Дети" открывается.

        Что делает:
          1. Входит в систему
          2. Переходит в первый садик
          3. Кликает по разделу "Дети"
          4. Проверяет что страница загрузилась
        """
        go_to_children_page(driver)

        page_src = driver.page_source
        assert (
            "Дети" in page_src or "Children" in page_src
        ), "Страница Дети не загрузилась"
        print("\n✅ Страница Дети загрузилась")

    def test_children_tabs_visible(self, driver):
        """
        ТЕСТ 2: Вкладки "Список детей" и "Добавить ребёнка" видны.

        Streamlit вкладки (st.tabs) рендерятся как кнопки с role="tab".
        """
        go_to_children_page(driver)

        # Ищем все вкладки на странице
        tabs = driver.find_elements(By.XPATH, "//button[@role='tab']")

        assert len(tabs) >= 2, f"Ожидали минимум 2 вкладки, нашли: {len(tabs)}"
        print(f"\n✅ Найдено {len(tabs)} вкладок")

    def test_children_list_displayed(self, driver):
        """
        ТЕСТ 3: Список детей отображается на странице.

        После seed.py в каждом садике есть дети.
        Проверяем, что таблица или список виден.
        """
        go_to_children_page(driver)

        page_src = driver.page_source

        # Ищем признаки списка детей — имена из seed.py
        has_children = (
            "Анна" in page_src or
            "Иван" in page_src or
            "Мария" in page_src or
            "активный" in page_src or
            "active" in page_src.lower() or
            "младшая" in page_src or
            "Junior" in page_src
        )
        assert has_children, (
            "Список детей не найден на странице. "
            "Убедитесь, что seed.py был запущен."
        )
        print("\n✅ Список детей отображается")

    def test_add_child_tab_click(self, driver):
        """
        ТЕСТ 4: Вкладка "Добавить ребёнка" открывается по клику.

        Что делает:
          1. Переходит на страницу детей
          2. Находит вкладку "Добавить"
          3. Кликает на неё
          4. Проверяет, что форма появилась
        """
        go_to_children_page(driver)

        # Ищем вкладку "Добавить ребёнка"
        add_tab = wait_for(driver, By.XPATH,
            "//button[@role='tab' and ("
            "contains(., 'Добавить') or contains(., 'Add'))]")
        add_tab.click()
        time.sleep(1)

        # После клика должна появиться форма с полями
        page_src = driver.page_source
        has_form = (
            "Имя" in page_src or
            "First Name" in page_src or
            "Фамилия" in page_src or
            "Last Name" in page_src
        )
        assert has_form, "Форма добавления ребёнка не появилась"
        print("\n✅ Форма добавления ребёнка открылась")

    def test_add_child_form_has_fields(self, driver):
        """
        ТЕСТ 5: Форма добавления ребёнка содержит необходимые поля.

        Проверяем наличие обязательных полей: Имя, Фамилия.
        """
        go_to_children_page(driver)

        # Открываем вкладку добавления
        add_tab = wait_for(driver, By.XPATH,
            "//button[@role='tab' and (contains(., 'Добавить') or contains(., 'Add'))]")
        add_tab.click()
        time.sleep(1.5)

        # Проверяем наличие текстовых полей
        inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
        assert len(inputs) >= 2, (
            f"Ожидали минимум 2 текстовых поля в форме, нашли: {len(inputs)}"
        )
        print(f"\n✅ В форме найдено {len(inputs)} текстовых полей")

    def test_filter_by_group(self, driver):
        """
        ТЕСТ 6: Фильтр по группе отображается на странице.

        На странице детей есть выпадающий список для фильтрации по группе.
        """
        go_to_children_page(driver)

        # Streamlit selectbox = div с data-baseweb="select"
        selects = driver.find_elements(By.XPATH,
            "//div[@data-baseweb='select']")

        assert len(selects) >= 1, "Фильтр по группе не найден"
        print(f"\n✅ Найдено {len(selects)} фильтров на странице")
