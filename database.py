from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, unique=True, nullable=False)
    expenses = relationship("Expense", back_populates="category")

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, default=datetime.now().date())
    amount = Column(Float, nullable=False)
    description = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="expenses")

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize default categories if they don't exist
def init_categories():
    db = SessionLocal()
    default_categories = ["Groceries", "Transportation", "Entertainment", "Bills", "Shopping"]
    
    try:
        existing_categories = db.query(Category).all()
        if not existing_categories:
            for category_name in default_categories:
                category = Category(category=category_name)
                db.add(category)
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error initializing categories: {e}")
    finally:
        db.close()

# Call initialization
init_categories()
