# Инструкция по запуску Selenium-тестов

---

## Предварительные требования

### 1. Установленные пакеты
```bash
py -m pip install selenium webdriver-manager pytest
```

### 2. Запущенное приложение
Streamlit должен быть запущен на `http://localhost:8501`.  
Из папки `kindergarden/`:
```bash
streamlit run main.py
```

### 3. База данных с тестовыми данными
Суперадмин `admin@kms.com` / `admin123` должен существовать.  
Запусти seed ОДИН раз после первого запуска приложения:
```bash
py seed.py
```

### 4. Chrome установлен
ChromeDriver скачивается автоматически через `webdriver-manager`.  
Устанавливать вручную не нужно.

---

## Рабочая директория

**Все команды ниже выполняются из папки `kindergarden/`:**

```bash
cd C:\Users\RedmiBook\Documents\MyProjects\ClaudeCode_test\kindergarden
```

> Если запускать из другой папки — тесты не найдут `conftest.py` и упадут с ошибкой `ModuleNotFoundError`.

---

## Запуск всех тестов сразу

```bash
py -m pytest tests_selenium/ -v
```

Что означают флаги:
- `tests_selenium/` — папка с тестами
- `-v` — подробный вывод (verbose): имя каждого теста + PASSED/FAILED

---

## Запуск отдельных файлов

### Диагностические тесты (запускай первым при проблемах)

```bash
py -m pytest tests_selenium/test_s00_diagnostics.py -v -s
```

Флаг `-s` — показывает `print()` вывод прямо в терминале.  
Тесты сохраняют скриншоты и HTML в `tests_selenium/diag_output/`.

---

### Тесты страницы входа

```bash
py -m pytest tests_selenium/test_s01_login.py -v -s
```

Запуск одного класса из файла:
```bash
py -m pytest tests_selenium/test_s01_login.py::TestLoginPage -v -s
py -m pytest tests_selenium/test_s01_login.py::TestPageTitle -v -s
```

---

### Тесты навигации

```bash
py -m pytest tests_selenium/test_s02_navigation.py -v -s
```

---

### Тесты страницы "Дети"

```bash
py -m pytest tests_selenium/test_s03_children.py -v -s
```

---

### Тесты переключения языка

```bash
py -m pytest tests_selenium/test_s04_language.py -v -s
```

Запуск одного класса:
```bash
py -m pytest tests_selenium/test_s04_language.py::TestLanguageSwitching -v -s
py -m pytest tests_selenium/test_s04_language.py::TestPageStructure -v -s
```

---

## Запуск отдельных тестов

Синтаксис: `файл::Класс::тест_метод`

```bash
# Один конкретный тест
py -m pytest tests_selenium/test_s01_login.py::TestLoginPage::test_page_loads -v -s

# Тест успешного входа
py -m pytest tests_selenium/test_s01_login.py::TestLoginPage::test_successful_login -v -s

# Тест неправильного пароля
py -m pytest tests_selenium/test_s01_login.py::TestLoginPage::test_wrong_password_shows_error -v -s

# Тест заголовка вкладки браузера
py -m pytest tests_selenium/test_s01_login.py::TestPageTitle::test_browser_tab_title -v -s

# Тест входа в садик
py -m pytest tests_selenium/test_s02_navigation.py::TestSidebarNavigation::test_enter_kindergarten -v -s

# Тест выхода из системы
py -m pytest tests_selenium/test_s02_navigation.py::TestSidebarNavigation::test_logout_works -v -s

# Тест переключения на английский
py -m pytest tests_selenium/test_s04_language.py::TestLanguageSwitching::test_switch_to_english_on_login_page -v -s

# Тест что приложение не упало
py -m pytest tests_selenium/test_s04_language.py::TestPageStructure::test_streamlit_app_not_crashed -v -s
```

---

## Запуск по названию теста (поиск по ключевому слову)

Флаг `-k` позволяет запустить тесты, чьё имя содержит определённое слово:

