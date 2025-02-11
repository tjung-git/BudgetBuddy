import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils import *

# Initialize the application (Presumed to be handled by the database now)
# init_files()

# Page configuration
st.set_page_config(page_title="Personal Budget Tracker", layout="wide")

# Title and description
st.title("Personal Budget Tracker")
st.markdown("---")

# Sidebar for adding categories
with st.sidebar:
    st.header("Category Management")
    new_category = st.text_input("Add New Category")
    if st.button("Add Category"):
        if new_category.strip():
            success, message = add_category(new_category.strip())
            st.write(message)
        else:
            st.write("Please enter a category name")

    st.markdown("---")
    st.header("Delete Category")
    category_to_delete = st.selectbox("Select category to delete", load_categories())
    if st.button("Delete Category"):
        success, message = delete_category(category_to_delete)
        st.write(message)

# Main content
tab1, tab2, tab3 = st.tabs(["Add Expense", "Analytics", "History"])

# Add Expense Tab
with tab1:
    st.header("Add New Expense")

    col1, col2 = st.columns(2)

    with col1:
        expense_date = st.date_input("Date", datetime.now())
        expense_category = st.selectbox("Category", load_categories())

    with col2:
        expense_amount = st.number_input("Amount", min_value=0.01, step=0.01)
        expense_description = st.text_input("Description")

    if st.button("Add Expense"):
        if expense_amount > 0:
            save_expense(expense_date, expense_category, expense_amount, expense_description)
            st.success("Expense added successfully!")
        else:
            st.error("Please enter a valid amount")

# Analytics Tab
with tab2:
    st.header("Expense Analytics")

    # Category breakdown
    category_summary = get_category_summary()
    if not category_summary.empty:
        fig1 = px.pie(category_summary, values='amount', names='category', 
                      title='Spending by Category')
        st.plotly_chart(fig1)

    # Monthly trends
    monthly_summary = get_monthly_summary()
    if not monthly_summary.empty:
        fig2 = px.bar(monthly_summary, x='date', y='amount', color='category',
                      title='Monthly Spending Trends')
        st.plotly_chart(fig2)

    # Basic statistics
    expenses_df = load_expenses()
    if not expenses_df.empty:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Expenses", f"${expenses_df['amount'].sum():.2f}")

        with col2:
            st.metric("Average Expense", f"${expenses_df['amount'].mean():.2f}")

        with col3:
            st.metric("Number of Transactions", len(expenses_df))

# History Tab
with tab3:
    st.header("Expense History")
    expenses_df = load_expenses()
    if not expenses_df.empty:
        expenses_df['date'] = pd.to_datetime(expenses_df['date']).dt.date
        st.dataframe(expenses_df.sort_values('date', ascending=False), use_container_width=True)
    else:
        st.write("No expenses recorded yet!")

# Footer
st.markdown("---")
st.markdown("Personal Budget Tracker - Track your expenses with ease!")