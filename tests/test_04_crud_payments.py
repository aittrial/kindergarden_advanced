"""
test_04_crud_payments.py — Тесты логики оплаты и должников

ТЕМА: Бизнес-логика и regression tests
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Что изучаем в этом файле:

1. REGRESSION TESTS — тесты на исправленные баги (чтобы не вернулись)
2. Тестирование БИЗНЕС-ЛОГИКИ — алгоритм определения должников
3. Граничные случаи (edge cases): 0, частичная, полная оплата
4. Сложные fixtures с зависимостями

ИСТОРИЯ БАГА:
    Если ежемесячный взнос = 3000, а родитель внёс только 1500,
    ребёнок показывался как "оплатил". Это было неправильно!

    Причина: система проверяла ФАКТ платежа, а не его СУММУ.
    Исправление: теперь суммируются все платежи за месяц через func.sum().

    Тест test_partial_payment_child_is_debtor — это REGRESSION TEST.
    Он гарантирует, что этот баг не вернётся.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import pytest
from datetime import date
import crud

# Тестовые данные
YEAR = 2026
MONTH = 4


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 1: Добавление платежей
# ═══════════════════════════════════════════════════════════════════════

class TestAddPayment:

    def test_add_single_payment(self, test_child_with_fee, test_kindergarten):
        """Добавляем один платёж и проверяем, что он сохранился."""
        crud.add_payment(
            child_id=test_child_with_fee.id,
            year=YEAR,
            month=MONTH,
            amount=3000.0,
            paid_date=date(2026, 4, 1),
            comment="Оплата за апрель"
        )

        payments = crud.get_all_payments(test_kindergarten)
        assert len(payments) == 1
        assert payments[0]["amount"] == 3000.0

    def test_add_multiple_payments_same_month(self, test_child_with_fee, test_kindergarten):
        """Можно добавить несколько частичных платежей за один месяц."""
        crud.add_payment(
            child_id=test_child_with_fee.id,
            year=YEAR, month=MONTH, amount=1500.0,
            paid_date=date(2026, 4, 1), comment="Первая часть"
        )
        crud.add_payment(
            child_id=test_child_with_fee.id,
            year=YEAR, month=MONTH, amount=1500.0,
            paid_date=date(2026, 4, 15), comment="Вторая часть"
        )

        payments = crud.get_all_payments(test_kindergarten)
        assert len(payments) == 2

        # Суммарно оплачено 3000
        total = sum(p["amount"] for p in payments)
        assert total == 3000.0

    def test_payment_stores_comment(self, test_child_with_fee, test_kindergarten):
        """Комментарий к платежу сохраняется."""
        crud.add_payment(
            child_id=test_child_with_fee.id,
            year=YEAR, month=MONTH, amount=3000.0,
            paid_date=date(2026, 4, 1), comment="Оплата наличными"
        )

        payments = crud.get_all_payments(test_kindergarten)
        assert payments[0]["comment"] == "Оплата наличными"


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 2: Логика определения должников
# ═══════════════════════════════════════════════════════════════════════

class TestDebtorLogic:
    """
    Это самые важные тесты — они проверяют бизнес-логику системы.
    Функция get_debtors() определяет, кто из родителей не оплатил.
    """

    @pytest.mark.smoke
    def test_no_payment_means_debtor(self, test_child_with_fee, test_kindergarten):
        """
        SMOKE-ТЕСТ: Ребёнок без платежей — должник.

        Взнос: 3000, оплачено: 0 → должник.
        """
        debtors = crud.get_debtors(test_kindergarten, YEAR, MONTH)

        assert len(debtors) == 1
        assert debtors[0].id == test_child_with_fee.id

    @pytest.mark.smoke
    def test_full_payment_means_not_debtor(self, test_child_with_fee, test_kindergarten):
        """
        SMOKE-ТЕСТ: Ребёнок с полной оплатой — НЕ должник.

        Взнос: 3000, оплачено: 3000 → не должник.
        """
        crud.add_payment(
            child_id=test_child_with_fee.id,
            year=YEAR, month=MONTH, amount=3000.0,
            paid_date=date(2026, 4, 1), comment=""
        )

        debtors = crud.get_debtors(test_kindergarten, YEAR, MONTH)

        assert len(debtors) == 0, "Полностью оплативший ребёнок не должник"

    @pytest.mark.regression
    def test_partial_payment_child_is_debtor(self, test_child_with_fee, test_kindergarten):
        """
        REGRESSION TEST — проверяет исправленный баг!

        БАГ: Если оплачено 1500 из 3000, система считала ребёнка оплатившим.
        ИСПРАВЛЕНИЕ: Теперь суммируются все платежи за месяц.

        Взнос: 3000, оплачено: 1500 → ребёнок ДОЛЖНИК (долг = 1500).

        Этот тест должен ВСЕГДА проходить. Если он падает — баг вернулся!
        """
        # Оплачена только ПОЛОВИНА взноса
        crud.add_payment(
            child_id=test_child_with_fee.id,
            year=YEAR, month=MONTH, amount=1500.0,  # только 1500 из 3000!
            paid_date=date(2026, 4, 1), comment="Частичная оплата"
        )

        debtors = crud.get_debtors(test_kindergarten, YEAR, MONTH)

        # Ребёнок должен быть в списке должников
        assert len(debtors) == 1, "Частично оплативший ребёнок — должник!"
        assert debtors[0].id == test_child_with_fee.id

    @pytest.mark.regression
    def test_partial_payment_correct_debt_amount(self, test_child_with_fee, test_kindergarten):
        """
        REGRESSION TEST: Сумма долга рассчитывается правильно.

        Взнос: 3000, оплачено: 1000 → долг = 2000.
        """
        crud.add_payment(
            child_id=test_child_with_fee.id,
            year=YEAR, month=MONTH, amount=1000.0,
            paid_date=date(2026, 4, 1), comment=""
        )

        debtors = crud.get_debtors(test_kindergarten, YEAR, MONTH)

        assert len(debtors) == 1
        # Долг сохраняется в _debt_amount (устанавливается в get_debtors)
        assert debtors[0]._debt_amount == 2000.0

    @pytest.mark.regression
    def test_multiple_partial_payments_summed(self, test_child_with_fee, test_kindergarten):
        """
        REGRESSION TEST: Несколько частичных платежей суммируются.

        Взнос: 3000, оплачено: 1000 + 1000 + 1000 = 3000 → не должник.
        """
        for i in range(3):
            crud.add_payment(
                child_id=test_child_with_fee.id,
                year=YEAR, month=MONTH, amount=1000.0,
                paid_date=date(2026, 4, i + 1), comment=f"Часть {i+1}"
            )

        debtors = crud.get_debtors(test_kindergarten, YEAR, MONTH)

        assert len(debtors) == 0, "3 платежа по 1000 = 3000 = полная оплата"

    def test_overpayment_not_debtor(self, test_child_with_fee, test_kindergarten):
        """Если оплатили больше взноса — всё равно не должник."""
        crud.add_payment(
            child_id=test_child_with_fee.id,
            year=YEAR, month=MONTH, amount=5000.0,  # переплата!
            paid_date=date(2026, 4, 1), comment=""
        )

        debtors = crud.get_debtors(test_kindergarten, YEAR, MONTH)
        assert len(debtors) == 0


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 3: Граничные случаи для должников
# ═══════════════════════════════════════════════════════════════════════

class TestDebtorEdgeCases:
    """
    Edge cases — граничные случаи, которые часто вызывают баги.
    """

    def test_child_without_fee_not_debtor(self, test_child, test_kindergarten):
        """
        Ребёнок БЕЗ установленного взноса (fee=0) не является должником.

        Нельзя быть должником, если нет суммы к оплате.
        """
        # test_child создан без monthly_fee (по умолчанию 0)
        debtors = crud.get_debtors(test_kindergarten, YEAR, MONTH)
        assert len(debtors) == 0, "Без взноса нет долга"

    def test_inactive_child_not_debtor(self, test_child_with_fee, test_kindergarten):
        """
        Неактивный ребёнок не проверяется на задолженность.

        Ребёнок, который выбыл из садика, не должен числиться должником.
        """
        # Деактивируем ребёнка
        crud.update_child(
            child_id=test_child_with_fee.id,
            first_name=test_child_with_fee.first_name,
            last_name=test_child_with_fee.last_name,
            birth_date=test_child_with_fee.birth_date,
            parent_name=test_child_with_fee.parent_name,
            parent_phone=test_child_with_fee.parent_phone,
            enrollment_date=test_child_with_fee.enrollment_date,
            status="выбыл"  # неактивный
        )

        debtors = crud.get_debtors(test_kindergarten, YEAR, MONTH)
        assert len(debtors) == 0, "Неактивный ребёнок не должник"

    def test_payment_in_different_month_not_counted(
        self, test_child_with_fee, test_kindergarten
    ):
        """
        Оплата за ДРУГОЙ месяц не засчитывается в текущий.

        Если оплачен март, но не оплачен апрель — должник в апреле.
        """
        # Оплата за МАРТ (а не апрель!)
        crud.add_payment(
            child_id=test_child_with_fee.id,
            year=YEAR, month=3,  # март, а не апрель
            amount=3000.0,
            paid_date=date(2026, 3, 1), comment="Оплата за март"
        )

        # Проверяем должников за АПРЕЛЬ
        debtors = crud.get_debtors(test_kindergarten, YEAR, MONTH)
        assert len(debtors) == 1, "Оплата за март не считается за апрель"

    @pytest.mark.parametrize("paid_amount,monthly_fee,should_be_debtor", [
        (0.0,    3000.0, True),   # ничего не заплатил
        (1.0,    3000.0, True),   # заплатил символически
        (1500.0, 3000.0, True),   # заплатил половину
        (2999.0, 3000.0, True),   # не хватает 1 шекеля
        (3000.0, 3000.0, False),  # заплатил точно
        (3001.0, 3000.0, False),  # заплатил с лишним
        (5000.0, 3000.0, False),  # заплатил намного больше
    ])
    def test_debtor_threshold(
        self, test_child_with_fee, test_kindergarten,
        paid_amount, monthly_fee, should_be_debtor
    ):
        """
        Параметризованный тест для разных сумм оплаты.

        Проверяем точный порог: должник если paid < fee.
        """
        # Устанавливаем взнос
        crud.update_child_fee(test_child_with_fee.id, monthly_fee)

        if paid_amount > 0:
            crud.add_payment(
                child_id=test_child_with_fee.id,
                year=YEAR, month=MONTH, amount=paid_amount,
                paid_date=date(2026, 4, 1), comment=""
            )

        debtors = crud.get_debtors(test_kindergarten, YEAR, MONTH)
        is_debtor = len(debtors) > 0

        assert is_debtor == should_be_debtor, (
            f"При взносе {monthly_fee} и оплате {paid_amount}: "
            f"ожидали {'должник' if should_be_debtor else 'не должник'}"
        )


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 4: Удаление платежей
# ═══════════════════════════════════════════════════════════════════════

class TestDeletePayment:

    def test_delete_payment(self, test_child_with_fee, test_kindergarten):
        """После удаления платёж не отображается."""
        crud.add_payment(
            child_id=test_child_with_fee.id,
            year=YEAR, month=MONTH, amount=3000.0,
            paid_date=date(2026, 4, 1), comment=""
        )

        payments = crud.get_all_payments(test_kindergarten)
        assert len(payments) == 1

        crud.delete_payment(payments[0]["id"])

        payments_after = crud.get_all_payments(test_kindergarten)
        assert len(payments_after) == 0

    def test_delete_payment_makes_child_debtor_again(
        self, test_child_with_fee, test_kindergarten
    ):
        """После удаления платежа ребёнок снова становится должником."""
        crud.add_payment(
            child_id=test_child_with_fee.id,
            year=YEAR, month=MONTH, amount=3000.0,
            paid_date=date(2026, 4, 1), comment=""
        )

        # После оплаты — не должник
        assert len(crud.get_debtors(test_kindergarten, YEAR, MONTH)) == 0

        # Удаляем платёж
        payments = crud.get_all_payments(test_kindergarten)
        crud.delete_payment(payments[0]["id"])

        # Снова должник
        assert len(crud.get_debtors(test_kindergarten, YEAR, MONTH)) == 1
