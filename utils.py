import pandas as pd
from datetime import datetime
from database import SessionLocal, Category, Expense
from sqlalchemy import func

def load_categories():
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        return [cat.category for cat in categories]
    finally:
        db.close()

def load_expenses():
    db = SessionLocal()
    try:
        expenses = db.query(Expense).all()
        return pd.DataFrame([{
            'date': expense.date,
            'category': expense.category.category,
            'amount': expense.amount,
            'description': expense.description
        } for expense in expenses])
    finally:
        db.close()

def save_expense(date, category, amount, description):
    db = SessionLocal()
    try:
        category_obj = db.query(Category).filter(Category.category == category).first()
        new_expense = Expense(
            date=date,
            category_id=category_obj.id,
            amount=amount,
            description=description
        )
        db.add(new_expense)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def add_category(category):
    db = SessionLocal()
    try:
        # Check category limit
        if db.query(Category).count() >= 20:
            return False, "Maximum number of categories (20) reached"

        # Check if category exists
        if db.query(Category).filter(Category.category == category).first():
            return False, "Category already exists"

        new_category = Category(category=category)
        db.add(new_category)
        db.commit()
        return True, "Category added successfully"
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()

def delete_category(category):
    db = SessionLocal()
    try:
        # Check if it's the last category
        if db.query(Category).count() <= 1:
            return False, "Cannot delete the last category"

        category_obj = db.query(Category).filter(Category.category == category).first()

        # Check if category has expenses
        if db.query(Expense).filter(Expense.category_id == category_obj.id).count() > 0:
            return False, "Cannot delete category with existing expenses"

        db.delete(category_obj)
        db.commit()
        return True, "Category deleted successfully"
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()

def get_monthly_summary():
    db = SessionLocal()
    try:
        expenses = load_expenses()
        if len(expenses) == 0:
            return pd.DataFrame()

        expenses['date'] = pd.to_datetime(expenses['date'])
        monthly = expenses.groupby([expenses['date'].dt.strftime('%Y-%m'), 'category'])['amount'].sum().reset_index()
        return monthly
    finally:
        db.close()

def get_category_summary():
    db = SessionLocal()
    try:
        expenses = load_expenses()
        if len(expenses) == 0:
            return pd.DataFrame()

        return expenses.groupby('category')['amount'].sum().reset_index()
    finally:
        db.close()