"""
test_06_i18n.py — Тесты системы переводов и форматирования (i18n.py)

ТЕМА: Тестирование без базы данных + мокирование зависимостей
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Что изучаем в этом файле:

1. UNIT TESTS без БД — тестируем чистую бизнес-логику
2. unittest.mock.patch — временная замена зависимостей
3. Тестирование словарей (dict) и структур данных
4. Параметризация для проверки всех языков и валют

ПРОБЛЕМА: i18n.py использует st.session_state (Streamlit).
Вне работающего Streamlit приложения это вызовет ошибку.

РЕШЕНИЕ: Мы "мокируем" (mock) session_state — заменяем его обычным словарём
на время теста. Функции i18n.py даже не знают, что работают с моком.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import pytest
from unittest.mock import patch

from i18n import (
    TRANSLATIONS, CURRENCIES, MONTHS,
    ATTENDANCE_STATUSES, ATTENDANCE_DISPLAY,
    CHILD_GROUPS, CHILD_GROUP_DISPLAY,
    EXPENSE_CATEGORIES, EXPENSE_CATEGORY_DISPLAY,
    PRODUCT_UNITS, CHILD_STATUSES,
)
import i18n


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 1: Структура словаря переводов
# ═══════════════════════════════════════════════════════════════════════

class TestTranslationsStructure:
    """
    Эти тесты проверяют СТРУКТУРУ данных, а не поведение функций.
    БД не нужна. Streamlit не нужен. Простые dict-проверки.
    """

    def test_both_languages_exist(self):
        """Словарь переводов содержит оба языка."""
        assert "ru" in TRANSLATIONS
        assert "en" in TRANSLATIONS

    def test_same_keys_in_both_languages(self):
        """
        Все ключи русского перевода должны быть и в английском.
        Если добавили ключ только в одном языке — это баг!
        """
        ru_keys = set(TRANSLATIONS["ru"].keys())
        en_keys = set(TRANSLATIONS["en"].keys())

        # Ключи, которые есть в RU но нет в EN
        missing_in_en = ru_keys - en_keys
        # Ключи, которые есть в EN но нет в RU
        missing_in_ru = en_keys - ru_keys

        assert not missing_in_en, f"Эти ключи есть в RU, но нет в EN: {missing_in_en}"
        assert not missing_in_ru, f"Эти ключи есть в EN, но нет в RU: {missing_in_ru}"

    def test_no_empty_translations(self):
        """Ни один перевод не должен быть пустой строкой."""
        for lang, translations in TRANSLATIONS.items():
            for key, value in translations.items():
                assert value != "", f"Пустой перевод: [{lang}][{key}]"

    @pytest.mark.parametrize("key", [
        "app_title", "sign_in", "sign_out",
        "nav_children", "nav_attendance", "nav_products",
        "nav_expenses", "nav_reports", "nav_payments",
    ])
    def test_critical_keys_exist(self, key):
        """
        Параметризованный тест: критически важные ключи должны существовать
        в обоих языках. Это smoke-тест для системы переводов.
        """
        assert key in TRANSLATIONS["ru"], f"Ключ '{key}' отсутствует в RU"
        assert key in TRANSLATIONS["en"], f"Ключ '{key}' отсутствует в EN"

    def test_translations_are_different_languages(self):
        """RU и EN переводы не должны быть идентичными."""
        # Берём несколько ключей и проверяем, что переводы разные
        different_keys = ["sign_in", "sign_out", "nav_children"]
        for key in different_keys:
            ru_val = TRANSLATIONS["ru"][key]
            en_val = TRANSLATIONS["en"][key]
            assert ru_val != en_val, (
                f"Ключ '{key}': RU='{ru_val}' совпадает с EN='{en_val}'"
            )


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 2: Тестирование функции t() с мокированием session_state
# ═══════════════════════════════════════════════════════════════════════

class TestTranslationFunction:
    """
    Тестируем функцию t(key) — основную функцию перевода.

    Проблема: t() вызывает get_lang(), которая читает st.session_state.
    Решение: используем patch() для замены session_state словарём.

    patch() работает как контекстный менеджер:
    with patch(...):
        # здесь session_state = наш словарь
    # после блока — session_state возвращается в исходное состояние
    """

    def test_russian_translation(self):
        """Функция t() возвращает русский перевод."""
        # Мокируем session_state: устанавливаем язык "ru"
        with patch.object(i18n.st, "session_state", {"lang": "ru", "currency": "ILS"}):
            result = i18n.t("sign_in")
        assert result == "Войти"

    def test_english_translation(self):
        """Функция t() возвращает английский перевод."""
        with patch.object(i18n.st, "session_state", {"lang": "en", "currency": "USD"}):
            result = i18n.t("sign_in")
        assert result == "Sign In"

    def test_missing_key_returns_key_itself(self):
        """
        Если ключ не найден — возвращается сам ключ.
        Это защита от ошибок: лучше показать технический ключ, чем упасть.
        """
        with patch.object(i18n.st, "session_state", {"lang": "ru", "currency": "ILS"}):
            result = i18n.t("nonexistent_key_12345")
        assert result == "nonexistent_key_12345"

    def test_unknown_language_falls_back_to_russian(self):
        """Неизвестный язык возвращает русский перевод (запасной вариант)."""
        with patch.object(i18n.st, "session_state", {"lang": "fr", "currency": "EUR"}):
            result = i18n.t("sign_in")
        assert result == "Войти"  # fallback на ru

    @pytest.mark.parametrize("lang,expected", [
        ("ru", "Войти"),
        ("en", "Sign In"),
    ])
    def test_translation_parametrized(self, lang, expected):
        """Параметризованная проверка переводов для разных языков."""
        with patch.object(i18n.st, "session_state", {"lang": lang, "currency": "ILS"}):
            result = i18n.t("sign_in")
        assert result == expected


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 3: Тестирование валют
# ═══════════════════════════════════════════════════════════════════════

class TestCurrencies:

    def test_three_currencies_defined(self):
        """Должно быть ровно 3 поддерживаемые валюты."""
        assert len(CURRENCIES) == 3

    @pytest.mark.parametrize("currency,symbol", [
        ("ILS", "₪"),
        ("USD", "$"),
        ("EUR", "€"),
    ])
    def test_currency_symbols(self, currency, symbol):
        """Каждая валюта имеет правильный символ."""
        assert CURRENCIES[currency]["symbol"] == symbol

    def test_currencies_have_names_in_both_languages(self):
        """У каждой валюты есть названия на русском и английском."""
        for code, data in CURRENCIES.items():
            assert "name_ru" in data, f"Нет name_ru для {code}"
            assert "name_en" in data, f"Нет name_en для {code}"
            assert data["name_ru"] != "", f"Пустое name_ru для {code}"
            assert data["name_en"] != "", f"Пустое name_en для {code}"

    def test_format_amount_ils(self):
        """Форматирование суммы в шекелях."""
        with patch.object(i18n.st, "session_state", {"lang": "ru", "currency": "ILS"}):
            result = i18n.format_amount(1500.0)
        assert "₪" in result
        assert "1,500.00" in result

    def test_format_amount_usd(self):
        """Форматирование суммы в долларах."""
        with patch.object(i18n.st, "session_state", {"lang": "en", "currency": "USD"}):
            result = i18n.format_amount(250.50)
        assert "$" in result
        assert "250.50" in result

    def test_format_amount_eur(self):
        """Форматирование суммы в евро."""
        with patch.object(i18n.st, "session_state", {"lang": "en", "currency": "EUR"}):
            result = i18n.format_amount(100.0)
        assert "€" in result

    def test_format_zero_amount(self):
        """Нулевая сумма форматируется без ошибок."""
        with patch.object(i18n.st, "session_state", {"lang": "ru", "currency": "ILS"}):
            result = i18n.format_amount(0.0)
        assert "0.00" in result


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 4: Тестирование справочных данных
# ═══════════════════════════════════════════════════════════════════════

class TestReferenceData:
    """
    Тесты для справочников: статусы, группы, категории.
    Эти данные используются в UI — важно, чтобы они были правильными.
    """

    def test_attendance_statuses_count(self):
        """Ровно 3 статуса посещаемости."""
        assert len(ATTENDANCE_STATUSES) == 3

    def test_attendance_statuses_content(self):
        """Правильные статусы посещаемости."""
        assert "присутствовал" in ATTENDANCE_STATUSES
        assert "отсутствовал" in ATTENDANCE_STATUSES
        assert "болел" in ATTENDANCE_STATUSES

    def test_attendance_display_both_languages(self):
        """Статусы посещаемости переведены на оба языка."""
        for status in ATTENDANCE_STATUSES:
            assert status in ATTENDANCE_DISPLAY["ru"]
            assert status in ATTENDANCE_DISPLAY["en"]

    def test_child_groups_count(self):
        """Ровно 3 группы детей."""
        assert len(CHILD_GROUPS) == 3

    def test_child_groups_content(self):
        """Правильные названия групп."""
        assert "младшая" in CHILD_GROUPS
        assert "средняя" in CHILD_GROUPS
        assert "старшая" in CHILD_GROUPS

    def test_expense_categories_exist(self):
        """Категории расходов определены."""
        assert len(EXPENSE_CATEGORIES) > 0
        assert "Еда" in EXPENSE_CATEGORIES
        assert "Другое" in EXPENSE_CATEGORIES

    def test_product_units_exist(self):
        """Единицы измерения для продуктов определены."""
        assert len(PRODUCT_UNITS) > 0

    @pytest.mark.parametrize("status_ru,status_en", [
        ("присутствовал", "present"),
        ("отсутствовал",  "absent"),
        ("болел",         "sick"),
    ])
    def test_attendance_display_values(self, status_ru, status_en):
        """Конкретные значения переводов статусов посещаемости."""
        assert ATTENDANCE_DISPLAY["ru"][status_ru] == status_ru  # ru = как есть
        assert ATTENDANCE_DISPLAY["en"][status_ru] == status_en  # en = переводим

    @pytest.mark.parametrize("group_ru,group_en", [
        ("младшая", "Junior"),
        ("средняя", "Middle"),
        ("старшая", "Senior"),
    ])
    def test_group_display_values(self, group_ru, group_en):
        """Конкретные значения переводов групп."""
        assert CHILD_GROUP_DISPLAY["en"][group_ru] == group_en


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 5: Месяцы
# ═══════════════════════════════════════════════════════════════════════

class TestMonths:

    def test_twelve_months_in_each_language(self):
        """В каждом языке ровно 12 месяцев."""
        assert len(MONTHS["ru"]) == 12
        assert len(MONTHS["en"]) == 12

    @pytest.mark.parametrize("month_num,expected_ru,expected_en", [
        (1,  "Январь",   "January"),
        (6,  "Июнь",     "June"),
        (12, "Декабрь",  "December"),
    ])
    def test_month_names(self, month_num, expected_ru, expected_en):
        """Проверяем конкретные названия месяцев."""
        # Месяцы хранятся с индексом 0, поэтому month_num - 1
        assert MONTHS["ru"][month_num - 1] == expected_ru
        assert MONTHS["en"][month_num - 1] == expected_en

    def test_month_name_function(self):
        """Функция month_name() возвращает правильное название."""
        with patch.object(i18n.st, "session_state", {"lang": "ru", "currency": "ILS"}):
            result = i18n.month_name(1)
        assert result == "Январь"

    def test_month_name_english(self):
        """month_name() работает для английского языка."""
        with patch.object(i18n.st, "session_state", {"lang": "en", "currency": "USD"}):
            result = i18n.month_name(6)
        assert result == "June"
