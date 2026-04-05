"""
conftest.py — Конфигурация тестов (загружается pytest автоматически)

Этот файл — "фундамент" всех тестов. Он делает 3 вещи:
1. Настраивает пути импорта (чтобы найти модули проекта)
2. Создаёт тестовую базу данных в памяти (SQLite in-memory)
3. Определяет fixtures — повторно используемые "заготовки" данных

FIXTURES — это как конструктор в тестах: создаёт нужные данные перед тестом
и убирает их после. Без fixtures пришлось бы повторять код в каждом тесте.
"""

import os
import sys
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ── ШАГ 1: Добавляем корневую папку проекта в sys.path ───────────────────────
# Это нужно, чтобы Python мог найти файлы проекта (crud.py, models.py и т.д.)
# __file__ = .../kindergarden/tests/conftest.py
# os.path.dirname дважды поднимает нас до .../kindergarden/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# ── ШАГ 2: Устанавливаем тестовую БД ДО импорта модулей проекта ──────────────
# database.py читает эту переменную при первом импорте.
# Если установить её здесь — проект подключится к тестовой БД, а не к Neon.tech.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# ── ШАГ 3: Импортируем модули проекта (ПОСЛЕ установки DATABASE_URL) ──────────
from database import Base  # noqa: E402
import crud                 # noqa: E402
from auth import hash_password  # noqa: E402

# ── ШАГ 4: Создаём тестовый движок SQLite ────────────────────────────────────
#
# StaticPool = все соединения используют одну и ту же in-memory БД.
# Без StaticPool каждое соединение видит пустую БД (данные не сохраняются).
#
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Фабрика тестовых сессий (аналог SessionLocal в database.py)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


# ── ГЛАВНАЯ FIXTURE: Сброс БД перед каждым тестом ────────────────────────────

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """
    autouse=True — эта fixture применяется ко ВСЕМ тестам автоматически.

    Перед каждым тестом:
      - Создаёт все таблицы в тестовой БД
      - Подменяет crud.SessionLocal на тестовую версию (monkeypatch)

    После каждого теста:
      - Удаляет все таблицы (чистый лист для следующего теста)

    monkeypatch — встроенный инструмент pytest для временной замены объектов.
    Замена действует только во время теста, после — откатывается автоматически.
    """
    # Создаём таблицы
    Base.metadata.create_all(bind=TEST_ENGINE)

    # Подменяем SessionLocal в модуле crud
    monkeypatch.setattr(crud, "SessionLocal", TestSessionLocal)

    yield  # ← тест выполняется здесь

    # Чистим таблицы после теста
    Base.metadata.drop_all(bind=TEST_ENGINE)


# ── ВСПОМОГАТЕЛЬНЫЕ FIXTURES ──────────────────────────────────────────────────

@pytest.fixture
def db_session():
    """
    Предоставляет прямую сессию к тестовой БД.
    Используется в тестах, которым нужен прямой доступ к SQLAlchemy.

    yield session — возвращает сессию в тест.
    Блок finally гарантирует закрытие сессии даже при ошибке.
    """
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_kindergarten():
    """
    Создаёт тестовый садик и возвращает его ID.

    Fixtures могут зависеть от других fixtures — например, test_child
    зависит от test_kindergarten.
    """
    kg_id = crud.add_kindergarten(
        name="Тестовый Садик",
        address="ул. Тестовая, 1",
        phone="050-1234567",
        logo_url="",
    )
    return kg_id


@pytest.fixture
def second_kindergarten():
    """Второй садик — для тестов изоляции данных между садиками."""
    kg_id = crud.add_kindergarten(
        name="Другой Садик",
        address="ул. Другая, 2",
        phone="050-7654321",
        logo_url="",
    )
    return kg_id


@pytest.fixture
def test_child(test_kindergarten):
    """
    Создаёт тестового ребёнка и возвращает объект Child.

    Эта fixture зависит от test_kindergarten — pytest автоматически
    создаёт test_kindergarten перед test_child.
    """
    crud.add_child(
        kindergarten_id=test_kindergarten,
        first_name="Иван",
        last_name="Петров",
        birth_date=date(2020, 5, 15),
        parent_name="Петров Сергей",
        parent_phone="050-9876543",
        enrollment_date=date(2023, 9, 1),
        status="активный",
        group="младшая",
    )
    children = crud.get_all_children(test_kindergarten)
    return children[0]


@pytest.fixture
def test_child_with_fee(test_kindergarten):
    """Ребёнок с установленным ежемесячным взносом 3000."""
    crud.add_child(
        kindergarten_id=test_kindergarten,
        first_name="Мария",
        last_name="Сидорова",
        birth_date=date(2019, 8, 20),
        parent_name="Сидорова Анна",
        parent_phone="050-1111111",
        enrollment_date=date(2023, 9, 1),
        status="активный",
        group="средняя",
    )
    children = crud.get_all_children(test_kindergarten)
    child = children[0]
    crud.update_child_fee(child.id, 3000.0)
    # Обновляем объект из БД
    children = crud.get_all_children(test_kindergarten)
    return children[0]
