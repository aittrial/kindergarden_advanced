from models import (Expense, Child, Attendance, Product, ProductTransaction,
                    User, Payment, Kindergarten)
from database import SessionLocal
from sqlalchemy import func


# ── KINDERGARTENS ────────────────────────────────────────────────────────────

def get_all_kindergartens():
    db = SessionLocal()
    try:
        return db.query(Kindergarten).all()
    finally:
        db.close()


def get_kindergarten_by_id(kg_id):
    db = SessionLocal()
    try:
        return db.query(Kindergarten).filter(Kindergarten.id == kg_id).first()
    finally:
        db.close()


def add_kindergarten(name, address, phone, logo_url):
    db = SessionLocal()
    try:
        kg = Kindergarten(name=name, address=address, phone=phone, logo_url=logo_url)
        db.add(kg)
        db.commit()
        db.refresh(kg)
        return kg.id
    finally:
        db.close()


def update_kindergarten(kg_id, name, address, phone, logo_url):
    db = SessionLocal()
    try:
        kg = db.query(Kindergarten).filter(Kindergarten.id == kg_id).first()
        if kg:
            kg.name = name
            kg.address = address
            kg.phone = phone
            kg.logo_url = logo_url
            db.commit()
    finally:
        db.close()


def delete_kindergarten(kg_id):
    db = SessionLocal()
    try:
        # cascade: delete all linked data
        children = db.query(Child).filter(Child.kindergarten_id == kg_id).all()
        for child in children:
            db.query(Attendance).filter(Attendance.child_id == child.id).delete()
            db.query(Payment).filter(Payment.child_id == child.id).delete()
        db.query(Child).filter(Child.kindergarten_id == kg_id).delete()

        products = db.query(Product).filter(Product.kindergarten_id == kg_id).all()
        for p in products:
            db.query(ProductTransaction).filter(ProductTransaction.product_id == p.id).delete()
        db.query(Product).filter(Product.kindergarten_id == kg_id).delete()

        db.query(Expense).filter(Expense.kindergarten_id == kg_id).delete()
        db.query(User).filter(User.kindergarten_id == kg_id).update({"kindergarten_id": None})
        db.query(Kindergarten).filter(Kindergarten.id == kg_id).delete()
        db.commit()
    finally:
        db.close()


# ── USERS ────────────────────────────────────────────────────────────────────

def get_user_by_email(email: str):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()


def create_user(email: str, password_hash: str, role: str, kindergarten_id=None):
    db = SessionLocal()
    try:
        user = User(email=email, password_hash=password_hash, role=role,
                    kindergarten_id=kindergarten_id)
        db.add(user)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()


def superadmin_exists():
    db = SessionLocal()
    try:
        return db.query(User).filter(User.role == 'superadmin').first() is not None
    finally:
        db.close()


def get_all_admins(kindergarten_id=None):
    db = SessionLocal()
    try:
        q = db.query(User).filter(User.role == 'admin')
        if kindergarten_id is not None:
            q = q.filter(User.kindergarten_id == kindergarten_id)
        return q.all()
    finally:
        db.close()


def delete_user_by_email(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False
    finally:
        db.close()


def update_user_preferences(email: str, language: str, currency: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.language = language
            user.currency = currency
            db.commit()
    finally:
        db.close()


# ── CHILDREN ─────────────────────────────────────────────────────────────────

def get_all_children(kindergarten_id):
    db = SessionLocal()
    try:
        return db.query(Child).filter(Child.kindergarten_id == kindergarten_id).all()
    finally:
        db.close()


def add_child(kindergarten_id, first_name, last_name, birth_date,
              parent_name, parent_phone, enrollment_date, status, group="младшая"):
    db = SessionLocal()
    try:
        child = Child(kindergarten_id=kindergarten_id, first_name=first_name,
                      last_name=last_name, birth_date=birth_date,
                      parent_name=parent_name, parent_phone=parent_phone,
                      enrollment_date=enrollment_date, status=status, group=group)
        db.add(child)
        db.commit()
    finally:
        db.close()


def update_child(child_id, first_name, last_name, birth_date,
                 parent_name, parent_phone, enrollment_date, status):
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == child_id).first()
        if child:
            child.first_name = first_name
            child.last_name = last_name
            child.birth_date = birth_date
            child.parent_name = parent_name
            child.parent_phone = parent_phone
            child.enrollment_date = enrollment_date
            child.status = status
            db.commit()
    finally:
        db.close()


def update_child_group(child_id, group):
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == child_id).first()
        if child:
            child.group = group
            db.commit()
    finally:
        db.close()


def update_child_fee(child_id, monthly_fee):
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == child_id).first()
        if child:
            child.monthly_fee = monthly_fee
            db.commit()
    finally:
        db.close()


def delete_child(child_id):
    db = SessionLocal()
    try:
        db.query(Attendance).filter(Attendance.child_id == child_id).delete()
        db.query(Payment).filter(Payment.child_id == child_id).delete()
        child = db.query(Child).filter(Child.id == child_id).first()
        if child:
            db.delete(child)
            db.commit()
    finally:
        db.close()


# ── ATTENDANCE ────────────────────────────────────────────────────────────────

def add_attendance(child_id, date, status):
    db = SessionLocal()
    try:
        existing = db.query(Attendance).filter(
            Attendance.child_id == child_id, Attendance.date == date).first()
        if existing:
            existing.status = status
        else:
            db.add(Attendance(child_id=child_id, date=date, status=status))
        db.commit()
    finally:
        db.close()


