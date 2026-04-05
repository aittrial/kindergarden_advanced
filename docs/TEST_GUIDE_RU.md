# Руководство по тестированию
# Kindergarten Management System — PyTest Guide (RU)

**Версия:** 1.0 | **Дата:** Апрель 2026  
**Для кого:** Студенты курса QA Testing

---

## Содержание
1. [Что такое тестирование?](#1-что-такое-тестирование)
2. [Установка и запуск](#2-установка-и-запуск)
3. [Структура тестов](#3-структура-тестов)
4. [Концепции pytest](#4-концепции-pytest)
5. [Описание тестовых файлов](#5-описание-тестовых-файлов)
6. [Запуск отдельных тестов](#6-запуск-отдельных-тестов)
7. [Понимание результатов](#7-понимание-результатов)
8. [Задания для студентов](#8-задания-для-студентов)

---

## 1. Что такое тестирование?

**Тест** — это код, который проверяет, что другой код работает правильно.

```
Программа без тестов = Самолёт без проверки перед вылетом.
```

### Виды тестов в этом проекте

| Вид | Что проверяет | Файл |
|-----|--------------|------|
| **Unit test** | Одну функцию изолированно | test_01_auth.py, test_06_i18n.py |
| **Integration test** | Несколько слоёв вместе (функция + БД) | test_03, test_04, test_05 |
| **Smoke test** | Самые критичные функции работают | `@pytest.mark.smoke` |
| **Regression test** | Исправленные баги не вернулись | `@pytest.mark.regression` |

### Паттерн AAA (Arrange / Act / Assert)

Каждый тест строится по трём шагам:

```python
def test_example():
    # Arrange — подготовка данных
    password = "mypassword"
    
    # Act — выполняем тестируемое действие
    hashed = hash_password(password)
    
    # Assert — проверяем результат
    assert hashed != password
```

---

## 2. Установка и запуск

### Шаг 1: Установить зависимости
```bash
# Из корневой папки проекта (kindergarden/)
pip install -r requirements.txt
pip install pytest
```

### Шаг 2: Запустить все тесты
```bash
# Из корневой папки проекта (kindergarden/)
pytest
```

### Шаг 3: Запуск с подробным выводом
```bash
pytest -v
```

**Пример вывода:**
```
tests/test_01_auth.py::TestHashPassword::test_returns_string         PASSED
tests/test_01_auth.py::TestHashPassword::test_hash_is_not_plaintext  PASSED
tests/test_01_auth.py::TestVerifyPassword::test_correct_password      PASSED
...
========================= 52 passed in 3.21s =========================
```

---

## 3. Структура тестов

```
kindergarden/
├── pytest.ini                    ← Конфигурация pytest
├── tests/
│   ├── conftest.py               ← Общие fixtures (запускается автоматически)
│   ├── requirements_test.txt     ← Зависимости для тестов
│   ├── test_01_auth.py           ← Хэширование паролей (Unit)
│   ├── test_02_models.py         ← Модели БД (Integration)
│   ├── test_03_crud_children.py  ← CRUD дети (Integration)
│   ├── test_04_crud_payments.py  ← Оплата и должники (Integration + Regression)
│   ├── test_05_crud_attendance.py← Посещаемость (Integration)
│   └── test_06_i18n.py           ← Переводы и валюты (Unit + Mock)
└── docs/
    ├── TEST_GUIDE_RU.md          ← Этот файл
    └── TEST_GUIDE_EN.md
```

### Почему используется SQLite вместо Neon.tech?

| SQLite in-memory | Neon.tech (production) |
|-----------------|----------------------|
| Мгновенно (нет сети) | 1-3 сек на запрос |
| Чистая БД для каждого теста | Данные остаются между тестами |
| Не нужен интернет | Требует подключения |
| Не портит реальные данные | Может испортить production данные |

**Правило: никогда не тестируйте на production базе данных!**

---

## 4. Концепции pytest

### 4.1 Fixtures — готовые данные для тестов

Fixture — это функция, которая создаёт данные перед тестом и убирает после.

```python
# В conftest.py определена fixture:
@pytest.fixture
def test_kindergarten():
    kg_id = crud.add_kindergarten(name="Тестовый Садик", ...)
    return kg_id

# В тесте — просто указываем имя fixture как параметр:
def test_something(test_kindergarten):
    # test_kindergarten уже создан и содержит ID садика
    children = crud.get_all_children(test_kindergarten)
```

**Autouse fixture** — применяется ко ВСЕМ тестам автоматически:
```python
@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    # Выполняется перед каждым тестом
    Base.metadata.create_all(bind=TEST_ENGINE)
    monkeypatch.setattr(crud, "SessionLocal", TestSessionLocal)
    
    yield  # Тест выполняется здесь
    
    # Выполняется после каждого теста
    Base.metadata.drop_all(bind=TEST_ENGINE)
```

### 4.2 parametrize — один тест, много данных

```python
@pytest.mark.parametrize("password", [
    "short",
    "a" * 100,
    "пароль на русском",
])
def test_any_password_works(password):
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    
# pytest запустит этот тест 3 раза, по одному для каждого пароля
```

### 4.3 markers — категории тестов

```python
@pytest.mark.smoke
def test_critical():
    ...

@pytest.mark.regression  
def test_fixed_bug():
    ...
```

Запуск по маркерам:
```bash
pytest -m smoke        # только smoke тесты
pytest -m regression   # только regression тесты
pytest -m "not smoke"  # всё кроме smoke
```

### 4.4 pytest.raises — ожидаемые ошибки

```python
def test_duplicate_email_raises_error(db_session):
    db_session.add(User(email="same@test.com", ...))
    db_session.commit()
    
    db_session.add(User(email="same@test.com", ...))  # дубликат!
    
    with pytest.raises(IntegrityError):
        db_session.commit()  # Ожидаем IntegrityError
    # Если ошибки нет — тест УПАДЁТ
    # Если ошибка есть — тест ПРОЙДЁТ
```

### 4.5 Mock — замена зависимостей

Когда функция зависит от внешней системы (Streamlit, сеть, БД),
используем mock — временную замену:

```python
from unittest.mock import patch

def test_russian_translation():
    # patch.object заменяет st.session_state на обычный словарь
    with patch.object(i18n.st, "session_state", {"lang": "ru", "currency": "ILS"}):
        result = i18n.t("sign_in")
    
    assert result == "Войти"
# После блока with — session_state возвращается в исходное состояние
```

---

## 5. Описание тестовых файлов

### test_01_auth.py — Аутентификация
**Концепции:** AAA, assert, parametrize, markers  
**Без БД:** Чистые unit-тесты функций `hash_password()` и `verify_password()`

Ключевые тесты:
- `test_returns_string` — хэш является строкой
- `test_deterministic` — одинаковый пароль = одинаковый хэш
- `test_case_sensitive` — "Password" ≠ "password"
- `test_various_password_formats` — параметризация разных паролей

### test_02_models.py — Модели базы данных
**Концепции:** db_session fixture, IntegrityError, defaults  
**С БД:** Прямое создание объектов SQLAlchemy

Ключевые тесты:
- `test_user_unique_email_constraint` — UNIQUE ограничение в БД
- `test_child_default_group` — значения по умолчанию
- `test_multiple_payments_same_month` — разрешены частичные оплаты

### test_03_crud_children.py — CRUD операции
**Концепции:** Integration tests, зависимые fixtures, изоляция данных

Ключевые тесты:
- `test_child_belongs_to_correct_kindergarten` — мультитенантность
- `test_update_child_group` — перевод между группами
- `test_delete_nonexistent_child_no_error` — graceful handling

### test_04_crud_payments.py — Оплата и должники
**Концепции:** Regression tests, edge cases, complex parametrize  
**Самые важные тесты проекта!**

Ключевые тесты:
- `test_partial_payment_child_is_debtor` — **REGRESSION**: частичная оплата ≠ полная
- `test_multiple_partial_payments_summed` — суммирование платежей
- `test_debtor_threshold` — параметризация пороговых значений
- `test_inactive_child_not_debtor` — неактивные не проверяются

### test_05_crud_attendance.py — Посещаемость
**Концепции:** Upsert логика, JOIN-запросы

Ключевые тесты:
- `test_update_existing_attendance` — upsert: обновление, а не дублирование
- `test_multiple_updates_same_day` — последний статус побеждает
- `test_attendance_isolated_by_kindergarten` — изоляция по садикам

### test_06_i18n.py — Переводы и валюты
**Концепции:** Mock (patch.object), структурные тесты словарей

Ключевые тесты:
- `test_same_keys_in_both_languages` — синхронизация переводов
- `test_missing_key_returns_key_itself` — безопасный fallback
- `test_format_amount_ils` — форматирование суммы с символом

---

## 6. Запуск отдельных тестов

```bash
# Один файл
pytest tests/test_01_auth.py

# Один класс
pytest tests/test_01_auth.py::TestHashPassword

# Один тест
pytest tests/test_04_crud_payments.py::TestDebtorLogic::test_partial_payment_child_is_debtor

# По маркеру
pytest -m smoke
pytest -m regression

# С подробным выводом
pytest -v

# Остановиться при первой ошибке
pytest -x

# Показать 5 самых медленных тестов
pytest --durations=5

# Только тесты, содержащие слово "payment" в названии
pytest -k "payment"

# Краткий вывод (точки вместо названий)
pytest -q
```

---

## 7. Понимание результатов

### Успешный запуск
```
test_01_auth.py::TestHashPassword::test_returns_string PASSED    [ 10%]
test_01_auth.py::TestHashPassword::test_hash_is_not_plaintext PASSED [ 20%]
...
========================= 52 passed in 3.21s =========================
```

### Упавший тест
```
FAILED tests/test_04_crud_payments.py::TestDebtorLogic::test_partial_payment_child_is_debtor

AssertionError: Частично оплативший ребёнок — должник!
assert 0 == 1
 +  where 0 = len([])
```

**Расшифровка:**
- `FAILED` — тест не прошёл
- `AssertionError` — условие assert было False
- `assert 0 == 1` — ожидали 1 должника, получили 0
- Это означает, что баг с частичной оплатой **вернулся**!

### Символы
| Символ | Значение |
|--------|---------|
| `.` | PASSED — тест прошёл |
| `F` | FAILED — тест упал |
| `E` | ERROR — исключение в fixture |
| `s` | SKIPPED — тест пропущен |
| `x` | XFAIL — ожидаемо упал |

---

## 8. Задания для студентов

### Уровень 1 (Начинающий)
1. Запустите все тесты командой `pytest -v`
2. Запустите только smoke-тесты: `pytest -m smoke`
3. Найдите и прочитайте тест `test_partial_payment_child_is_debtor`
4. Объясните своими словами: почему это regression test?

### Уровень 2 (Средний)
5. Добавьте новый тест в `test_01_auth.py`: проверьте, что хэш содержит только строчные буквы
6. Добавьте тест в `test_03_crud_children.py`: добавьте 10 детей и проверьте, что все сохранились
7. В `test_04_crud_payments.py` добавьте параметр `(0.01, 3000.0, True)` в `test_debtor_threshold` — что произойдёт?

### Уровень 3 (Продвинутый)
8. Напишите новый файл `test_07_crud_expenses.py` с тестами для функций расходов
9. Добавьте тест, который проверяет, что удалённый садик не возвращается в списке
10. Напишите тест, который намеренно обнаруживает баг: что будет, если добавить ребёнка без имени?

---

## Полезные ссылки

- [Документация pytest](https://docs.pytest.org)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [SQLAlchemy тестирование](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)
