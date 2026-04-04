from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'superadmin' or 'admin'
    language = Column(String, default="ru", server_default="ru")
    currency = Column(String, default="ILS", server_default="ILS")


class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    category = Column(String)
    amount = Column(Float)
    description = Column(String)
    comment = Column(Text)

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

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    date = Column(Date)
    status = Column(String) # присутствовал, отсутствовал, болел

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    unit = Column(String)
    min_stock = Column(Float, default=1.0)

class ProductTransaction(Base):
    __tablename__ = "product_transactions"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    date = Column(Date)
    quantity = Column(Float)
    transaction_type = Column(String) # income / expense
