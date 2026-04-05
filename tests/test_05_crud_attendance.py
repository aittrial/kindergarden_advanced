"""
test_05_crud_attendance.py — Тесты журнала посещаемости

ТЕМА: Тестирование upsert-логики и связей таблиц
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Что изучаем в этом файле:

1. UPSERT логика: add_attendance обновляет запись, если она уже есть
2. Тестирование JOIN запросов (attendance + child)
3. Изоляция данных: посещаемость по садикам
4. Параметризация по статусам присутствия

Тестируем: функции посещаемости из crud.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import pytest
from datetime import date
import crud

TODAY = date(2026, 4, 5)
ANOTHER_DAY = date(2026, 4, 6)


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 1: Добавление записей посещаемости
# ═══════════════════════════════════════════════════════════════════════

class TestAddAttendance:

    def test_add_attendance_present(self, test_child, test_kindergarten):
        """Отмечаем ребёнка как присутствующего."""
        crud.add_attendance(test_child.id, TODAY, "присутствовал")

        records = crud.get_attendance_by_date(test_kindergarten, TODAY)
        assert len(records) == 1
        assert records[0].status == "присутствовал"

    @pytest.mark.parametrize("status", ["присутствовал", "отсутствовал", "болел"])
    def test_all_statuses_accepted(self, test_child, test_kindergarten, status):
        """Все три статуса принимаются системой."""
        crud.add_attendance(test_child.id, TODAY, status)

        records = crud.get_attendance_by_date(test_kindergarten, TODAY)
        assert records[0].status == status

    def test_attendance_linked_to_child(self, test_child, test_kindergarten):
        """Запись посещаемости привязана к правильному ребёнку."""
        crud.add_attendance(test_child.id, TODAY, "присутствовал")

        records = crud.get_attendance_by_date(test_kindergarten, TODAY)
        assert records[0].child_id == test_child.id

    def test_different_days_stored_separately(self, test_child, test_kindergarten):
        """Посещаемость за разные дни хранится раздельно."""
        crud.add_attendance(test_child.id, TODAY, "присутствовал")
        crud.add_attendance(test_child.id, ANOTHER_DAY, "болел")

        records_today = crud.get_attendance_by_date(test_kindergarten, TODAY)
        records_other = crud.get_attendance_by_date(test_kindergarten, ANOTHER_DAY)

        assert records_today[0].status == "присутствовал"
        assert records_other[0].status == "болел"


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 2: UPSERT логика (обновление существующей записи)
# ═══════════════════════════════════════════════════════════════════════

class TestAttendanceUpsert:
    """
    UPSERT = UPDATE or INSERT (обновить или добавить).

    Если запись за этот день уже есть — обновляем статус.
    Если нет — создаём новую.

    Это важно: нельзя иметь две записи для одного ребёнка за один день.
    """

    def test_update_existing_attendance(self, test_child, test_kindergarten):
        """
        Отметили 'присутствовал', потом исправили на 'болел'.
        Запись должна обновиться, а не задублироваться.
        """
        # Первая отметка
        crud.add_attendance(test_child.id, TODAY, "присутствовал")

        records_after_first = crud.get_attendance_by_date(test_kindergarten, TODAY)
        assert len(records_after_first) == 1
        assert records_after_first[0].status == "присутствовал"

        # Исправляем отметку
        crud.add_attendance(test_child.id, TODAY, "болел")

        # Запись должна быть одна, но с обновлённым статусом
        records_after_update = crud.get_attendance_by_date(test_kindergarten, TODAY)
        assert len(records_after_update) == 1, "Не должно быть дублирования!"
        assert records_after_update[0].status == "болел", "Статус должен обновиться"

    def test_multiple_updates_same_day(self, test_child, test_kindergarten):
        """Можно менять статус несколько раз — всегда сохраняется последний."""
        statuses = ["присутствовал", "отсутствовал", "болел", "присутствовал"]

        for status in statuses:
            crud.add_attendance(test_child.id, TODAY, status)

        records = crud.get_attendance_by_date(test_kindergarten, TODAY)

        assert len(records) == 1, "Только одна запись за день"
        assert records[0].status == "присутствовал", "Последний статус из списка"


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 3: Получение посещаемости
# ═══════════════════════════════════════════════════════════════════════

class TestGetAttendance:

    def test_get_attendance_by_date_empty(self, test_kindergarten):
        """Для пустого дня возвращается пустой список."""
        records = crud.get_attendance_by_date(test_kindergarten, TODAY)
        assert records == []

    def test_get_all_attendance_includes_child_info(
        self, test_child, test_kindergarten
    ):
        """
        get_all_attendance возвращает данные с JOIN по таблице children.
        Проверяем, что имена детей присутствуют в результате.
        """
        crud.add_attendance(test_child.id, TODAY, "присутствовал")

        all_records = crud.get_all_attendance(test_kindergarten)

        assert len(all_records) == 1
        record = all_records[0]

        # Проверяем, что JOIN сработал и вернул имена
        assert record["first_name"] == test_child.first_name
        assert record["last_name"] == test_child.last_name
        assert record["status"] == "присутствовал"
        assert record["date"] == TODAY

    def test_get_all_attendance_includes_group(self, test_child, test_kindergarten):
        """Данные о группе ребёнка тоже присутствуют (для фильтрации)."""
        crud.add_attendance(test_child.id, TODAY, "присутствовал")

        all_records = crud.get_all_attendance(test_kindergarten)
        assert "group" in all_records[0]

    def test_no_attendance_returns_empty(self, test_kindergarten):
        """Пустой журнал возвращает пустой список."""
        records = crud.get_all_attendance(test_kindergarten)
        assert records == []


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 4: Изоляция по садикам
# ═══════════════════════════════════════════════════════════════════════

class TestAttendanceIsolation:

    def test_attendance_isolated_by_kindergarten(
        self, test_kindergarten, second_kindergarten
    ):
        """
        Посещаемость одного садика не видна в другом.
        Проверяем мультитенантную изоляцию для журнала.
        """
        # Создаём ребёнка в первом садике
        crud.add_child(
            kindergarten_id=test_kindergarten,
            first_name="Ребёнок", last_name="Первого",
            birth_date=date(2020, 1, 1),
            parent_name="Родитель", parent_phone="050-0000000",
            enrollment_date=date(2023, 9, 1), status="активный"
        )
        child_kg1 = crud.get_all_children(test_kindergarten)[0]

        # Создаём ребёнка во втором садике
        crud.add_child(
            kindergarten_id=second_kindergarten,
            first_name="Ребёнок", last_name="Второго",
            birth_date=date(2020, 1, 1),
            parent_name="Другой родитель", parent_phone="050-9999999",
            enrollment_date=date(2023, 9, 1), status="активный"
        )
        child_kg2 = crud.get_all_children(second_kindergarten)[0]

        # Отмечаем посещаемость в обоих садиках
        crud.add_attendance(child_kg1.id, TODAY, "присутствовал")
        crud.add_attendance(child_kg2.id, TODAY, "болел")

        # Проверяем изоляцию
        att_kg1 = crud.get_attendance_by_date(test_kindergarten, TODAY)
        att_kg2 = crud.get_attendance_by_date(second_kindergarten, TODAY)

        assert len(att_kg1) == 1
        assert len(att_kg2) == 1
        assert att_kg1[0].status == "присутствовал"
        assert att_kg2[0].status == "болел"