```bash
# Все тесты связанные с входом
py -m pytest tests_selenium/ -k "login" -v -s

# Все тесты связанные с языком
py -m pytest tests_selenium/ -k "language" -v -s

# Все тесты связанные с sidebar
py -m pytest tests_selenium/ -k "sidebar" -v -s

# Все тесты связанные с logout
py -m pytest tests_selenium/ -k "logout" -v -s

# Все тесты связанные с children (дети)
py -m pytest tests_selenium/ -k "children" -v -s

# Несколько ключевых слов — через "or"
py -m pytest tests_selenium/ -k "login or language" -v -s

# Исключить тест — через "not"
py -m pytest tests_selenium/ -k "not diagnostics" -v -s
```

---

## Полный справочник команд

| Что запустить | Команда |
|---------------|---------|
| Все тесты | `py -m pytest tests_selenium/ -v` |
| Все тесты с выводом print | `py -m pytest tests_selenium/ -v -s` |
| Только диагностика | `py -m pytest tests_selenium/test_s00_diagnostics.py -v -s` |
| Только login тесты | `py -m pytest tests_selenium/test_s01_login.py -v -s` |
| Только navigation | `py -m pytest tests_selenium/test_s02_navigation.py -v -s` |
| Только children | `py -m pytest tests_selenium/test_s03_children.py -v -s` |
| Только language | `py -m pytest tests_selenium/test_s04_language.py -v -s` |
| Один класс | `py -m pytest tests_selenium/test_s01_login.py::TestLoginPage -v -s` |
| Один тест | `py -m pytest tests_selenium/test_s01_login.py::TestLoginPage::test_page_loads -v -s` |
| По ключевому слову | `py -m pytest tests_selenium/ -k "login" -v -s` |
| Остановить при первой ошибке | `py -m pytest tests_selenium/ -v -x` |
| Показать 3 самых медленных | `py -m pytest tests_selenium/ -v --durations=3` |
| Без открытия браузера | см. раздел Headless |

---

## Запуск в headless режиме (без открытия браузера)

Чтобы тесты работали без видимого окна Chrome, раскомментируй строку в `conftest.py`:

```python
# В файле tests_selenium/conftest.py, строка ~116:
options.add_argument("--headless")   # убери # перед этой строкой
```

После этого запускай как обычно:
```bash
py -m pytest tests_selenium/ -v
```

Headless режим быстрее и удобен для CI/CD.

---

## Остановка при первой ошибке

```bash
py -m pytest tests_selenium/ -v -x
```

Флаг `-x` — остановить после первого FAILED теста. Удобно при отладке.

---

## Сохранение результатов в файл

```bash
py -m pytest tests_selenium/ -v > results.txt 2>&1
```

Или с подробным отчётом:
```bash
py -m pytest tests_selenium/ -v --tb=long > results.txt 2>&1
```

---

## Порядок запуска тестов (рекомендуемый)

Если запускаешь впервые или после проблем — рекомендуется такой порядок:

### Шаг 1: Убедись что приложение работает
```bash
py -m pytest tests_selenium/test_s04_language.py::TestPageStructure::test_streamlit_app_not_crashed -v -s
```

### Шаг 2: Запусти диагностику (сохранит скриншоты)
```bash
py -m pytest tests_selenium/test_s00_diagnostics.py -v -s
```
Открой `tests_selenium/diag_output/01_login_page.png` — убедись что страница выглядит правильно.

### Шаг 3: Запусти тесты входа
```bash
py -m pytest tests_selenium/test_s01_login.py -v -s
```

### Шаг 4: Запусти тесты навигации
```bash
py -m pytest tests_selenium/test_s02_navigation.py -v -s
```

### Шаг 5: Все остальные тесты
```bash
py -m pytest tests_selenium/test_s03_children.py tests_selenium/test_s04_language.py -v -s
```

---

## Что означает вывод pytest

```
tests_selenium/test_s01_login.py::TestLoginPage::test_page_loads PASSED    [  6%]
tests_selenium/test_s01_login.py::TestLoginPage::test_login_form_visible PASSED [ 12%]
tests_selenium/test_s01_login.py::TestLoginPage::test_successful_login FAILED   [ 18%]
```

