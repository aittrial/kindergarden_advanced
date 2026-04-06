# Руководство по Selenium WebDriver тестированию
# Kindergarten Management System — GUI Tests

**Версия:** 1.0 | **Дата:** Апрель 2026  
**Для кого:** Студенты курса QA Testing

---

## Содержание
1. [Что такое Selenium?](#1-что-такое-selenium)
2. [Установка](#2-установка)
3. [Подготовка приложения](#3-подготовка-приложения)
4. [Запуск тестов](#4-запуск-тестов)
5. [Структура тестов](#5-структура-тестов)
6. [Описание тестовых файлов](#6-описание-тестовых-файлов)
7. [Концепции Selenium](#7-концепции-selenium)
8. [Частые проблемы и решения](#8-частые-проблемы-и-решения)
9. [Задания для студентов](#9-задания-для-студентов)

---

## 1. Что такое Selenium?

**Selenium** — инструмент для автоматизации браузера. Он управляет Chrome так же, как это делает человек: открывает страницы, кликает кнопки, вводит текст и проверяет результат.

```
pytest запускает Streamlit → Selenium открывает Chrome → 
кликает по кнопкам → проверяет текст на экране
```

### Отличие от PyTest (обычных тестов)

| PyTest (unit/integration) | Selenium (GUI) |
|--------------------------|----------------|
| Тестирует функции Python | Тестирует то, что видит пользователь |
| Не нужен браузер | Открывает реальный браузер Chrome |
| Быстро (секунды) | Медленно (секунды на каждый клик) |
| SQLite in-memory | Нужен запущенный Streamlit |
| Не нужен интернет | Нужен локальный Streamlit |

### Важное ограничение
Selenium тесты работают **только локально**.  
Нельзя тестировать Streamlit Cloud через Selenium.

---

## 2. Установка

### Шаг 1: Google Chrome
Убедись, что Google Chrome установлен.  
Скачать: https://www.google.com/chrome/

### Шаг 2: Python-библиотеки
```bash
py -m pip install selenium webdriver-manager
```

**Что устанавливается:**
- `selenium` — основная библиотека для управления браузером
- `webdriver-manager` — автоматически скачивает ChromeDriver нужной версии

> **ChromeDriver не нужно скачивать вручную!**  
> `webdriver-manager` делает это автоматически при первом запуске.

### Шаг 3: Проверка установки
```bash
py -c "from selenium import webdriver; print('Selenium OK')"
py -c "from webdriver_manager.chrome import ChromeDriverManager; print('WebDriverManager OK')"
```

---

## 3. Подготовка приложения

### Шаг 1: Убедись, что база данных заполнена

Selenium тесты ожидают, что в базе есть тестовый суперадмин:
- **Email:** `admin@kms.com`
- **Пароль:** `admin123`

Если его нет — запусти seed через приложение:
1. Запусти Streamlit: `py -m streamlit run main.py`
2. Открой http://localhost:8501
3. Войди как суперадмин → **Детские сады (⚙️)** → **🛠 Инициализация базы данных** → **Сбросить и заполнить**

### Шаг 2: Вариант А — Streamlit запускается автоматически
Просто запускай тесты — conftest.py запустит Streamlit сам.

### Шаг 3: Вариант Б — Streamlit запущен вручную (рекомендуется для отладки)
Открой **два терминала**:

**Терминал 1** — запуск Streamlit:
```bash
cd C:\Users\RedmiBook\Documents\MyProjects\ClaudeCode_test\kindergarden
py -m streamlit run main.py
```

**Терминал 2** — запуск тестов:
```bash
cd C:\Users\RedmiBook\Documents\MyProjects\ClaudeCode_test\kindergarden
py -m pytest tests_selenium/ -v
```

---

## 4. Запуск тестов

> **ВАЖНО:** Всегда запускай из папки `kindergarden/`, а НЕ из `tests_selenium/`

```bash
cd C:\Users\RedmiBook\Documents\MyProjects\ClaudeCode_test\kindergarden
```

### Все selenium тесты
```bash
py -m pytest tests_selenium/ -v
```

### Каждый файл отдельно
```bash
py -m pytest tests_selenium/test_s01_login.py -v
py -m pytest tests_selenium/test_s02_navigation.py -v
py -m pytest tests_selenium/test_s03_children.py -v
py -m pytest tests_selenium/test_s04_language.py -v
```

### Один тест
```bash
py -m pytest tests_selenium/test_s01_login.py::TestLoginPage::test_successful_login -v
```

### Без открытия браузера (headless режим)
Раскомментируй в conftest.py строку:
```python
options.add_argument("--headless")
```
Затем запускай как обычно.

---

## 5. Структура тестов

```
kindergarden/
├── tests_selenium/
│   ├── conftest.py              ← Запуск Streamlit + настройка Chrome
│   ├── test_s01_login.py        ← Тесты страницы входа (9 тестов)
│   ├── test_s02_navigation.py   ← Тесты навигации и sidebar (7 тестов)
│   ├── test_s03_children.py     ← Тесты страницы Дети (6 тестов)
│   └── test_s04_language.py     ← Тесты переключения языка (9 тестов)
└── docs/
    └── SELENIUM_GUIDE_RU.md     ← Этот файл
```

---

## 6. Описание тестовых файлов

---

### conftest.py — Основа всех тестов

**Fixture `streamlit_server` (scope="session"):**
- Проверяет — не запущен ли Streamlit уже
- Если нет — запускает `main.py` как subprocess
- Ждёт до 15 секунд пока Streamlit поднимется
- После всех тестов — останавливает Streamlit

**Fixture `driver`:**
- Создаёт новый экземпляр Chrome для каждого теста
- `ChromeDriverManager().install()` — автоматически скачивает ChromeDriver
- После теста — закрывает браузер

**Вспомогательные функции:**
- `wait_for(driver, By.XPATH, "...")` — ждёт появления элемента (максимум 15 сек)
- `wait_for_text(driver, "текст")` — ждёт появления текста на странице
- `login(driver)` — выполняет вход под тестовым суперадмином

---

### test_s01_login.py — Страница входа

| Тест | Что проверяет |
|------|--------------|
| `test_page_loads` | Заголовок приложения виден |
| `test_login_form_visible` | Поля Email и Password отображаются |
| `test_login_button_visible` | Кнопка "Войти" присутствует |
| `test_successful_login` | Вход с правильным паролем переводит на главную |
| `test_wrong_password_shows_error` | Неправильный пароль показывает ошибку |
| `test_empty_fields_shows_error` | Пустые поля показывают ошибку валидации |
| `test_language_selector_visible` | Переключатель языка виден до входа |
| `test_browser_tab_title` | Заголовок вкладки браузера правильный |
| `test_page_url` | URL содержит localhost:8501 |

---

### test_s02_navigation.py — Навигация

| Тест | Что проверяет |
|------|--------------|
| `test_sidebar_visible_after_login` | Sidebar появляется после входа |
| `test_user_email_in_sidebar` | Email пользователя виден в sidebar |
| `test_logout_button_in_sidebar` | Кнопка "Выйти" есть в sidebar |
| `test_logout_works` | Нажатие "Выйти" возвращает на страницу входа |
| `test_kindergarten_list_visible_for_superadmin` | Суперадмин видит список садиков |
| `test_enter_kindergarten` | Вход в садик кнопкой "Войти →" работает |
| `test_navigation_menu_items` | Пункты меню (Дети, Посещаемость и др.) видны |

---

### test_s03_children.py — Страница Дети

| Тест | Что проверяет |
|------|--------------|
| `test_children_page_loads` | Страница Дети открывается |
| `test_children_tabs_visible` | Вкладки "Список" и "Добавить" видны |
| `test_children_list_displayed` | Список детей отображается (из seed) |
| `test_add_child_tab_click` | Клик по вкладке "Добавить" открывает форму |
| `test_add_child_form_has_fields` | Форма содержит поля ввода |
| `test_filter_by_group` | Фильтр по группе присутствует |

---

### test_s04_language.py — Язык и структура

| Тест | Что проверяет |
|------|--------------|
| `test_default_language_is_russian` | По умолчанию — русский язык |
| `test_language_selectors_on_login_page` | 2 переключателя на странице входа |
| `test_switch_to_english_on_login_page` | Переключение на английский работает |
| `test_english_login_button_text` | Кнопка меняет текст при смене языка |
| `test_settings_in_sidebar_after_login` | Настройки языка есть в sidebar |
| `test_currency_selector_on_login_page` | Переключатель валюты присутствует |
| `test_main_title_present` | Заголовок H1 есть на каждой странице |
| `test_streamlit_app_not_crashed` | Нет страницы с ошибкой |
| `test_responsive_layout` | Контент виден в разных разрешениях |

---

## 7. Концепции Selenium

### Поиск элементов

```python
from selenium.webdriver.common.by import By

# По XPATH — самый гибкий способ
driver.find_element(By.XPATH, "//button[contains(text(), 'Войти')]")

# По CSS selector
driver.find_element(By.CSS_SELECTOR, "input[type='password']")

# По тексту в элементе
driver.find_element(By.XPATH, "//*[text()='Точный текст']")
driver.find_element(By.XPATH, "//*[contains(text(), 'Часть текста')]")
```

### Ожидание (ОБЯЗАТЕЛЬНО для Streamlit!)

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ждём максимум 15 секунд
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, "//h1"))
)

# Или используем нашу обёртку:
wait_for(driver, By.XPATH, "//h1")
```

### Действия с элементами

```python
element = driver.find_element(By.XPATH, "//input")

element.click()              # кликнуть
element.send_keys("текст")  # ввести текст
element.clear()              # очистить поле
element.text                 # получить текст элемента
element.is_displayed()       # виден ли элемент
```

### Проверка содержимого страницы

```python
# Весь HTML страницы
page_src = driver.page_source
assert "Войти" in page_src

# Заголовок вкладки браузера
title = driver.title

# Текущий URL
url = driver.current_url
```

### Streamlit-специфичные selectors

```python
# Sidebar
"//*[@data-testid='stSidebar']"

# Alert (st.error / st.warning / st.success)
"//*[@data-testid='stAlert']"

# Selectbox (st.selectbox)
"//div[@data-baseweb='select']"

# Вкладки (st.tabs)
"//button[@role='tab']"

# Основной контент
"//*[@data-testid='stMainBlockContainer']"

# Кнопки Streamlit (текст внутри <p>)
"//button[.//p[contains(text(), 'Войти')]]"
```

---

## 8. Частые проблемы и решения

### "Chrome not found"
```
Решение: Установи Google Chrome с https://www.google.com/chrome/
```

### "TimeoutException: element not found"
```
Причина: Streamlit не успел отрендерить элемент.
Решение: Увеличь timeout в wait_for() или добавь time.sleep(2)
```

### "Streamlit не запустился за 15 секунд"
```
Причина: Порт 8501 занят или проблема с main.py.
Решение: Запусти Streamlit вручную в отдельном терминале:
  py -m streamlit run main.py
```

### "Тест упал, но я не понимаю почему"
```
Решение: Сделай скриншот в момент ошибки:
  driver.save_screenshot("debug.png")
  # Открой debug.png и посмотри что было на экране
```

### "Element not interactable"
```
Причина: Элемент есть на странице, но не виден или перекрыт.
Решение: 
  # Прокрути к элементу
  driver.execute_script("arguments[0].scrollIntoView()", element)
  # Или кликни через JavaScript
  driver.execute_script("arguments[0].click()", element)
```

### Тест проходит у меня, но не у коллеги
```
Причина: Разные версии Chrome или данные в БД.
Решение: 
  1. Проверь версию Chrome (оба должны использовать одну)
  2. Запусти seed.py для создания одинаковых тестовых данных
```

---

## 9. Задания для студентов

### Уровень 1 (Начинающий)
1. Запусти все Selenium тесты: `py -m pytest tests_selenium/ -v`
2. Посмотри как открывается Chrome при запуске тестов
3. Найди в коде где используется `wait_for()` — объясни зачем
4. Добавь `driver.save_screenshot("test.png")` в любой тест и найди файл

### Уровень 2 (Средний)
5. Напиши тест: проверь что заголовок страницы входа содержит слово "детским" на русском
6. Напиши тест: войди в систему и проверь что URL не изменился (остался localhost:8501)
7. Измени тест `test_wrong_password_shows_error` — попробуй другие неправильные пароли

### Уровень 3 (Продвинутый)
8. Напиши тест для страницы "Посещаемость": проверь что вкладки "Отметить" и "Журнал" видны
9. Напиши тест: смени язык на английский и проверь что кнопка "Войти" стала "Sign In"
10. Напиши тест: войди в систему → войди в садик → проверь что в sidebar видно название садика

---

## Быстрая шпаргалка

```bash
# Подготовка (один раз)
py -m pip install selenium webdriver-manager

# Запустить Streamlit (Терминал 1)
cd .../kindergarden
py -m streamlit run main.py

# Запустить тесты (Терминал 2)
cd .../kindergarden
py -m pytest tests_selenium/ -v

# Один файл
py -m pytest tests_selenium/test_s01_login.py -v

# Один тест
py -m pytest tests_selenium/test_s01_login.py::TestLoginPage::test_successful_login -v

# При ошибке — сделать скриншот (добавить в тест)
driver.save_screenshot("debug.png")
```
