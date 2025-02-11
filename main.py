import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils import *

# Page configuration
st.set_page_config(page_title="Personal Budget Tracker", layout="wide")

# Title and description
st.title("Personal Budget Tracker")

# Budget Planning Section
st.header("Budget Planning")

# Total Budget Input
col1, col2 = st.columns([2, 1])
with col1:
    budgets_df, current_total = get_budget_data()
    total_budget = st.number_input("Enter your biweekly income", 
                                min_value=0.0, 
                                value=float(current_total),
                                step=100.0,
                                format="%.2f")

    if st.button("Update Total Budget"):
        success, message = update_total_budget(total_budget)
        st.write(message)
        if success:
            st.rerun()

# Budget Distribution Table
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Budget Distribution")
with col2:
    if st.button("Update All Budgets", type="primary"):
        all_updated = True
        for category in categories:
            amount = st.session_state.get(f"budget_{category}", 0.0)
            success, message = update_budget(category, amount)
            if not success:
                all_updated = False
                st.error(f"Error updating {category}: {message}")
        if all_updated:
            st.success("All budgets updated successfully!")
            st.rerun()

categories = load_categories()

total_allocated = 0.0
total_spent = 0.0
total_remaining = 0.0

# Create a table header
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    st.markdown("**Category**")
with col2:
    st.markdown("**Budget Amount**")
with col3:
    st.markdown("**Spent**")
with col4:
    st.markdown("**Remaining**")

# Display budget rows
for category in categories:
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        st.write(category)
    with col2:
        current_amount = budgets_df[budgets_df['category'] == category]['amount'].iloc[0] if not budgets_df.empty and category in budgets_df['category'].values else 0.0
        amount = st.number_input(f"Amount for {category}", 
                               min_value=0.0, 
                               value=float(current_amount),
                               step=10.0,
                               key=f"budget_{category}")
        total_allocated += amount
    with col3:
        spent = budgets_df[budgets_df['category'] == category]['spent'].iloc[0] if not budgets_df.empty and category in budgets_df['category'].values else 0.0
        st.write(f"${spent:.2f}")
        total_spent += spent
    with col4:
        remaining = budgets_df[budgets_df['category'] == category]['remaining'].iloc[0] if not budgets_df.empty and category in budgets_df['category'].values else 0.0
        st.write(f"${remaining:.2f}")
        total_remaining += remaining

# Display totals
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Budget", f"${total_budget:.2f}")
with col2:
    st.metric("Total Allocated", f"${total_allocated:.2f}")
with col3:
    st.metric("Total Spent", f"${total_spent:.2f}")
with col4:
    st.metric("Total Remaining", f"${total_remaining:.2f}")

st.markdown("---")

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["Add Expense", "Analytics", "History", "Settings"])

# Add Expense Tab
with tab1:
    st.header("Add New Expense")
    col1, col2 = st.columns(2)
    with col1:
        expense_date = st.date_input("Date", datetime.now())
        expense_category = st.selectbox("Category", categories)
    with col2:
        expense_amount = st.number_input("Amount", min_value=0.01, step=0.01)
        expense_description = st.text_input("Description")

    if st.button("Add Expense"):
        if expense_amount > 0:
            save_expense(expense_date, expense_category, expense_amount, expense_description)
            st.success("Expense added successfully!")
            st.rerun()
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

# History Tab
with tab3:
    st.header("Expense History")
    expenses_df = load_expenses()
    if not expenses_df.empty:
        expenses_df['date'] = pd.to_datetime(expenses_df['date']).dt.date
        st.dataframe(expenses_df.sort_values('date', ascending=False), use_container_width=True)
    else:
        st.write("No expenses recorded yet!")

# Settings Tab (including category management)
with tab4:
    st.header("Category Management")

    # Add new category
    with st.expander("Add New Category"):
        new_category = st.text_input("Add New Category")
        if st.button("Add Category"):
            if new_category.strip():
                success, message = add_category(new_category.strip())
                st.write(message)
                if success:
                    st.rerun()
            else:
                st.write("Please enter a category name")

    # Delete category (in danger zone)
    with st.expander("⚠️ Danger Zone - Delete Category"):
        st.warning("Warning: Deleting a category will remove all associated expenses and budget data!")
        category_to_delete = st.selectbox("Select category to delete", categories)
        if st.button("Delete Category", type="primary"):
            success, message = delete_category(category_to_delete)
            st.write(message)
            if success:
                st.rerun()

# Footer
st.markdown("---")
st.markdown("Personal Budget Tracker - Track your expenses with ease!")