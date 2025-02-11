import pandas as pd
from datetime import datetime
from database import SessionLocal, Category, Expense, Budget, Settings
from sqlalchemy import func
from contextlib import contextmanager

@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def load_categories():
    with get_db_session() as db:
        categories = db.query(Category).all()
        return [cat.category for cat in categories]

def load_expenses():
    with get_db_session() as db:
        expenses = db.query(Expense).all()
        return pd.DataFrame([{
            'expense_id': expense.id,  # Add expense ID to the DataFrame
            'date': expense.date,
            'category': expense.category.category,
            'amount': expense.amount,
            'description': expense.description
        } for expense in expenses])

def delete_expense(expense_id):
    with get_db_session() as db:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if expense:
            db.delete(expense)
            return True, "Expense deleted successfully"
        return False, "Expense not found"

def save_expense(date, category, amount, description):
    with get_db_session() as db:
        category_obj = db.query(Category).filter(Category.category == category).first()
        new_expense = Expense(
            date=date,
            category_id=category_obj.id,
            amount=amount,
            description=description
        )
        db.add(new_expense)

def add_category(category):
    with get_db_session() as db:
        # Check category limit
        if db.query(Category).count() >= 20:
            return False, "Maximum number of categories (20) reached"

        # Check if category exists
        if db.query(Category).filter(Category.category == category).first():
            return False, "Category already exists"

        new_category = Category(category=category)
        db.add(new_category)
        return True, "Category added successfully"

def delete_category(category):
    with get_db_session() as db:
        # Check if it's the last category
        if db.query(Category).count() <= 1:
            return False, "Cannot delete the last category"

        category_obj = db.query(Category).filter(Category.category == category).first()
        if not category_obj:
            return False, "Category not found"

        db.delete(category_obj)
        return True, "Category deleted successfully"

def calculate_category_expenses():
    expenses_df = load_expenses()
    if len(expenses_df) == 0:
        return pd.DataFrame(columns=['category', 'spent'])
    return expenses_df.groupby('category')['amount'].sum().reset_index().rename(columns={'amount': 'spent'})

def get_budget_data():
    with get_db_session() as db:
        budgets = db.query(Budget, Category).join(Category).all()
        settings = db.query(Settings).first()

        if not settings:
            settings = Settings(total_budget=0.0)
            db.add(settings)

        # Get expenses by category
        expenses_by_category = calculate_category_expenses()

        budget_data = []
        for budget, cat in budgets:
            spent = expenses_by_category[
                expenses_by_category['category'] == cat.category
            ]['spent'].iloc[0] if not expenses_by_category.empty and cat.category in expenses_by_category['category'].values else 0.0

            remaining = budget.amount - spent

            budget_data.append({
                'category': cat.category,
                'amount': budget.amount,
                'spent': spent,
                'remaining': remaining
            })

        return pd.DataFrame(budget_data), settings.total_budget

def update_budget(category, amount):
    with get_db_session() as db:
        category_obj = db.query(Category).filter(Category.category == category).first()
        if not category_obj:
            return False, "Category not found"

        budget = db.query(Budget).filter(Budget.category_id == category_obj.id).first()
        if budget:
            budget.amount = amount
        else:
            budget = Budget(category_id=category_obj.id, amount=amount)
            db.add(budget)

        return True, "Budget updated successfully"

def update_total_budget(amount):
    with get_db_session() as db:
        settings = db.query(Settings).first()
        if not settings:
            settings = Settings(total_budget=amount)
            db.add(settings)
        else:
            settings.total_budget = amount
        return True, "Total budget updated successfully"

def get_monthly_summary():
    with get_db_session() as db:
        expenses = load_expenses()
        if len(expenses) == 0:
            return pd.DataFrame()

        expenses['date'] = pd.to_datetime(expenses['date'])
        monthly = expenses.groupby([expenses['date'].dt.strftime('%Y-%m'), 'category'])['amount'].sum().reset_index()
        return monthly

def get_category_summary():
    with get_db_session() as db:
        expenses = load_expenses()
        if len(expenses) == 0:
            return pd.DataFrame()

        return expenses.groupby('category')['amount'].sum().reset_index()