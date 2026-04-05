# Testing Guide
# Kindergarten Management System — PyTest Guide (EN)

**Version:** 1.0 | **Date:** April 2026  
**Audience:** QA Testing Students

---

## Table of Contents
1. [What is Testing?](#1-what-is-testing)
2. [Setup and Running](#2-setup-and-running)
3. [Test Structure](#3-test-structure)
4. [Pytest Concepts](#4-pytest-concepts)
5. [Test Files Description](#5-test-files-description)
6. [Running Specific Tests](#6-running-specific-tests)
7. [Understanding Results](#7-understanding-results)
8. [Student Exercises](#8-student-exercises)

---

## 1. What is Testing?

A **test** is code that verifies that other code works correctly.

```
A program without tests = A plane without a pre-flight check.
```

### Types of Tests in This Project

| Type | What it checks | File |
|------|---------------|------|
| **Unit test** | A single function in isolation | test_01_auth.py, test_06_i18n.py |
| **Integration test** | Multiple layers together (function + DB) | test_03, test_04, test_05 |
| **Smoke test** | Most critical functions work | `@pytest.mark.smoke` |
| **Regression test** | Fixed bugs haven't returned | `@pytest.mark.regression` |

### AAA Pattern (Arrange / Act / Assert)

Every test follows three steps:

```python
def test_example():
    # Arrange — prepare the data
    password = "mypassword"
    
    # Act — execute the action being tested
    hashed = hash_password(password)
    
    # Assert — verify the result
    assert hashed != password
```

---

## 2. Setup and Running

### Step 1: Install dependencies
```bash
# From the project root folder (kindergarden/)
pip install -r requirements.txt
pip install pytest
```

### Step 2: Run all tests
```bash
# From the project root folder (kindergarden/)
pytest
```

### Step 3: Run with verbose output
```bash
pytest -v
```

**Example output:**
```
tests/test_01_auth.py::TestHashPassword::test_returns_string         PASSED
tests/test_01_auth.py::TestHashPassword::test_hash_is_not_plaintext  PASSED
tests/test_01_auth.py::TestVerifyPassword::test_correct_password      PASSED
...
========================= 52 passed in 3.21s =========================
```

---

## 3. Test Structure

```
kindergarden/
├── pytest.ini                    ← pytest configuration
├── tests/
│   ├── conftest.py               ← Shared fixtures (loaded automatically)
│   ├── requirements_test.txt     ← Test dependencies
│   ├── test_01_auth.py           ← Password hashing (Unit)
│   ├── test_02_models.py         ← DB models (Integration)
│   ├── test_03_crud_children.py  ← CRUD children (Integration)
│   ├── test_04_crud_payments.py  ← Payments & debtors (Integration + Regression)
│   ├── test_05_crud_attendance.py← Attendance (Integration)
│   └── test_06_i18n.py           ← Translations & currencies (Unit + Mock)
└── docs/
    ├── TEST_GUIDE_RU.md
    └── TEST_GUIDE_EN.md          ← This file
```

### Why SQLite instead of Neon.tech?

| SQLite in-memory | Neon.tech (production) |
|-----------------|----------------------|
| Instant (no network) | 1-3 sec per request |
| Fresh DB for each test | Data persists between tests |
| No internet required | Requires connection |
| Won't corrupt real data | May corrupt production data |

**Rule: Never test against a production database!**

---

## 4. Pytest Concepts

### 4.1 Fixtures — Ready-made data for tests

A fixture is a function that prepares data before a test and cleans up after.

```python
# Fixture defined in conftest.py:
@pytest.fixture
def test_kindergarten():
    kg_id = crud.add_kindergarten(name="Test Kindergarten", ...)
    return kg_id

# In a test — just add the fixture name as a parameter:
def test_something(test_kindergarten):
    # test_kindergarten is already created and contains the kindergarten ID
    children = crud.get_all_children(test_kindergarten)
```

**Autouse fixture** — applied to ALL tests automatically:
```python
@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    # Runs before each test
    Base.metadata.create_all(bind=TEST_ENGINE)
    monkeypatch.setattr(crud, "SessionLocal", TestSessionLocal)
    
    yield  # Test runs here
    
    # Runs after each test
    Base.metadata.drop_all(bind=TEST_ENGINE)
```

### 4.2 parametrize — One test, many data points

```python
@pytest.mark.parametrize("password", [
    "short",
    "a" * 100,
    "unicode password",
])
def test_any_password_works(password):
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    
# pytest runs this test 3 times, once for each password
```

### 4.3 markers — Test categories

```python
@pytest.mark.smoke
def test_critical():
    ...

@pytest.mark.regression  
def test_fixed_bug():
    ...
```

Run by marker:
```bash
pytest -m smoke        # smoke tests only
pytest -m regression   # regression tests only
pytest -m "not smoke"  # everything except smoke
```

### 4.4 pytest.raises — Expected errors

```python
def test_duplicate_email_raises_error(db_session):
    db_session.add(User(email="same@test.com", ...))
    db_session.commit()
    
    db_session.add(User(email="same@test.com", ...))  # duplicate!
    
    with pytest.raises(IntegrityError):
        db_session.commit()  # We EXPECT IntegrityError
    # If no error occurs — test FAILS
    # If error occurs — test PASSES
```

### 4.5 Mock — Replacing dependencies

When a function depends on an external system (Streamlit, network, DB),
we use a mock — a temporary replacement:

```python
from unittest.mock import patch

def test_russian_translation():
    # patch.object replaces st.session_state with a regular dict
    with patch.object(i18n.st, "session_state", {"lang": "ru", "currency": "ILS"}):
        result = i18n.t("sign_in")
    
    assert result == "Войти"
# After the 'with' block — session_state is restored to its original state
```

---

## 5. Test Files Description

### test_01_auth.py — Authentication
**Concepts:** AAA, assert, parametrize, markers  
**No DB:** Pure unit tests for `hash_password()` and `verify_password()`

Key tests:
- `test_returns_string` — hash is a string
- `test_deterministic` — same password = same hash
- `test_case_sensitive` — "Password" ≠ "password"
- `test_various_password_formats` — parametrized password formats

### test_02_models.py — Database Models
**Concepts:** db_session fixture, IntegrityError, defaults  
**With DB:** Direct SQLAlchemy object creation

Key tests:
- `test_user_unique_email_constraint` — UNIQUE database constraint
- `test_child_default_group` — default values
- `test_multiple_payments_same_month` — partial payments allowed

### test_03_crud_children.py — CRUD Operations
**Concepts:** Integration tests, dependent fixtures, data isolation

Key tests:
- `test_child_belongs_to_correct_kindergarten` — multi-tenancy
- `test_update_child_group` — switching between groups
- `test_delete_nonexistent_child_no_error` — graceful handling

### test_04_crud_payments.py — Payments and Debtors
**Concepts:** Regression tests, edge cases, complex parametrize  
**Most important tests in the project!**

Key tests:
- `test_partial_payment_child_is_debtor` — **REGRESSION**: partial payment ≠ full
- `test_multiple_partial_payments_summed` — payments are summed
- `test_debtor_threshold` — parametrized threshold values
- `test_inactive_child_not_debtor` — inactive children not checked

### test_05_crud_attendance.py — Attendance
**Concepts:** Upsert logic, JOIN queries

Key tests:
- `test_update_existing_attendance` — upsert: update, not duplicate
- `test_multiple_updates_same_day` — last status wins
- `test_attendance_isolated_by_kindergarten` — isolation per kindergarten

### test_06_i18n.py — Translations and Currencies
**Concepts:** Mock (patch.object), structural dict tests

Key tests:
- `test_same_keys_in_both_languages` — translation synchronization
- `test_missing_key_returns_key_itself` — safe fallback
- `test_format_amount_ils` — amount formatting with symbol

---

## 6. Running Specific Tests

```bash
# One file
pytest tests/test_01_auth.py

# One class
pytest tests/test_01_auth.py::TestHashPassword

# One specific test
pytest tests/test_04_crud_payments.py::TestDebtorLogic::test_partial_payment_child_is_debtor

# By marker
pytest -m smoke
pytest -m regression

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Show 5 slowest tests
pytest --durations=5

# Tests containing "payment" in the name
pytest -k "payment"

# Quiet output (dots instead of names)
pytest -q
```

---

## 7. Understanding Results

### Successful run
```
test_01_auth.py::TestHashPassword::test_returns_string PASSED    [ 10%]
test_01_auth.py::TestHashPassword::test_hash_is_not_plaintext PASSED [ 20%]
...
========================= 52 passed in 3.21s =========================
```

### Failed test
```
FAILED tests/test_04_crud_payments.py::TestDebtorLogic::test_partial_payment_child_is_debtor

AssertionError: Partially paying child should be a debtor!
assert 0 == 1
 +  where 0 = len([])
```

**Reading the output:**
- `FAILED` — test did not pass
- `AssertionError` — assert condition was False
- `assert 0 == 1` — expected 1 debtor, got 0
- This means the partial payment bug **has returned**!

### Output symbols
| Symbol | Meaning |
|--------|---------|
| `.` | PASSED |
| `F` | FAILED |
| `E` | ERROR — exception in fixture |
| `s` | SKIPPED |
| `x` | XFAIL — expected failure |

---

## 8. Student Exercises

### Level 1 (Beginner)
1. Run all tests with `pytest -v`
2. Run only smoke tests: `pytest -m smoke`
3. Find and read `test_partial_payment_child_is_debtor`
4. Explain in your own words: why is this a regression test?

### Level 2 (Intermediate)
5. Add a new test in `test_01_auth.py`: verify that the hash contains only lowercase letters
6. Add a test in `test_03_crud_children.py`: add 10 children and verify all were saved
7. In `test_04_crud_payments.py` add the parameter `(0.01, 3000.0, True)` to `test_debtor_threshold` — what happens?

### Level 3 (Advanced)
8. Write a new file `test_07_crud_expenses.py` with tests for expense functions
9. Add a test that verifies a deleted kindergarten doesn't appear in the list
10. Write a test that intentionally discovers a bug: what happens if you add a child without a name?

---

## Quick Reference Card

```bash
# Run everything
pytest

# Run with details
pytest -v

# Run specific file
pytest tests/test_01_auth.py

# Run specific test
pytest tests/test_01_auth.py::TestHashPassword::test_returns_string

# Run by marker
pytest -m smoke
pytest -m regression

# Stop on first failure  
pytest -x

# Filter by name
pytest -k "password"

# Show locals on failure
pytest -l
```

---

## Useful Links

- [pytest documentation](https://docs.pytest.org)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [SQLAlchemy testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)
