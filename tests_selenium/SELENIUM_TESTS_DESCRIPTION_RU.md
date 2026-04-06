# Описание Selenium-тестов — Kindergarten Management System

Все тесты находятся в папке `kindergarden/tests_selenium/`.  
Тесты проверяют GUI (графический интерфейс) приложения через реальный браузер Chrome.

---

## Структура папки

```
tests_selenium/
├── conftest.py                      — Конфигурация и вспомогательные функции
├── pytest_selenium.ini              — Настройки pytest для Selenium
├── test_s00_diagnostics.py          — Диагностические тесты (скриншоты, HTML)
├── test_s01_login.py                — Тесты страницы входа
├── test_s02_navigation.py           — Тесты навигации и sidebar
├── test_s03_children.py             — Тесты страницы "Дети"
├── test_s04_language.py             — Тесты переключения языка
└── diag_output/                     — Папка для скриншотов (создаётся автоматически)
```

---

## conftest.py — Конфигурация и вспомогательные функции

Этот файл не содержит тестов. Он настраивает окружение для всех тестов.

### Константы

| Константа | Значение | Назначение |
|-----------|----------|------------|
| `APP_URL` | `http://localhost:8501` | Адрес Streamlit приложения |
| `TEST_EMAIL` | `admin@kms.com` | Email тестового суперадмина |
| `TEST_PASSWORD` | `admin123` | Пароль тестового суперадмина |
| `STREAMLIT_STARTUP_TIMEOUT` | `15` | Максимальное время ожидания запуска (сек) |

### Fixtures (фикстуры)

**`streamlit_server`** (scope="session")
- Запускается **один раз** для всей сессии тестов
- Проверяет, запущен ли уже Streamlit на порту 8501
- Если нет — запускает `streamlit run main.py` как subprocess
- Ждёт до 15 секунд пока Streamlit поднимется
- После всех тестов останавливает сервер

**`driver`** (scope по умолчанию = function)
- Запускается **для каждого теста** отдельно
- Создаёт новый экземпляр Chrome WebDriver
- Настраивает окно браузера 1280×900
- Использует `webdriver-manager` — автоматически скачивает ChromeDriver
- После теста закрывает браузер (`browser.quit()`)
- Зависит от `streamlit_server` — Streamlit запускается первым

### Вспомогательные функции

**`wait_for(driver, by, value, timeout=15)`**
- Ждёт появления элемента на странице (максимум 15 секунд)
- Использует `WebDriverWait` + `EC.presence_of_element_located`
- **Почему нужна**: Streamlit — React-приложение, элементы загружаются асинхронно
- Вызывает исключение `TimeoutException` если элемент не появился

**`wait_for_text(driver, text, timeout=15)`**
- Ждёт появления любого текста на странице
- Ищет через XPATH: `//*[contains(text(), '...')]`

**`wait_clickable(driver, by, value, timeout=15)`**
- Ждёт пока элемент станет кликабельным (`element_to_be_clickable`)
- Нужна для кнопок, которые могут быть disabled

**`streamlit_ready(driver, timeout=10)`**
- Делает паузу 1.5 секунды для рендера Streamlit
- Вызывается после `driver.get()` перед поиском элементов

**`login(driver, email, password)`**
- Полная последовательность входа в систему:
  1. Открывает `APP_URL`
  2. Ждёт готовности Streamlit
  3. Находит поле Email по `aria-label='Email'` или `placeholder='Email'`
  4. Вводит email
  5. Находит поле Password по `type='password'`
  6. Вводит пароль
  7. Находит кнопку по `data-testid='stBaseButton-primaryFormSubmit'`
  8. Кликает кнопку
  9. Ждёт 4 секунды загрузки следующей страницы

> **Важно**: Кнопка ищется по `data-testid='stBaseButton-primaryFormSubmit'`, а **не** по тексту "Войти". В этом Streamlit приложении есть Tab с текстом "🔑 Войти" и Submit кнопка с текстом "Войти" — их легко перепутать по XPATH.

---

## pytest_selenium.ini — Настройки pytest

```ini
[pytest]
testpaths = tests_selenium   # откуда брать тесты
addopts = -v --tb=short      # подробный вывод + краткий traceback
markers =
    smoke: Critical UI tests
    slow: Tests that take more time
```

---

