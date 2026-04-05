"""
Run once to populate the database with 3 kindergartens and sample data.
Keeps existing superadmin, clears everything else.
"""
import os
import sys
import random
from pathlib import Path
from datetime import date, timedelta

sys.path.append(str(Path(__file__).resolve().parent))

from database import engine, Base, SessionLocal
import models  # noqa: F401 — registers all models
from models import (Kindergarten, User, Child, Attendance,
                    Product, ProductTransaction, Expense, Payment)
from auth import hash_password

# ── 1. DROP & RECREATE ALL TABLES ────────────────────────────────────────────
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── 2. RESTORE SUPERADMIN ────────────────────────────────────────────────────
import os
sa_email = os.environ.get("SEED_EMAIL", "admin@kms.com")
sa_password = os.environ.get("SEED_PASSWORD", "admin123")

superadmin = User(
    email=sa_email,
    password_hash=hash_password(sa_password),
    role="superadmin",
    language="ru",
    currency="ILS"
)
db.add(superadmin)
db.commit()
print(f"✓ Superadmin created: {sa_email} / {sa_password}")

# ── 3. THREE KINDERGARTENS ────────────────────────────────────────────────────
kgs_data = [
    {"name": "Солнышко",   "address": "ул. Цветочная, 5, Тель-Авив",    "phone": "+972-3-1111111"},
    {"name": "Радуга",     "address": "ул. Морская, 12, Хайфа",          "phone": "+972-4-2222222"},
    {"name": "Звёздочка",  "address": "ул. Иерусалимская, 8, Ришон-ле-Цион", "phone": "+972-3-3333333"},
]
kgs = []
for d in kgs_data:
    kg = Kindergarten(name=d["name"], address=d["address"], phone=d["phone"], logo_url="")
    db.add(kg)
db.commit()
kgs = db.query(Kindergarten).all()
print(f"✓ Kindergartens created: {[k.name for k in kgs]}")

# ── 4. SAMPLE DATA PER KINDERGARTEN ──────────────────────────────────────────
children_data = [
    # (first_name, last_name, birth_year, parent_name, phone, group, fee)
    ("Миша",    "Иванов",    2020, "Иван Иванов",      "+972-50-1111111", "младшая", 3000),
    ("Соня",    "Коэн",      2020, "Давид Коэн",       "+972-50-2222222", "младшая", 3000),
    ("Арик",    "Леви",      2019, "Рон Леви",         "+972-50-3333333", "средняя", 3200),
    ("Яэль",    "Кац",       2019, "Шира Кац",         "+972-50-4444444", "средняя", 3200),
    ("Даниэль", "Шапиро",   2018, "Ури Шапиро",       "+972-50-5555555", "старшая", 3500),
    ("Ноа",     "Даган",     2018, "Лиат Даган",       "+972-50-6666666", "старшая", 3500),
    ("Том",     "Азулай",    2020, "Ями Азулай",       "+972-50-7777777", "младшая", 3000),
    ("Майя",    "Розен",     2019, "Эран Розен",       "+972-50-8888888", "средняя", 3200),
]

products_data = [
    ("Молоко",    "литры",  10.0),
    ("Хлеб",     "штуки",  20.0),
    ("Гречка",   "кг",      5.0),
    ("Масло",    "кг",      3.0),
    ("Куриное филе", "кг",  8.0),
]

expense_categories = ["Еда", "Транспорт", "Жилье", "Связь", "Другое"]

today = date.today()

for kg in kgs:
    print(f"\n  Filling '{kg.name}'...")

    # Children
    children = []
    for i, cd in enumerate(children_data):
        fname, lname, byear, pname, pphone, group, fee = cd
        birth = date(byear, random.randint(1, 12), random.randint(1, 28))
        child = Child(
            kindergarten_id=kg.id,
            first_name=fname, last_name=lname,
            birth_date=birth, parent_name=pname, parent_phone=pphone,
            enrollment_date=date(2024, 9, 1), status="активный",
            group=group, monthly_fee=fee
        )
        db.add(child)
    db.commit()
    children = db.query(Child).filter(Child.kindergarten_id == kg.id).all()
    print(f"    ✓ {len(children)} children")

    # Attendance — last 10 weekdays
    statuses = ["присутствовал", "присутствовал", "присутствовал", "отсутствовал", "болел"]
    days_added = 0
    d = today
    while days_added < 10:
        if d.weekday() < 5:  # Mon-Fri
            for child in children:
                att = Attendance(
                    child_id=child.id, date=d,
                    status=random.choice(statuses)
                )
                db.add(att)
            days_added += 1
        d -= timedelta(days=1)
    db.commit()
    print(f"    ✓ Attendance for 10 days")

    # Products
    products = []
    for pname, unit, min_stock in products_data:
        p = Product(kindergarten_id=kg.id, name=pname, unit=unit, min_stock=min_stock)
        db.add(p)
    db.commit()
    products = db.query(Product).filter(Product.kindergarten_id == kg.id).all()

    for p in products:
        # income
        db.add(ProductTransaction(
            product_id=p.id, date=today - timedelta(days=7),
            quantity=random.uniform(15, 30), transaction_type="income"
        ))
        # expense (some below min_stock intentionally)
        db.add(ProductTransaction(
            product_id=p.id, date=today - timedelta(days=2),
            quantity=random.uniform(5, 20), transaction_type="expense"
        ))
    db.commit()
    print(f"    ✓ {len(products)} products with transactions")

    # Expenses — last 2 months
    for month_offset in [0, 1]:
        exp_month = today.month - month_offset
        exp_year = today.year
        if exp_month <= 0:
            exp_month += 12
            exp_year -= 1
        for _ in range(5):
            db.add(Expense(
                kindergarten_id=kg.id,
                date=date(exp_year, exp_month, random.randint(1, 20)),
                category=random.choice(expense_categories),
                amount=round(random.uniform(200, 2000), 2),
                description="Тестовый расход",
                comment=""
            ))
    db.commit()
    print(f"    ✓ 10 expenses")

    # Payments — current month, half the children paid fully, one paid partially
    for i, child in enumerate(children):
        if i < 4:  # fully paid
            db.add(Payment(
                child_id=child.id, year=today.year, month=today.month,
                amount=child.monthly_fee,
                paid_date=today - timedelta(days=random.randint(1, 10)),
                comment="Оплата за месяц"
            ))
        elif i == 4:  # partial payment
            db.add(Payment(
                child_id=child.id, year=today.year, month=today.month,
                amount=child.monthly_fee / 2,
                paid_date=today - timedelta(days=3),
                comment="Частичная оплата"
            ))
        # i >= 5: no payment — will appear as debtors
    db.commit()
    print(f"    ✓ Payments: 4 full, 1 partial, 3 debtors")

db.close()
print("\n✅ Database seeded successfully!")
print("   Login: admin@kms.com / admin123")
