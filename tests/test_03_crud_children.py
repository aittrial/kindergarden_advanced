"""
test_03_crud_children.py — Тесты CRUD операций для детей

ТЕМА: Integration tests и изоляция данных
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Что изучаем в этом файле:

1. INTEGRATION TESTS — тестируем несколько слоёв вместе (crud + БД)
2. ИЗОЛЯЦИЯ ДАННЫХ — каждый садик видит только своих детей
3. Цепочка операций: добавить → получить → изменить → удалить
4. Зависимые fixtures: test_child зависит от test_kindergarten

Тестируем: функции из crud.py для работы с детьми
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import pytest
from datetime import date
import crud


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 1: Базовые операции (CRUD)
# ═══════════════════════════════════════════════════════════════════════

class TestAddChild:
    """Тесты функции crud.add_child()"""

    def test_add_child_successfully(self, test_kindergarten):
        """
        test_kindergarten — fixture из conftest.py.
        Он уже создал садик и вернул его ID.
        """
        # Act
        crud.add_child(
            kindergarten_id=test_kindergarten,
            first_name="Алиса",
            last_name="Wonderland",
            birth_date=date(2020, 6, 1),
            parent_name="Анна Wonderland",
            parent_phone="050-1111111",
            enrollment_date=date(2023, 9, 1),
            status="активный",
            group="младшая"
        )

        # Assert: ребёнок появился в БД
        children = crud.get_all_children(test_kindergarten)
        assert len(children) == 1
        assert children[0].first_name == "Алиса"

    def test_add_multiple_children(self, test_kindergarten):
        """Добавляем нескольких детей и проверяем их количество."""
        names = [("Аня", "Иванова"), ("Боря", "Петров"), ("Вася", "Сидоров")]

        for first, last in names:
            crud.add_child(
                kindergarten_id=test_kindergarten,
                first_name=first, last_name=last,
                birth_date=date(2020, 1, 1),
                parent_name="Родитель", parent_phone="050-0000000",
                enrollment_date=date(2023, 9, 1),
                status="активный"
            )

        children = crud.get_all_children(test_kindergarten)
        assert len(children) == 3

    def test_child_saved_with_correct_data(self, test_kindergarten):
        """Данные ребёнка сохраняются правильно."""
        birth = date(2019, 12, 25)
        enroll = date(2023, 9, 1)

        crud.add_child(
            kindergarten_id=test_kindergarten,
            first_name="Максим",
            last_name="Зверев",
            birth_date=birth,
            parent_name="Зверев Павел",
            parent_phone="054-9999999",
            enrollment_date=enroll,
            status="активный",
            group="средняя"
        )

        children = crud.get_all_children(test_kindergarten)
        child = children[0]

        assert child.first_name == "Максим"
        assert child.last_name == "Зверев"
        assert child.birth_date == birth
        assert child.parent_name == "Зверев Павел"
        assert child.group == "средняя"

    @pytest.mark.parametrize("group", ["младшая", "средняя", "старшая"])
    def test_add_child_different_groups(self, test_kindergarten, group):
        """Дети могут быть добавлены в разные группы."""
        crud.add_child(
            kindergarten_id=test_kindergarten,
            first_name="Тест", last_name="Тестов",
            birth_date=date(2020, 1, 1),
            parent_name="Родитель", parent_phone="050-0000000",
            enrollment_date=date(2023, 9, 1),
            status="активный",
            group=group
        )

        children = crud.get_all_children(test_kindergarten)
        assert children[0].group == group


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 2: Обновление данных
# ═══════════════════════════════════════════════════════════════════════

class TestUpdateChild:
    """Тесты функций обновления данных ребёнка."""

    def test_update_child_basic_info(self, test_child):
        """
        test_child — fixture, который уже создал ребёнка.
        Мы просто обновляем его данные.
        """
        crud.update_child(
            child_id=test_child.id,
            first_name="Иван",
            last_name="Новиков",          # изменили фамилию
            birth_date=test_child.birth_date,
            parent_name="Новиков Сергей", # изменили имя родителя
            parent_phone="050-9999999",
            enrollment_date=test_child.enrollment_date,
            status="активный"
        )

        # Загружаем обновлённые данные из БД
        children = crud.get_all_children(test_child.kindergarten_id)
        updated = children[0]

        assert updated.last_name == "Новиков"
        assert updated.parent_name == "Новиков Сергей"

    def test_update_child_group(self, test_child):
        """Перевод ребёнка из одной группы в другую."""
        # Начальная группа — младшая (задана в fixture)
        assert test_child.group == "младшая"

        crud.update_child_group(test_child.id, "средняя")

        children = crud.get_all_children(test_child.kindergarten_id)
        assert children[0].group == "средняя"

    def test_update_child_fee(self, test_child):
        """Установка ежемесячного взноса."""
        crud.update_child_fee(test_child.id, 3500.0)

        children = crud.get_all_children(test_child.kindergarten_id)
        assert children[0].monthly_fee == 3500.0

    def test_deactivate_child(self, test_child):
        """Деактивация ребёнка (смена статуса)."""
        crud.update_child(
            child_id=test_child.id,
            first_name=test_child.first_name,
            last_name=test_child.last_name,
            birth_date=test_child.birth_date,
            parent_name=test_child.parent_name,
            parent_phone=test_child.parent_phone,
            enrollment_date=test_child.enrollment_date,
            status="выбыл"  # ← меняем статус
        )

        children = crud.get_all_children(test_child.kindergarten_id)
        assert children[0].status == "выбыл"


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 3: Удаление
# ═══════════════════════════════════════════════════════════════════════

class TestDeleteChild:

    def test_delete_child(self, test_child, test_kindergarten):
        """После удаления ребёнка нет в БД."""
        # Убеждаемся, что ребёнок есть
        children_before = crud.get_all_children(test_kindergarten)
        assert len(children_before) == 1

        # Удаляем
        crud.delete_child(test_child.id)

        # Проверяем, что пустой список
        children_after = crud.get_all_children(test_kindergarten)
        assert len(children_after) == 0

    def test_delete_nonexistent_child_no_error(self, test_kindergarten):
        """Удаление несуществующего ребёнка не вызывает ошибку."""
        fake_id = 99999

        # Не должно быть исключения
        crud.delete_child(fake_id)


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 4: ИЗОЛЯЦИЯ ДАННЫХ (мультитенантность)
# ═══════════════════════════════════════════════════════════════════════

class TestDataIsolation:
    """
    ВАЖНО: Каждый садик должен видеть ТОЛЬКО СВОИХ детей.
    Это ключевое требование мультитенантной архитектуры.
    """

    def test_child_belongs_to_correct_kindergarten(
        self, test_kindergarten, second_kindergarten
    ):
        """
        test_kindergarten и second_kindergarten — два разных садика.
        Дети первого не должны быть видны второму.
        """
        # Добавляем ребёнка в первый садик
        crud.add_child(
            kindergarten_id=test_kindergarten,
            first_name="В первом садике", last_name="Тестов",
            birth_date=date(2020, 1, 1),
            parent_name="Родитель", parent_phone="050-0000000",
            enrollment_date=date(2023, 9, 1), status="активный"
        )

        # Добавляем ребёнка во второй садик
        crud.add_child(
            kindergarten_id=second_kindergarten,
            first_name="Во втором садике", last_name="Другов",
            birth_date=date(2020, 1, 1),
            parent_name="Другой родитель", parent_phone="050-9999999",
            enrollment_date=date(2023, 9, 1), status="активный"
        )

        # Проверяем изоляцию
        children_kg1 = crud.get_all_children(test_kindergarten)
        children_kg2 = crud.get_all_children(second_kindergarten)

        assert len(children_kg1) == 1, "В первом садике должен быть 1 ребёнок"
        assert len(children_kg2) == 1, "Во втором садике должен быть 1 ребёнок"
        assert children_kg1[0].first_name == "В первом садике"
        assert children_kg2[0].first_name == "Во втором садике"

    def test_empty_kindergarten_returns_no_children(self, test_kindergarten):
        """Пустой садик возвращает пустой список, не None."""
        children = crud.get_all_children(test_kindergarten)

        assert children is not None
        assert len(children) == 0
        assert isinstance(children, list)