## test_s00_diagnostics.py — Диагностические тесты

**Назначение**: НЕ проверяет функциональность. Сохраняет скриншоты и HTML страниц для анализа структуры приложения. Запускается при отладке проблем с селекторами.

**Что изучаем**: как исследовать реальную структуру Streamlit-приложения.

### Вспомогательная функция `save_diag(driver, name)`
- Создаёт папку `diag_output/` если её нет
- Сохраняет скриншот: `diag_output/{name}.png`
- Сохраняет HTML страницы: `diag_output/{name}.html`

### Тест: `test_01_login_page_structure`
**Что делает:**
1. Открывает страницу входа
2. Сохраняет скриншот `01_login_page.png` и `01_login_page.html`
3. Находит все элементы с атрибутом `data-testid` и выводит их список
4. Находит все кнопки `<button>` и выводит их текст

**Зачем нужен**: Позволяет увидеть реальные `data-testid` значения в этой версии Streamlit, чтобы правильно написать селекторы для других тестов.

**Всегда проходит** (`assert True`).

---

### Тест: `test_02_after_login_structure`
**Что делает:**
1. Открывает страницу входа
2. Вводит email в поле `//input[@type='text']`
3. Вводит пароль в поле `//input[@type='password']`
4. Нажимает кнопку входа по тексту "Войти" или "Sign In"
5. Ждёт 5 секунд
6. Сохраняет скриншот `02_after_login.png` и HTML
7. Выводит все `data-testid` после входа
8. Ищет элементы sidebar: `stSidebar`, `stSidebarContent`, `stSidebarNav`
9. Выводит все ссылки `<a>`, кнопки `<button>`, навигационные элементы `<nav>`

**Зачем нужен**: Показывает реальную структуру страницы ПОСЛЕ входа. Из результатов этого теста было выяснено, что `data-testid="stSidebar"` в этой версии Streamlit **не существует**.

**Всегда проходит** (`assert True`).

---

### Тест: `test_03_page_source_keywords`
**Что делает:**
1. Входит в систему (аналогично тесту 02)
2. Получает HTML страницы через `driver.page_source`
3. Ищет 11 ключевых слов в HTML и выводит результат (✅ / ❌)

**Ключевые слова для поиска:**
- `stSidebar`, `stSidebarContent`, `stSidebarNav`
- `stAlert`, `Выйти`, `Sign Out`
- `admin@kms.com`, `Солнышко`, `Радуга`
- `sidebar`, `navigation`

**Зачем нужен**: Позволяет быстро проверить, какой текст и элементы реально присутствуют на странице после входа.

**Всегда проходит** (`assert True`).

---

## test_s01_login.py — Тесты страницы входа

**Тема**: Базовые Selenium операции  
**Что изучаем**: `driver.get()`, `find_element`, `By.XPATH`, `send_keys()`, `click()`, `page_source`, `WebDriverWait`

### Класс `TestLoginPage`

#### Тест 1: `test_page_loads`
**Что проверяет**: Страница открывается и показывает заголовок H1.

**Шаги:**
1. Открывает `http://localhost:8501`
2. Ждёт готовности Streamlit (`streamlit_ready`)
3. Ищет первый `<h1>` элемент через `wait_for`

**Проверки:**
- `title_element is not None` — заголовок найден
- `len(title_element.text) > 0` — заголовок не пустой

**Падает если**: Streamlit не запустился, или страница пустая.

---

#### Тест 2: `test_login_form_visible`
**Что проверяет**: Форма входа (Email + Password) отображается.

**Шаги:**
1. Открывает страницу
2. Ищет поле Email по XPATH: `//input[@aria-label='Email' or @placeholder='Email']`
3. Ищет поле Password по XPATH: `//input[@type='password']`

**Проверки:**
- `email_field.is_displayed()` — поле Email видимо
- `pass_field.is_displayed()` — поле Password видимо

**Падает если**: Форма входа не отображается.

---

#### Тест 3: `test_login_button_visible`
**Что проверяет**: Кнопка входа отображается.

**Шаги:**
1. Открывает страницу
2. Ищет кнопку по `data-testid='stBaseButton-primaryFormSubmit'`

**Проверки:**
- `btn.is_displayed()` — кнопка видима