| Статус | Значение |
|--------|----------|
| `PASSED` | Тест прошёл успешно |
| `FAILED` | Тест упал — проверка не прошла |
| `ERROR` | Тест упал с исключением (не с AssertionError) |
| `SKIPPED` | Тест пропущен (`pytest.skip()`) |
| `XFAIL` | Тест ожидаемо упал |

В конце pytest выводит итог:
```
5 passed, 2 failed, 1 skipped in 45.32s
```

---

## Чтение ошибок

При падении теста pytest показывает:

```
FAILED tests_selenium/test_s01_login.py::TestLoginPage::test_successful_login
─────────────────────── short test summary info ────────────────────────
FAILED: AssertionError: После входа не видно главной страницы
```

Как читать:
1. **Какой тест упал** — имя файла, класса, метода
2. **AssertionError** — провалилась проверка `assert`
3. **Текст ошибки** — то что написано после `assert ..., "текст"`

---

## Типичные проблемы и решения

### ❌ `ModuleNotFoundError: No module named 'conftest'`
**Причина**: Запуск из неправильной папки.  
**Решение**: Перейди в `kindergarden/`:
```bash
cd C:\Users\RedmiBook\Documents\MyProjects\ClaudeCode_test\kindergarden
```

---

### ❌ `TimeoutException: Message: element not found after 15 sec`
**Причина**: Streamlit не запущен или элемент не существует.  
**Решение**:
1. Убедись что Streamlit запущен: открой `http://localhost:8501` в браузере
2. Запусти диагностический тест для изучения структуры страницы:
```bash
py -m pytest tests_selenium/test_s00_diagnostics.py::TestDiagnostics::test_01_login_page_structure -v -s
```

---

### ❌ `WebDriverException: Chrome not found`
**Причина**: Chrome не установлен.  
**Решение**: Установи Google Chrome с официального сайта.

---

### ❌ Тесты логина падают — `"После входа не видно главной страницы"`
**Причина**: Возможно неправильный email/пароль в базе данных.  
**Решение**: Проверь что суперадмин создан правильно:
1. Останови Streamlit: `taskkill /F /IM python.exe`
2. Удали базу: `del local_storage.db`
3. Перезапусти Streamlit: `streamlit run main.py`
4. Запусти seed: `py seed.py`
5. Запусти тесты снова

---

### ❌ Тесты sidebar падают
**Причина**: В этой версии Streamlit `data-testid="stSidebar"` может не существовать.  
**Решение**: Запусти диагностику и найди реальный testid:
```bash
py -m pytest tests_selenium/test_s00_diagnostics.py::TestDiagnostics::test_02_after_login_structure -v -s
```
Посмотри в выводе список всех `data-testid` после входа.

---

### ❌ Тест `test_add_child_tab_click` падает (children)
**Причина**: Навигация по sidebar не работает — не удалось перейти на страницу Дети.  
**Решение**: Сначала убедись что тесты навигации (`test_s02_navigation.py`) проходят.

---

### ❌ `SessionNotCreatedException: Chrome version mismatch`
**Причина**: Версия ChromeDriver не совпадает с версией Chrome.  
**Решение**: `webdriver-manager` обновит ChromeDriver автоматически при следующем запуске. Если не помогает:
```bash
py -m pip install --upgrade webdriver-manager
```

---

## Структура вывода при успешном запуске

```
================================================= test session starts ==================================================
platform win32 -- Python 3.13.x, pytest-9.x.x
collected 34 items

tests_selenium/test_s01_login.py::TestLoginPage::test_page_loads PASSED
✅ Заголовок: Управление детским садом

tests_selenium/test_s01_login.py::TestLoginPage::test_login_form_visible PASSED
✅ Форма входа отображается корректно
...
================================================ 34 passed in 185.42s =================================================
```

Каждый тест занимает от 5 до 15 секунд (Streamlit медленно рендерит).  
Все 34 теста занимают около **3–5 минут**.