def get_attendance_by_date(kindergarten_id, selected_date):
    db = SessionLocal()
    try:
        results = db.query(Attendance).join(Child).filter(
            Child.kindergarten_id == kindergarten_id,
            Attendance.date == selected_date
        ).all()
        return results
    finally:
        db.close()


def get_all_attendance(kindergarten_id):
    db = SessionLocal()
    try:
        results = db.query(Attendance, Child).join(Child).filter(
            Child.kindergarten_id == kindergarten_id).all()
        return [{"date": a.date, "child_id": a.child_id,
                 "first_name": c.first_name, "last_name": c.last_name,
                 "group": c.group, "status": a.status}
                for a, c in results]
    finally:
        db.close()


# ── PRODUCTS ──────────────────────────────────────────────────────────────────

def get_all_products(kindergarten_id):
    db = SessionLocal()
    try:
        return db.query(Product).filter(Product.kindergarten_id == kindergarten_id).all()
    finally:
        db.close()


def add_product(kindergarten_id, name, unit, min_stock):
    db = SessionLocal()
    try:
        db.add(Product(kindergarten_id=kindergarten_id, name=name,
                       unit=unit, min_stock=min_stock))
        db.commit()
    finally:
        db.close()


def get_product_inventory(kindergarten_id):
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.kindergarten_id == kindergarten_id).all()
        inventory = []
        for p in products:
            inc = db.query(func.sum(ProductTransaction.quantity)).filter(
                ProductTransaction.product_id == p.id,
                ProductTransaction.transaction_type == 'income').scalar() or 0
            exp = db.query(func.sum(ProductTransaction.quantity)).filter(
                ProductTransaction.product_id == p.id,
                ProductTransaction.transaction_type == 'expense').scalar() or 0
            inventory.append({"id": p.id, "name": p.name, "unit": p.unit,
                               "current_stock": inc - exp, "min_stock": p.min_stock})
        return inventory
    finally:
        db.close()


def add_product_income(product_id, date, quantity):
    db = SessionLocal()
    try:
        db.add(ProductTransaction(product_id=product_id, date=date,
                                  quantity=quantity, transaction_type='income'))
        db.commit()
    finally:
        db.close()


def add_product_expense(product_id, date, quantity):
    db = SessionLocal()
    try:
        db.add(ProductTransaction(product_id=product_id, date=date,
                                  quantity=quantity, transaction_type='expense'))
        db.commit()
    finally:
        db.close()


def delete_product(product_id):
    db = SessionLocal()
    try:
        db.query(ProductTransaction).filter(
            ProductTransaction.product_id == product_id).delete()
        p = db.query(Product).filter(Product.id == product_id).first()
        if p:
            db.delete(p)
            db.commit()
    finally:
        db.close()


# ── EXPENSES ──────────────────────────────────────────────────────────────────

def get_all_expenses(kindergarten_id):
    db = SessionLocal()
    try:
        return db.query(Expense).filter(
            Expense.kindergarten_id == kindergarten_id).all()
    finally:
        db.close()


def add_expense(kindergarten_id, date, category, amount, description, comment):
    db = SessionLocal()
    try:
        db.add(Expense(kindergarten_id=kindergarten_id, date=date,
                       category=category, amount=amount,
                       description=description, comment=comment))
        db.commit()
    finally:
        db.close()


def delete_expense(expense_id):
    db = SessionLocal()
    try:
        e = db.query(Expense).filter(Expense.id == expense_id).first()
        if e:
            db.delete(e)
            db.commit()
    finally:
        db.close()


# ── PAYMENTS ──────────────────────────────────────────────────────────────────

def get_all_payments(kindergarten_id):
    db = SessionLocal()
    try:
        results = db.query(Payment, Child).join(Child).filter(
            Child.kindergarten_id == kindergarten_id).all()
        return [{"id": p.id, "child_id": p.child_id,
                 "child_name": f"{c.last_name} {c.first_name}",
                 "year": p.year, "month": p.month, "amount": p.amount,
                 "paid_date": p.paid_date, "comment": p.comment}
                for p, c in results]
    finally:
        db.close()


def add_payment(child_id, year, month, amount, paid_date, comment):
    db = SessionLocal()
    try:
        db.add(Payment(child_id=child_id, year=year, month=month,
                       amount=amount, paid_date=paid_date, comment=comment))
        db.commit()
    finally:
        db.close()


def delete_payment(payment_id):
    db = SessionLocal()
    try:
        p = db.query(Payment).filter(Payment.id == payment_id).first()
        if p:
            db.delete(p)
            db.commit()
    finally:
        db.close()


def get_debtors(kindergarten_id, current_year, current_month):
    db = SessionLocal()
    try:
        active = db.query(Child).filter(
            Child.kindergarten_id == kindergarten_id,
            Child.status == "активный"
        ).all()
        debtors = []
        for child in active:
            if not child.monthly_fee or child.monthly_fee <= 0:
                continue
            total_paid = db.query(func.sum(Payment.amount)).filter(
                Payment.child_id == child.id,
                Payment.year == current_year,
                Payment.month == current_month
            ).scalar() or 0
            if total_paid < child.monthly_fee:
                child._debt_amount = child.monthly_fee - total_paid
                debtors.append(child)
        return debtors
    finally:
        db.close()