**Зачем `data-testid`**: В Streamlit есть несколько кнопок с текстом "Войти" (Tab и Submit). `data-testid` однозначно идентифицирует именно кнопку отправки формы.

---

#### Тест 4: `test_successful_login`
**Что проверяет**: Успешный вход — после нажатия кнопки открывается главная страница.

**Предусловие**: Суперадмин `admin@kms.com` / `admin123` должен существовать (создаётся через `seed.py`).

**Шаги:**
1. Вводит `TEST_EMAIL` в поле Email
2. Вводит `TEST_PASSWORD` в поле Password
3. Кликает кнопку Submit
4. Ждёт 3 секунды
5. Проверяет содержимое страницы

**Проверки** (хотя бы одно):
- "садик" в HTML (нижний регистр)
- "kindergarten" в HTML (нижний регистр)
- "Войти →" в HTML (кнопка входа в садик)
- "Enter →" в HTML

---

#### Тест 5: `test_wrong_password_shows_error`
**Что проверяет**: При неправильном пароле появляется сообщение об ошибке.

**Шаги:**
1. Вводит правильный email
2. Вводит **неправильный** пароль: `"НЕПРАВИЛЬНЫЙ_ПАРОЛЬ_999"`
3. Кликает Submit
4. Ждёт 2 секунды
5. Проверяет HTML на наличие ошибки

**Проверки** (хотя бы одно):
- `"stAlert"` в HTML
- `"Неверный"` в HTML
- `"Invalid"` в HTML
- `'role="alert"'` в HTML

---

#### Тест 6: `test_empty_fields_shows_error`
**Что проверяет**: При пустых полях появляется ошибка валидации.

**Шаги:**
1. Открывает страницу (ничего не вводит)
2. Кликает кнопку Submit сразу
3. Ждёт 2 секунды
4. Проверяет HTML

**Проверки** (хотя бы одно):
- `"stAlert"` в HTML
- `"Введите"` в HTML
- `"Fill"` в HTML
- `'role="alert"'` в HTML

---

#### Тест 7: `test_language_selector_visible`
**Что проверяет**: Переключатель языка виден до входа в систему.

**Шаги:**
1. Открывает страницу
2. Ищет все элементы `//div[@data-baseweb='select']` (Streamlit selectbox)

**Проверки:**
- `len(selects) >= 1` — найден хотя бы один выпадающий список

---

### Класс `TestPageTitle`

#### Тест 8: `test_browser_tab_title`
**Что проверяет**: Заголовок вкладки браузера (тег `<title>`) содержит нужный текст.

**Шаги:**
1. Открывает страницу
2. Читает `driver.title`

**Проверки** (хотя бы одно):
- `"Kindergarten"` в title
- `"детск"` в title (нижний регистр)

**Streamlit**: Заголовок задаётся через `st.set_page_config(page_title=...)`.

---

#### Тест 9: `test_page_url`
**Что проверяет**: URL страницы правильный.

**Шаги:**
1. Открывает страницу
2. Читает `driver.current_url`

**Проверки:**
- `"localhost:8501"` в URL

---

## test_s02_navigation.py — Тесты навигации

**Тема**: Навигация по страницам и sidebar  
**Что изучаем**: Использование `login()`, поиск элементов в sidebar, клик по меню.

**Важная особенность**: 
- Sidebar виден сразу после входа (с email и настройками)
- Пункты навигации (Дети, Посещаемость...) появляются только ПОСЛЕ входа в конкретный садик

### Вспомогательная функция `login_and_enter_kindergarten(driver)`
1. Вызывает `login(driver)`, ждёт 3 секунды
2. Ищет кнопку "→" (вход в садик)
3. Кликает её, ждёт 4 секунды
4. Если кнопка не найдена — пропускает (уже в садике)

### Класс `TestSidebarNavigation`

#### Тест 1: `test_sidebar_visible_after_login`
**Что проверяет**: Sidebar отображается после входа в систему.

**Шаги:**
1. Вызывает `login(driver)`, ждёт 3 секунды
2. Ищет `data-testid='stSidebar'` с timeout=15

**Проверки:**
- `sidebar.is_displayed()` — sidebar видим

> **Примечание**: Если этот тест падает — проверьте через `test_s00_diagnostics.py` какой реальный `data-testid` у sidebar в вашей версии Streamlit.

---

