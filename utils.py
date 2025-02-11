import pandas as pd
from datetime import datetime
import os

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Initialize CSV files if they don't exist
def init_files():
    if not os.path.exists('data/categories.csv'):
        default_categories = pd.DataFrame({
            'category': ['Groceries', 'Transportation', 'Entertainment', 'Bills', 'Shopping']
        })
        default_categories.to_csv('data/categories.csv', index=False)
    
    if not os.path.exists('data/expenses.csv'):
        expenses_df = pd.DataFrame(columns=['date', 'category', 'amount', 'description'])
        expenses_df.to_csv('data/expenses.csv', index=False)

def load_categories():
    return pd.read_csv('data/categories.csv')['category'].tolist()

def load_expenses():
    return pd.read_csv('data/expenses.csv')

def save_expense(date, category, amount, description):
    expenses_df = load_expenses()
    new_expense = pd.DataFrame({
        'date': [date],
        'category': [category],
        'amount': [amount],
        'description': [description]
    })
    expenses_df = pd.concat([expenses_df, new_expense], ignore_index=True)
    expenses_df.to_csv('data/expenses.csv', index=False)

def add_category(category):
    categories = load_categories()
    if len(categories) >= 20:
        return False, "Maximum number of categories (20) reached"
    if category in categories:
        return False, "Category already exists"
    
    categories_df = pd.read_csv('data/categories.csv')
    new_category = pd.DataFrame({'category': [category]})
    categories_df = pd.concat([categories_df, new_category], ignore_index=True)
    categories_df.to_csv('data/categories.csv', index=False)
    return True, "Category added successfully"

def delete_category(category):
    categories_df = pd.read_csv('data/categories.csv')
    if len(categories_df) <= 1:
        return False, "Cannot delete the last category"
    
    expenses_df = load_expenses()
    if len(expenses_df[expenses_df['category'] == category]) > 0:
        return False, "Cannot delete category with existing expenses"
    
    categories_df = categories_df[categories_df['category'] != category]
    categories_df.to_csv('data/categories.csv', index=False)
    return True, "Category deleted successfully"

def get_monthly_summary():
    expenses_df = load_expenses()
    if len(expenses_df) == 0:
        return pd.DataFrame()
    
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    monthly = expenses_df.groupby([expenses_df['date'].dt.strftime('%Y-%m'), 'category'])['amount'].sum().reset_index()
    return monthly

def get_category_summary():
    expenses_df = load_expenses()
    if len(expenses_df) == 0:
        return pd.DataFrame()
    
    return expenses_df.groupby('category')['amount'].sum().reset_index()
