import pandas as pd
from datetime import datetime
from database import SessionLocal, Category, Expense, Budget, Settings
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

def get_budget_data():
    db = SessionLocal()
    try:
        budgets = db.query(Budget, Category).join(Category).all()
        settings = db.query(Settings).first()

        if not settings:
            settings = Settings(total_budget=0.0)
            db.add(settings)
            db.commit()

        return pd.DataFrame([{
            'category': cat.category,
            'amount': budget.amount,
            'notes': budget.notes
        } for budget, cat in budgets]), settings.total_budget
    finally:
        db.close()

def update_budget(category, amount, notes=""):
    db = SessionLocal()
    try:
        category_obj = db.query(Category).filter(Category.category == category).first()
        if not category_obj:
            return False, "Category not found"

        budget = db.query(Budget).filter(Budget.category_id == category_obj.id).first()
        if budget:
            budget.amount = amount
            budget.notes = notes
        else:
            budget = Budget(category_id=category_obj.id, amount=amount, notes=notes)
            db.add(budget)

        db.commit()
        return True, "Budget updated successfully"
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()

def update_total_budget(amount):
    db = SessionLocal()
    try:
        settings = db.query(Settings).first()
        if not settings:
            settings = Settings(total_budget=amount)
            db.add(settings)
        else:
            settings.total_budget = amount
        db.commit()
        return True, "Total budget updated successfully"
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()