#### Тест 2: `test_user_email_in_sidebar`
**Что проверяет**: Email текущего пользователя отображается в sidebar.

**Шаги:**
1. Входит в систему
2. Ищет sidebar
3. Ждёт 2 секунды (полный рендер)
4. Читает `sidebar.text`

**Проверки:**
- `TEST_EMAIL` (`admin@kms.com`) найден в тексте sidebar

---

#### Тест 3: `test_logout_button_in_sidebar`
**Что проверяет**: Кнопка "Выйти" или "Sign Out" есть в sidebar.

**Шаги:**
1. Входит в систему
2. Ищет кнопку через XPATH: `//button[.//p[contains(text(), 'Выйти') or contains(text(), 'Sign Out')]]`

**Проверки:**
- `logout_btn.is_displayed()` — кнопка видима

---

#### Тест 4: `test_logout_works`
**Что проверяет**: Нажатие "Выйти" возвращает на страницу входа.

**Шаги:**
1. Входит в систему
2. Находит и кликает кнопку "Выйти"
3. Ждёт 3 секунды
4. Проверяет HTML

**Проверки** (хотя бы одно):
- `"Войти"` в HTML
- `"Sign In"` в HTML

---

#### Тест 5: `test_kindergarten_list_visible_for_superadmin`
**Что проверяет**: Суперадмин видит список садиков после входа.

**Шаги:**
1. Входит в систему, ждёт 4 секунды
2. Проверяет HTML страницы

**Проверки** (хотя бы одно):
- `"Войти"` в HTML (кнопка "Войти →" для садика)
- `"Enter"` в HTML
- `"Солнышко"` в HTML (название садика из seed)
- `"Радуга"` в HTML
- `"Звёздочка"` в HTML
- `"садик"` в HTML

---

#### Тест 6: `test_enter_kindergarten`
**Что проверяет**: Суперадмин может войти в садик нажав "Войти →".

**Шаги:**
1. Входит в систему
2. Ищет кнопку с текстом "→"
3. Кликает её
4. Ждёт 4 секунды

**Проверки** (хотя бы одно):
- `"Добро пожаловать"` в HTML
- `"Welcome"` в HTML
- `"Посещаемость"` в HTML
- `"Attendance"` в HTML
- `"Дети"` в HTML

---

#### Тест 7: `test_navigation_menu_items`
**Что проверяет**: После входа в садик в sidebar появляются пункты навигации.

**Шаги:**
1. Вызывает `login_and_enter_kindergarten(driver)`
2. Ищет sidebar
3. Читает текст sidebar

**Проверки:**
- Найдено минимум 2 из 4 ожидаемых пунктов: `["Дети", "Посещаемость", "Продукты", "Расходы"]`

---

## test_s03_children.py — Тесты страницы "Дети"

**Тема**: Работа с формами и таблицами  
**Что изучаем**: Клик по вкладкам (tabs), заполнение форм, проверка данных, `find_elements()`

### Вспомогательная функция `go_to_children_page(driver)`
1. Вызывает `login(driver)`, ждёт 2 секунды
2. Пытается войти в садик (кнопка "→")
3. Ищет пункт "Дети" или "Children" в sidebar и кликает
4. Ждёт 2 секунды

### Класс `TestChildrenPage`

#### Тест 1: `test_children_page_loads`
**Что проверяет**: Страница "Дети" открывается после перехода.

**Шаги:**
1. Вызывает `go_to_children_page(driver)`
2. Проверяет HTML

**Проверки** (хотя бы одно):
- `"Дети"` в HTML
- `"Children"` в HTML

---

#### Тест 2: `test_children_tabs_visible`
**Что проверяет**: На странице есть минимум 2 вкладки.

**Шаги:**
1. Переходит на страницу Дети
2. Ищет все элементы `//button[@role='tab']`

**Проверки:**
- `len(tabs) >= 2` — минимум 2 вкладки

**Streamlit tabs**: Вкладки рендерятся как `<button role="tab">`.

---

#### Тест 3: `test_children_list_displayed`
**Что проверяет**: Список детей отображается (данные из seed.py).

**Шаги:**
1. Переходит на страницу Дети
2. Проверяет HTML

**Проверки** (хотя бы одно):
- `"Анна"`, `"Иван"`, `"Мария"` — имена детей из seed.py
- `"активный"` или `"active"` — статус ребёнка
- `"младшая"` или `"Junior"` — название группы

