"""
test_s00_diagnostics.py — Диагностические тесты

Эти тесты НЕ проверяют функциональность.
Они сохраняют скриншоты и HTML страницы чтобы понять
реальную структуру приложения и исправить селекторы.

Запускай ПЕРВЫМ при проблемах с другими тестами:
    py -m pytest tests_selenium/test_s00_diagnostics.py -v -s
"""

import time
import os
from selenium.webdriver.common.by import By
from conftest import APP_URL, TEST_EMAIL, TEST_PASSWORD, wait_for, streamlit_ready

DIAG_DIR = os.path.join(os.path.dirname(__file__), "diag_output")


def save_diag(driver, name):
    """Сохраняет скриншот и HTML страницы в папку diag_output/."""
    os.makedirs(DIAG_DIR, exist_ok=True)
    driver.save_screenshot(os.path.join(DIAG_DIR, f"{name}.png"))
    with open(os.path.join(DIAG_DIR, f"{name}.html"), "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"\n📸 Скриншот: tests_selenium/diag_output/{name}.png")
    print(f"📄 HTML:     tests_selenium/diag_output/{name}.html")


class TestDiagnostics:

    def test_01_login_page_structure(self, driver):
        """Сохраняет скриншот страницы входа и выводит все data-testid."""
        driver.get(APP_URL)
        streamlit_ready(driver)
        save_diag(driver, "01_login_page")

        # Выводим все элементы с data-testid
        elements = driver.find_elements(By.XPATH, "//*[@data-testid]")
        testids = set(e.get_attribute("data-testid") for e in elements)
        print(f"\n🔍 Все data-testid на странице входа:")
        for tid in sorted(testids):
            print(f"   {tid}")

        # Выводим все кнопки
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\n🔘 Кнопки ({len(buttons)}):")
        for b in buttons[:10]:
            print(f"   '{b.text[:50]}'")

        assert True  # диагностический тест всегда проходит

    def test_02_after_login_structure(self, driver):
        """Сохраняет скриншот ПОСЛЕ входа и выводит структуру страницы."""
        driver.get(APP_URL)
        streamlit_ready(driver)

        # Входим
        email_field = wait_for(driver, By.XPATH, "//input[@type='text']")
        email_field.send_keys(TEST_EMAIL)
        pass_field = wait_for(driver, By.XPATH, "//input[@type='password']")
        pass_field.send_keys(TEST_PASSWORD)
        btn = wait_for(driver, By.XPATH,
            "//button[.//p[contains(text(),'Войти') or contains(text(),'Sign In')]]")
        btn.click()
        time.sleep(5)

        save_diag(driver, "02_after_login")

        # Выводим все data-testid
        elements = driver.find_elements(By.XPATH, "//*[@data-testid]")
        testids = set(e.get_attribute("data-testid") for e in elements)
        print(f"\n🔍 Все data-testid после входа:")
        for tid in sorted(testids):
            print(f"   {tid}")

        # Ищем sidebar любым способом
        for selector in ["stSidebar", "stSidebarContent", "stSidebarNav"]:
            found = driver.find_elements(By.XPATH, f"//*[@data-testid='{selector}']")
            print(f"\n   data-testid='{selector}': найдено {len(found)}")

        # Все ссылки <a>
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"\n🔗 Ссылки ({len(links)}):")
        for lnk in links[:15]:
            print(f"   href='{lnk.get_attribute('href')}' text='{lnk.text[:40]}'")

        # Все кнопки
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\n🔘 Кнопки ({len(buttons)}):")
        for b in buttons[:15]:
            print(f"   '{b.text[:60]}'")

        # nav элементы
        navs = driver.find_elements(By.TAG_NAME, "nav")
        print(f"\n🗂 Nav элементов: {len(navs)}")
        for n in navs:
            print(f"   class='{n.get_attribute('class')}' text='{n.text[:80]}'")

        assert True

    def test_03_page_source_keywords(self, driver):
        """Проверяет наличие ключевых слов в HTML после входа."""
        driver.get(APP_URL)
        streamlit_ready(driver)

        email_field = wait_for(driver, By.XPATH, "//input[@type='text']")
        email_field.send_keys(TEST_EMAIL)
        pass_field = wait_for(driver, By.XPATH, "//input[@type='password']")
        pass_field.send_keys(TEST_PASSWORD)
        btn = wait_for(driver, By.XPATH,
            "//button[.//p[contains(text(),'Войти') or contains(text(),'Sign In')]]")
        btn.click()
        time.sleep(5)

        src = driver.page_source

        keywords = [
            "stSidebar", "stSidebarContent", "stSidebarNav",
            "stAlert", "Выйти", "Sign Out",
            "admin@kms.com", "Солнышко", "Радуга",
            "sidebar", "navigation",
        ]
        print("\n🔍 Поиск ключевых слов в page_source:")
        for kw in keywords:
            found = kw in src
            mark = "✅" if found else "❌"
            print(f"   {mark} '{kw}'")

        assert True
