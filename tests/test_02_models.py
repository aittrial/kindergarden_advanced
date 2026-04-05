"""
test_02_models.py — Тесты моделей базы данных (models.py)

ТЕМА: Fixtures и работа с базой данных
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Что изучаем в этом файле:

1. FIXTURE db_session — прямой доступ к SQLAlchemy сессии
2. Создание объектов моделей напрямую
3. Проверка значений по умолчанию (default values)
4. Тестирование ограничений БД (constraints: NOT NULL, UNIQUE)
5. pytest.raises — ожидаемые исключения

Тестируем: модели из models.py через прямые SQL-операции
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError

from models import Kindergarten, User, Child, Attendance, Product, Expense, Payment
from auth import hash_password


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 1: Модель Kindergarten (садик)
# ═══════════════════════════════════════════════════════════════════════

class TestKindergartenModel:

    def test_create_kindergarten_minimal(self, db_session):
        """
        db_session — это fixture из conftest.py.
        pytest видит параметр 'db_session' и автоматически вызывает fixture.

        Создаём садик только с обязательным полем name.
        """
        # Arrange
        kg = Kindergarten(name="Солнышко")

        # Act
        db_session.add(kg)
        db_session.commit()
        db_session.refresh(kg)  # Загружаем данные из БД (в т.ч. id)

        # Assert
        assert kg.id is not None, "ID должен быть присвоен автоматически"
        assert kg.name == "Солнышко"

    def test_create_kindergarten_full(self, db_session):
        """Создание садика со всеми полями."""
        kg = Kindergarten(
            name="Радуга",
            address="Хайфа, ул. Цветочная 5",
            phone="04-9876543",
            logo_url="https://example.com/logo.png"
        )
        db_session.add(kg)
        db_session.commit()

        assert kg.name == "Радуга"
        assert kg.address == "Хайфа, ул. Цветочная 5"
        assert kg.logo_url == "https://example.com/logo.png"

    def test_optional_fields_default_to_none(self, db_session):
        """Необязательные поля по умолчанию None."""
        kg = Kindergarten(name="Минимум")
        db_session.add(kg)
        db_session.commit()

        assert kg.address is None
        assert kg.phone is None
        assert kg.logo_url is None

    def test_multiple_kindergartens(self, db_session):
        """Можно создать несколько садиков в одной БД."""
        names = ["Садик А", "Садик Б", "Садик В"]
        for name in names:
            db_session.add(Kindergarten(name=name))
        db_session.commit()

        count = db_session.query(Kindergarten).count()
        assert count == 3

    def test_each_kindergarten_has_unique_id(self, db_session):
        """У каждого садика уникальный ID."""
        kg1 = Kindergarten(name="Первый")
        kg2 = Kindergarten(name="Второй")
        db_session.add_all([kg1, kg2])
        db_session.commit()

        assert kg1.id != kg2.id


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 2: Модель User (пользователь/администратор)
# ═══════════════════════════════════════════════════════════════════════

class TestUserModel:

    def test_create_superadmin(self, db_session):
        """Создание суперадмина."""
        user = User(
            email="super@kms.com",
            password_hash=hash_password("admin123"),
            role="superadmin"
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.role == "superadmin"
        assert user.email == "super@kms.com"

    def test_user_default_language_is_russian(self, db_session):
        """По умолчанию язык — русский."""
        user = User(email="u@test.com", password_hash="hash", role="admin")
        db_session.add(user)
        db_session.commit()

        assert user.language == "ru"

    def test_user_default_currency_is_ils(self, db_session):
        """По умолчанию валюта — израильский шекель."""
        user = User(email="u@test.com", password_hash="hash", role="admin")
        db_session.add(user)
        db_session.commit()

        assert user.currency == "ILS"

    def test_user_unique_email_constraint(self, db_session):
        """
        Нельзя создать двух пользователей с одинаковым email.
        pytest.raises проверяет, что исключение ДЕЙСТВИТЕЛЬНО возникло.

        Если исключения нет — тест упадёт!
        Если исключение есть — тест пройдёт.
        """
        db_session.add(User(email="same@test.com", password_hash="h1", role="admin"))
        db_session.commit()

        db_session.add(User(email="same@test.com", password_hash="h2", role="admin"))

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()  # Откатываем после ошибки

    def test_admin_linked_to_kindergarten(self, db_session):
        """Администратор может быть привязан к садику."""
        kg = Kindergarten(name="Тестовый")
        db_session.add(kg)
        db_session.commit()

        admin = User(
            email="admin@test.com",
            password_hash=hash_password("pass"),
            role="admin",
            kindergarten_id=kg.id
        )
        db_session.add(admin)
        db_session.commit()

        assert admin.kindergarten_id == kg.id


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 3: Модель Child (ребёнок)
# ═══════════════════════════════════════════════════════════════════════

class TestChildModel:

    def test_create_child(self, db_session):
        """Создание ребёнка с привязкой к садику."""
        kg = Kindergarten(name="Тест")
        db_session.add(kg)
        db_session.commit()

        child = Child(
            kindergarten_id=kg.id,
            first_name="Аня",
            last_name="Иванова",
            birth_date=date(2020, 3, 10),
            status="активный",
            group="младшая",
            monthly_fee=3000.0
        )
        db_session.add(child)
        db_session.commit()

        assert child.id is not None
        assert child.first_name == "Аня"
        assert child.monthly_fee == 3000.0

    def test_child_default_group(self, db_session):
        """По умолчанию — младшая группа."""
        kg = Kindergarten(name="Тест")
        db_session.add(kg)
        db_session.commit()

        child = Child(
            kindergarten_id=kg.id,
            first_name="Петя",
            last_name="Сидоров"
        )
        db_session.add(child)
        db_session.commit()

        assert child.group == "младшая"
        assert child.status == "активный"

    @pytest.mark.parametrize("group", ["младшая", "средняя", "старшая"])
    def test_valid_groups(self, db_session, group):
        """
        Параметризация + fixture db_session:
        pytest создаёт новую сессию для каждого параметра.
        """
        kg = Kindergarten(name="Тест")
        db_session.add(kg)
        db_session.commit()

        child = Child(
            kindergarten_id=kg.id,
            first_name="Тест",
            last_name="Тестов",
            group=group
        )
        db_session.add(child)
        db_session.commit()

        assert child.group == group


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 4: Модель Payment (платёж)
# ═══════════════════════════════════════════════════════════════════════

class TestPaymentModel:

    def test_create_payment(self, db_session):
        """Создание платежа."""
        kg = Kindergarten(name="Тест")
        db_session.add(kg)
        db_session.commit()

        child = Child(
            kindergarten_id=kg.id,
            first_name="Вася",
            last_name="Пупкин",
            monthly_fee=2000.0
        )
        db_session.add(child)
        db_session.commit()

        payment = Payment(
            child_id=child.id,
            year=2026,
            month=4,
            amount=2000.0,
            paid_date=date(2026, 4, 1)
        )
        db_session.add(payment)
        db_session.commit()

        assert payment.id is not None
        assert payment.amount == 2000.0
        assert payment.year == 2026
        assert payment.month == 4

    def test_multiple_payments_same_month(self, db_session):
        """Можно добавить несколько платежей за один месяц (частичные оплаты)."""
        kg = Kindergarten(name="Тест")
        db_session.add(kg)
        db_session.commit()

        child = Child(kindergarten_id=kg.id, first_name="А", last_name="Б")
        db_session.add(child)
        db_session.commit()

        # Первая частичная оплата
        db_session.add(Payment(child_id=child.id, year=2026, month=4, amount=1000.0,
                                paid_date=date(2026, 4, 1)))
        # Вторая частичная оплата
        db_session.add(Payment(child_id=child.id, year=2026, month=4, amount=500.0,
                                paid_date=date(2026, 4, 15)))
        db_session.commit()

        count = db_session.query(Payment).filter_by(child_id=child.id).count()
        assert count == 2