**Предусловие**: Seed.py должен быть запущен.

---

#### Тест 4: `test_add_child_tab_click`
**Что проверяет**: Вкладка "Добавить ребёнка" открывает форму.

**Шаги:**
1. Переходит на страницу Дети
2. Ищет вкладку с текстом "Добавить" или "Add"
3. Кликает по ней
4. Ждёт 1 секунду
5. Проверяет HTML

**Проверки** (хотя бы одно):
- `"Имя"` или `"First Name"` в HTML
- `"Фамилия"` или `"Last Name"` в HTML

---

#### Тест 5: `test_add_child_form_has_fields`
**Что проверяет**: Форма добавления содержит поля для ввода.

**Шаги:**
1. Переходит на страницу Дети
2. Кликает вкладку "Добавить"
3. Ищет все `<input type="text">`

**Проверки:**
- `len(inputs) >= 2` — минимум 2 текстовых поля

---

#### Тест 6: `test_filter_by_group`
**Что проверяет**: На странице детей есть фильтр по группе (selectbox).

**Шаги:**
1. Переходит на страницу Дети
2. Ищет все `//div[@data-baseweb='select']`

**Проверки:**
- `len(selects) >= 1` — минимум 1 выпадающий список

---

## test_s04_language.py — Тесты переключения языка

**Тема**: Проверка динамического поведения интерфейса  
**Что изучаем**: Streamlit selectbox, ActionChains, JavaScript executor

### Класс `TestLanguageSwitching`

#### Тест 1: `test_default_language_is_russian`
**Что проверяет**: По умолчанию интерфейс на русском языке.

**Шаги:**
1. Открывает страницу
2. Проверяет HTML

**Проверки** (хотя бы одно):
- `"Войти"` в HTML
- `"детским садом"` в HTML

---

#### Тест 2: `test_language_selectors_on_login_page`
**Что проверяет**: На странице входа есть 2 переключателя (язык + валюта).

**Шаги:**
1. Открывает страницу
2. Ищет все `//div[@data-baseweb='select']`

**Проверки:**
- `len(selects) >= 2` — минимум 2 выпадающих списка

---

#### Тест 3: `test_switch_to_english_on_login_page`
**Что проверяет**: Переключение на английский язык до входа.

**Шаги:**
1. Открывает страницу
2. Кликает первый selectbox
3. Ждёт 1 секунду
4. Ищет опцию "English" в списке
5. Кликает "English"
6. Ждёт 2 секунды
7. Проверяет HTML

**Проверки** (хотя бы одно):
- `"Sign In"` в HTML
- `"Kindergarten Management"` в HTML

**Обработка ошибок**: Если список не открылся — пробует `execute_script` (JS click).

---

#### Тест 4: `test_english_login_button_text`
**Что проверяет**: После переключения на English кнопка показывает "Sign In".

**Шаги:**
1. Проверяет что начальный язык — русский (`"Войти"` в HTML)
2. Переключает на English
3. Проверяет HTML

**Проверки:**
- `"Sign In"` в HTML

**Если selectbox не открылся**: `pytest.skip()` — тест пропускается, не падает.

---

#### Тест 5: `test_settings_in_sidebar_after_login`
**Что проверяет**: После входа настройки языка доступны в sidebar.

**Шаги:**
1. Вызывает `login(driver)`, ждёт 4 секунды
2. Ищет sidebar, ждёт 2 секунды
3. Читает текст sidebar

**Проверки** (хотя бы одно):
- `"Настройки"` или `"Settings"` в sidebar
- `"Язык"` или `"Language"` в sidebar
- `"Русский"` или `"Шекели"` в sidebar

---

#### Тест 6: `test_currency_selector_on_login_page`
**Что проверяет**: Переключатель валюты присутствует на странице входа.

**Шаги:**
1. Открывает страницу
2. Проверяет наличие 2 selectbox
3. Проверяет HTML

**Проверки:**
- `len(selects) >= 2` — есть 2 выпадающих списка
- В HTML есть `"Шекели"`, `"Shekels"`, `"ILS"` или `"₪"`

---

### Класс `TestPageStructure`

#### Тест 7: `test_main_title_present`
**Что проверяет**: Главный заголовок H1 присутствует.

