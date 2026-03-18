from sqlalchemy.orm import Session
from models import Expense, Child, Attendance, Product, ProductTransaction
from database import SessionLocal
from sqlalchemy import func

# --- РАСХОДЫ (уже работают) ---
def get_all_expenses():
    db = SessionLocal()
    try:
        return db.query(Expense).all()
    finally:
        db.close()

def add_expense(date, category, amount, description, comment):
    db = SessionLocal()
    try:
        new_item = Expense(date=date, category=category, amount=amount, description=description, comment=comment)
        db.add(new_item)
        db.commit()
    finally:
        db.close()

def delete_expense(expense_id):
    db = SessionLocal()
    try:
        item = db.query(Expense).filter(Expense.id == expense_id).first()
        if item:
            db.delete(item)
            db.commit()
    finally:
        db.close()

# --- ДЕТИ (наводим порядок тут) ---
def get_all_children():
    db = SessionLocal()
    try:
        return db.query(Child).all()
    finally:
        db.close()

def add_child(first_name, last_name, birth_date, parent_name, parent_phone, enrollment_date, status):
    db = SessionLocal()
    try:
        new_child = Child(
            first_name=first_name, last_name=last_name, birth_date=birth_date,
            parent_name=parent_name, parent_phone=parent_phone, 
            enrollment_date=enrollment_date, status=status
        )
        db.add(new_child)
        db.commit()
    finally:
        db.close()

def update_child(child_id, first_name, last_name, birth_date, parent_name, parent_phone, enrollment_date, status):
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

def delete_child(child_id):
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == child_id).first()
        if child:
            db.delete(child)
            db.commit()
    finally:
        db.close()

# --- ПОСЕЩАЕМОСТЬ ---
def add_attendance(child_id, date, status):
    db = SessionLocal()
    try:
        existing = db.query(Attendance).filter(Attendance.child_id == child_id, Attendance.date == date).first()
        if existing:
            existing.status = status
        else:
            new_att = Attendance(child_id=child_id, date=date, status=status)
            db.add(new_att)
        db.commit()
    finally:
        db.close()

def get_attendance_by_date(selected_date):
    db = SessionLocal()
    try:
        return db.query(Attendance).filter(Attendance.date == selected_date).all()
    finally:
        db.close()

def get_all_attendance():
    db = SessionLocal()
    try:
        # Сложный запрос, чтобы сразу получить имена детей
        results = db.query(Attendance, Child).join(Child).all()
        data = []
        for att, child in results:
            data.append({
                "date": att.date,
                "first_name": child.first_name,
                "last_name": child.last_name,
                "status": att.status
            })
        return data
    finally:
        db.close()

# --- ПРОДУКТЫ ---
def get_all_products():
    db = SessionLocal()
    try:
        return db.query(Product).all()
    finally:
        db.close()

def add_product(name, unit, min_stock):
    db = SessionLocal()
    try:
        new_p = Product(name=name, unit=unit, min_stock=min_stock)
        db.add(new_p)
        db.commit()
    finally:
        db.close()

def get_product_inventory():
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        inventory = []
        for p in products:
            incomes = db.query(func.sum(ProductTransaction.quantity)).filter(
                ProductTransaction.product_id == p.id, ProductTransaction.transaction_type == 'income').scalar() or 0
            expenses = db.query(func.sum(ProductTransaction.quantity)).filter(
                ProductTransaction.product_id == p.id, ProductTransaction.transaction_type == 'expense').scalar() or 0
            inventory.append({
                "id": p.id, "name": p.name, "unit": p.unit,
                "current_stock": incomes - expenses, "min_stock": p.min_stock
            })
        return inventory
    finally:
        db.close()
        
def add_product_income(product_id, date, quantity):
    db = SessionLocal()
    try:
        new_trans = ProductTransaction(product_id=product_id, date=date, quantity=quantity, transaction_type='income')
        db.add(new_trans)
        db.commit()
    finally:
        db.close()

def add_product_expense(product_id, date, quantity):
    db = SessionLocal()
    try:
        new_trans = ProductTransaction(product_id=product_id, date=date, quantity=quantity, transaction_type='expense')
        db.add(new_trans)
        db.commit()
    finally:
        db.close()

def delete_product(product_id):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            # Сначала удаляем транзакции продукта, потом сам продукт
            db.query(ProductTransaction).filter(ProductTransaction.product_id == product_id).delete()
            db.delete(product)
            db.commit()
    finally:
        db.close()
