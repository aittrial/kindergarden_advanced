"""
test_01_auth.py — Тесты модуля аутентификации (auth.py)

ТЕМА: Базовые концепции pytest
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Что изучаем в этом файле:

1. СТРУКТУРА ТЕСТА — функция начинается с "test_"
2. ПАТТЕРН AAA — Arrange / Act / Assert (Подготовка / Действие / Проверка)
3. ASSERT — утверждение, которое должно быть True
4. pytest.mark.parametrize — один тест с разными входными данными
5. pytest.raises — проверка, что код вызывает исключение

Тестируем: auth.py (функции hash_password и verify_password)
Эти тесты НЕ нужна база данных — чистые unit-тесты.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import pytest
from auth import hash_password, verify_password


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 1: Тесты функции hash_password()
# ═══════════════════════════════════════════════════════════════════════

class TestHashPassword:
    """
    Группировка тестов в класс — удобно для организации.
    Название класса должно начинаться с "Test".
    """

    def test_returns_string(self):
        """
        Паттерн AAA (Arrange / Act / Assert):

        Arrange — подготовка данных
        Act     — вызов тестируемой функции
        Assert  — проверка результата
        """
        # Arrange
        password = "mypassword123"

        # Act
        result = hash_password(password)

        # Assert
        assert isinstance(result, str), "Хэш должен быть строкой"

    def test_hash_is_not_plaintext(self):
        """Хэш не должен совпадать с исходным паролем — это было бы небезопасно."""
        password = "secret"

        hashed = hash_password(password)

        assert hashed != password, "Хэш не должен совпадать с исходным паролем"

    def test_sha256_length(self):
        """
        SHA-256 всегда производит хэш длиной ровно 64 символа.
        Это фиксированная длина, независимо от длины пароля.
        """
        hashed = hash_password("любой пароль")

        assert len(hashed) == 64, f"SHA-256 хэш должен быть 64 символа, получили {len(hashed)}"

    def test_deterministic(self):
        """
        Детерминированность: один и тот же пароль ВСЕГДА даёт одинаковый хэш.
        Это важно — иначе нельзя будет проверить пароль при следующем входе.
        """
        password = "consistent_password"

        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 == hash2, "Один и тот же пароль должен давать одинаковый хэш"

    def test_different_passwords_produce_different_hashes(self):
        """Разные пароли должны давать разные хэши."""
        hash1 = hash_password("password1")
        hash2 = hash_password("password2")

        assert hash1 != hash2, "Разные пароли должны давать разные хэши"

    def test_empty_string(self):
        """
        Граничный случай (edge case): пустая строка тоже хэшируется.
        Edge cases — важная часть тестирования!
        """
        result = hash_password("")

        assert isinstance(result, str)
        assert len(result) == 64

    def test_long_password(self):
        """Граничный случай: очень длинный пароль."""
        long_password = "a" * 1000

        result = hash_password(long_password)

        # SHA-256 всегда 64 символа, независимо от длины входа
        assert len(result) == 64

    def test_unicode_password(self):
        """Пароли на кириллице и других языках тоже работают."""
        result = hash_password("пароль на русском языке")

        assert isinstance(result, str)
        assert len(result) == 64


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 2: Тесты функции verify_password()
# ═══════════════════════════════════════════════════════════════════════

class TestVerifyPassword:

    def test_correct_password_returns_true(self):
        """Правильный пароль должен успешно верифицироваться."""
        # Arrange
        password = "correct_password"
        hashed = hash_password(password)

        # Act
        result = verify_password(password, hashed)

        # Assert
        assert result is True, "Верный пароль должен возвращать True"

    def test_wrong_password_returns_false(self):
        """Неправильный пароль должен быть отклонён."""
        hashed = hash_password("correct_password")

        result = verify_password("wrong_password", hashed)

        assert result is False, "Неверный пароль должен возвращать False"

    def test_case_sensitive(self):
        """Пароли чувствительны к регистру: 'Password' ≠ 'password'."""
        hashed = hash_password("Password")

        assert verify_password("password", hashed) is False  # строчные — не то
        assert verify_password("Password", hashed) is True   # правильный регистр

    def test_empty_password_rejected(self):
        """Пустой пароль не совпадает с хэшем настоящего пароля."""
        hashed = hash_password("real_password")

        assert verify_password("", hashed) is False

    def test_similar_passwords_rejected(self):
        """Похожие, но не одинаковые пароли должны быть отклонены."""
        hashed = hash_password("password")

        assert verify_password("password ", hashed) is False   # пробел в конце
        assert verify_password(" password", hashed) is False   # пробел в начале
        assert verify_password("password1", hashed) is False   # лишний символ


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 3: Параметризованные тесты
# ═══════════════════════════════════════════════════════════════════════

class TestParametrized:
    """
    pytest.mark.parametrize позволяет запустить один тест с разными данными.

    Вместо того чтобы писать 5 одинаковых тестов — пишем один с параметрами.
    pytest запустит его столько раз, сколько параметров указано.
    """

    @pytest.mark.parametrize("password", [
        "short",                    # короткий
        "a" * 100,                  # очень длинный
        "пароль на русском",        # кириллица
        "p@$$w0rd!",                # спецсимволы
        "   spaces   ",             # пробелы
        "12345678",                 # только цифры
        "UPPERCASE",                # только заглавные
    ])
    def test_any_password_can_be_hashed_and_verified(self, password):
        """
        Любой пароль можно захэшировать и верифицировать.

        Параметр password принимает каждое значение из списка по очереди.
        pytest запустит этот тест 7 раз — по одному для каждого пароля.
        """
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    @pytest.mark.parametrize("wrong_password,correct_password", [
        ("admin",    "admin123"),
        ("password", "p@ssword"),
        ("123456",   "1234567"),
        ("",         "notempty"),
    ])
    def test_wrong_passwords_rejected(self, wrong_password, correct_password):
        """
        Параметризация с несколькими параметрами.
        Каждая пара (wrong, correct) проверяется отдельно.
        """
        hashed = hash_password(correct_password)
        assert verify_password(wrong_password, hashed) is False


# ═══════════════════════════════════════════════════════════════════════
# РАЗДЕЛ 4: Тесты с маркерами (markers)
# ═══════════════════════════════════════════════════════════════════════

class TestWithMarkers:
    """
    Маркеры позволяют группировать тесты и запускать их выборочно.

    Запустить только smoke-тесты: pytest -m smoke
    Запустить только regression:  pytest -m regression
    """

    @pytest.mark.smoke
    def test_basic_auth_flow(self):
        """
        Smoke-тест: базовая проверка — система вообще работает?
        Smoke-тесты запускают первыми, они быстрые и проверяют самое важное.
        """
        password = "admin123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    @pytest.mark.regression
    def test_hash_is_hex_string(self):
        """
        Regression-тест: SHA-256 хэш — это шестнадцатеричная строка (0-9, a-f).
        Regression-тесты проверяют, что исправленные баги не вернулись.
        """
        hashed = hash_password("test")
        # Каждый символ должен быть шестнадцатеричным
        assert all(c in "0123456789abcdef" for c in hashed)