**Шаги:**
1. Открывает страницу
2. Ищет `<h1>` через `wait_for`

**Проверки:**
- `title is not None` и `len(title.text) > 0`

---

#### Тест 8: `test_streamlit_app_not_crashed`
**Что проверяет**: Приложение не упало (нет страницы с ошибкой Streamlit).

**Шаги:**
1. Открывает страницу
2. Проверяет HTML

**Проверки** (всё отсутствует):
- `"This app has encountered an error"` — НЕТ
- `"ProgrammingError"` — НЕТ
- `"ImportError"` — НЕТ

**Полезность**: Первый тест для запуска при любых проблемах.

---

#### Тест 9: `test_responsive_layout`
**Что проверяет**: Страница корректно отображается в разрешении 1280×900.

**Шаги:**
1. Открывает страницу
2. Устанавливает размер окна 1280×900
3. Ждёт 1 секунду
4. Ищет `data-testid='stMainBlockContainer'`

**Проверки:**
- `len(main_content) > 0` — основной контейнер найден

---

## Итоговая таблица тестов

| Файл | Класс | Тест | Что проверяет |
|------|-------|------|---------------|
| s00 | TestDiagnostics | test_01_login_page_structure | Структура страницы входа |
| s00 | TestDiagnostics | test_02_after_login_structure | Структура после входа |
| s00 | TestDiagnostics | test_03_page_source_keywords | Ключевые слова в HTML |
| s01 | TestLoginPage | test_page_loads | Заголовок H1 на странице |
| s01 | TestLoginPage | test_login_form_visible | Email и Password поля видны |
| s01 | TestLoginPage | test_login_button_visible | Кнопка Submit видна |
| s01 | TestLoginPage | test_successful_login | Успешный вход |
| s01 | TestLoginPage | test_wrong_password_shows_error | Ошибка при неверном пароле |
| s01 | TestLoginPage | test_empty_fields_shows_error | Ошибка при пустых полях |
| s01 | TestLoginPage | test_language_selector_visible | Переключатель языка есть |
| s01 | TestPageTitle | test_browser_tab_title | Заголовок вкладки браузера |
| s01 | TestPageTitle | test_page_url | URL страницы |
| s02 | TestSidebarNavigation | test_sidebar_visible_after_login | Sidebar виден |
| s02 | TestSidebarNavigation | test_user_email_in_sidebar | Email в sidebar |
| s02 | TestSidebarNavigation | test_logout_button_in_sidebar | Кнопка выхода в sidebar |
| s02 | TestSidebarNavigation | test_logout_works | Выход из системы |
| s02 | TestSidebarNavigation | test_kindergarten_list_visible_for_superadmin | Список садиков |
| s02 | TestSidebarNavigation | test_enter_kindergarten | Вход в садик |
| s02 | TestSidebarNavigation | test_navigation_menu_items | Пункты меню в sidebar |
| s03 | TestChildrenPage | test_children_page_loads | Страница Дети открывается |
| s03 | TestChildrenPage | test_children_tabs_visible | Вкладки на странице |
| s03 | TestChildrenPage | test_children_list_displayed | Список детей из seed |
| s03 | TestChildrenPage | test_add_child_tab_click | Вкладка добавления |
| s03 | TestChildrenPage | test_add_child_form_has_fields | Поля формы добавления |
| s03 | TestChildrenPage | test_filter_by_group | Фильтр по группе |
| s04 | TestLanguageSwitching | test_default_language_is_russian | Язык по умолчанию |
| s04 | TestLanguageSwitching | test_language_selectors_on_login_page | 2 переключателя на странице |
| s04 | TestLanguageSwitching | test_switch_to_english_on_login_page | Переключение на English |
| s04 | TestLanguageSwitching | test_english_login_button_text | Кнопка Sign In |
| s04 | TestLanguageSwitching | test_settings_in_sidebar_after_login | Настройки в sidebar |
| s04 | TestLanguageSwitching | test_currency_selector_on_login_page | Переключатель валюты |
| s04 | TestPageStructure | test_main_title_present | H1 заголовок |
| s04 | TestPageStructure | test_streamlit_app_not_crashed | Нет страницы ошибки |
| s04 | TestPageStructure | test_responsive_layout | Основной контейнер виден |

**Всего: 34 теста** в 5 файлах.
