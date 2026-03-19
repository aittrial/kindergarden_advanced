from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, Float
from sqlalchemy.orm import declarative_base, relationship
import os
import sys

# Добавляем путь, чтобы Python видел database.py, если он не в той же папке
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import Base

class Child(Base):
    __tablename__ = "children"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_date = Column(Date)
    parent_name = Column(String)
    parent_phone = Column(String)
    enrollment_date = Column(Date)
    status = Column(String, default="активный")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    unit = Column(String)
    min_stock = Column(Float, default=1.0)
    
    transactions = relationship("ProductTransaction", back_populates="product")

class ProductTransaction(Base):
    __tablename__ = "product_transactions"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    date = Column(Date)
    quantity = Column(Float)
    transaction_type = Column(String) # "income" or "expense"
    
    product = relationship("Product", back_populates="transactions")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    category = Column(String)
    amount = Column(Float)
    description = Column(String)
