from sqlalchemy.orm import Session
from models import Expense
from database import SessionLocal

def add_expense(date, category, description, amount, comment):
    db = SessionLocal()
    try:
        new_expense = Expense(
            date=date,
            category=category,
            description=description,
            amount=amount,
            comment=comment
        )
        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)
        return new_expense
    finally:
        db.close()

# Остальные функции (get_all_expenses, delete_expense) можно оставить как есть
def get_all_expenses():
    db = SessionLocal()
    try:
        return db.query(Expense).all()
    finally:
        db.close()

def delete_expense(expense_id):
    db = SessionLocal()
    try:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if expense:
            db.delete(expense)
            db.commit()
        return True
    finally:
        db.close()
