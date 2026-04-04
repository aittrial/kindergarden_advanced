import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Берём URL из переменных окружения (Railway/Streamlit Cloud)
DATABASE_URL = os.environ.get("DATABASE_URL")

# Если нет в env — пробуем st.secrets (Streamlit Cloud)
if not DATABASE_URL:
    try:
        import streamlit as st
        DATABASE_URL = st.secrets.get("DATABASE_URL")
    except Exception:
        pass

# Логика: если переменной нет (например, локально), используем SQLite
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./local_storage.db"
else:
    # Исправляем формат ссылки для SQLAlchemy
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
