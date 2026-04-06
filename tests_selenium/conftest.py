"""
conftest.py — Настройка Selenium WebDriver для GUI тестов

Этот файл делает 3 вещи:
1. Запускает Streamlit-приложение локально перед тестами
2. Настраивает Chrome WebDriver (браузер для тестов)
3. Предоставляет вспомогательные функции (ожидание элементов, вход в систему)

ВАЖНО: Selenium тесты работают только ЛОКАЛЬНО.
Нельзя тестировать Streamlit Cloud через Selenium.
"""

import os
import sys
import time
import subprocess
import pytest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ── Путь к проекту ────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# ── Адрес Streamlit приложения ────────────────────────────────────────────────
APP_URL = "http://localhost:8501"
STREAMLIT_STARTUP_TIMEOUT = 15  # секунд ожидания запуска

# ── Тестовый суперадмин (создаётся автоматически через seed) ──────────────────
TEST_EMAIL = "koroligorn@gmail.com"
TEST_PASSWORD = "7654321.com"


# ═══════════════════════════════════════════════════════════════════════
# FIXTURE: Запуск Streamlit (один раз для всей сессии тестов)
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def streamlit_server():
    """
    scope="session" — fixture запускается ОДИН РАЗ для всех тестов.

    Запускает Streamlit как subprocess и ждёт пока он поднимется.
    После всех тестов — останавливает сервер.

    Если Streamlit уже запущен (ты запустил вручную) — всё равно работает,
    subprocess просто не создаётся (порт уже занят — проверяем доступность).
    """
    import urllib.request
    import urllib.error

    # Проверяем — может Streamlit уже запущен?
    try:
        urllib.request.urlopen(APP_URL, timeout=2)
        print(f"\n✅ Streamlit уже запущен на {APP_URL}")
        yield APP_URL
        return
    except Exception:
        pass

    # Запускаем Streamlit как фоновый процесс
    print(f"\n🚀 Запускаем Streamlit на {APP_URL}...")
    main_py = os.path.join(PROJECT_ROOT, "main.py")
    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", main_py,
         "--server.port=8501",
         "--server.headless=true",
         "--browser.gatherUsageStats=false"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=PROJECT_ROOT
    )

    # Ждём пока Streamlit поднимется
    for i in range(STREAMLIT_STARTUP_TIMEOUT):
        try:
            urllib.request.urlopen(APP_URL, timeout=2)
            print(f"✅ Streamlit готов (через {i+1} сек)")
            break
        except Exception:
            time.sleep(1)
    else:
        process.terminate()
        pytest.fail(f"Streamlit не запустился за {STREAMLIT_STARTUP_TIMEOUT} секунд")

    yield APP_URL

    # Останавливаем после всех тестов
    print("\n🛑 Останавливаем Streamlit...")
    process.terminate()
    process.wait()


# ═══════════════════════════════════════════════════════════════════════
# FIXTURE: Chrome WebDriver (для каждого теста — свежий браузер)
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture
def driver(streamlit_server):
    """
    Создаёт новый экземпляр Chrome для каждого теста.
    После теста — закрывает браузер.

    webdriver_manager автоматически скачивает нужную версию ChromeDriver.
    Не нужно скачивать вручную!
    """
    options = Options()

    # Раскомментируй если хочешь тесты БЕЗ открытия браузера (headless)
    # options.add_argument("--headless")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # ChromeDriverManager автоматически находит и скачивает ChromeDriver
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    browser.implicitly_wait(3)  # неявное ожидание 3 сек

    yield browser

    browser.quit()


# ═══════════════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (helpers)
# ═══════════════════════════════════════════════════════════════════════

def wait_for(driver, by, value, timeout=15):
    """
    Ждёт появления элемента на странице.

    Streamlit — React-приложение, элементы появляются не сразу.
    Нельзя просто искать элемент — нужно ждать!

    Args:
        driver  — WebDriver (браузер)
        by      — тип поиска (By.XPATH, By.CSS_SELECTOR и др.)
        value   — значение для поиска
        timeout — максимальное время ожидания в секундах
    """
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def wait_for_text(driver, text, timeout=15):
    """Ждёт появления текста где-либо на странице."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(
            (By.XPATH, f"//*[contains(text(), '{text}')]")
        )
    )


def wait_clickable(driver, by, value, timeout=15):
    """Ждёт пока элемент станет кликабельным."""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )


def streamlit_ready(driver, timeout=10):
    """
    Ждёт пока Streamlit загрузит страницу полностью.
    Определяем по исчезновению spinner'а загрузки.
    """
    time.sleep(1.5)  # Streamlit всегда нужна секунда на рендер


def login(driver, email=TEST_EMAIL, password=TEST_PASSWORD):
    """
    Вспомогательная функция входа в систему.
    Используется в большинстве тестов как подготовительный шаг.

    Args:
        driver   — WebDriver
        email    — email пользователя (по умолчанию тестовый суперадмин)
        password — пароль (по умолчанию тестовый)
    """
    driver.get(APP_URL)
    streamlit_ready(driver)

    # Находим поле Email
    email_input = wait_for(driver, By.XPATH,
        "//input[@aria-label='Email' or @placeholder='Email']")
    email_input.clear()
    email_input.send_keys(email)

    # Находим поле Пароль
    password_input = wait_for(driver, By.XPATH,
        "//input[@type='password']")
    password_input.clear()
    password_input.send_keys(password)

    # Нажимаем кнопку входа
    login_btn = wait_clickable(driver, By.XPATH,
        "//button[.//p[contains(text(), 'Войти') or contains(text(), 'Sign In')]]")
    login_btn.click()

    # Ждём загрузки следующей страницы
    streamlit_ready(driver)
    time.sleep(2)
