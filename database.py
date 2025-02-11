from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Create database engine with proper SSL configuration
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=3600,   # Recycle connections every hour
    connect_args={
        "sslmode": "require"  # Force SSL connection
    }
)

# Configure session with proper handling
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, unique=True, nullable=False)
    expenses = relationship("Expense", back_populates="category", cascade="all, delete-orphan")
    budget = relationship("Budget", back_populates="category", uselist=False, cascade="all, delete-orphan")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, default=datetime.now().date())
    amount = Column(Float, nullable=False)
    description = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    category = relationship("Category", back_populates="expenses")

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), unique=True, nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    category = relationship("Category", back_populates="budget")

class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    total_budget = Column(Float, nullable=False, default=0.0)

# Database session context manager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize default categories if they don't exist
def init_categories():
    db = SessionLocal()
    default_categories = ["Food & Groceries", "Dining Out", "Credit Card Debt", "Emergency Fund", "Miscellaneous", "Fixed Bills"]

    try:
        existing_categories = db.query(Category).all()
        if not existing_categories:
            for category_name in default_categories:
                category = Category(category=category_name)
                db.add(category)
            db.commit()

            # Initialize settings with default total budget
            settings = Settings(total_budget=0.0)
            db.add(settings)
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error initializing categories: {e}")
    finally:
        db.close()

# Call initialization
init_categories()