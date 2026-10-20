
import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px


FILE_NAME = "expenses.csv"
BUDGET_FILE = "budget.txt"

if not os.path.exists(BUDGET_FILE):
    with open(BUDGET_FILE, "w") as file:
        file.write("5000")

with open(BUDGET_FILE, "r") as file:
    saved_budget = float(file.read())

if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(
        columns=["Date", "Expense Name", "Amount", "Category"]
    )
    df.to_csv(FILE_NAME, index=False)

df = pd.read_csv(FILE_NAME)

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])
    df["Amount"] = pd.to_numeric(df["Amount"])

today = date.today()

if not df.empty:
    monthly_expenses = df[
        (df["Date"].dt.month == today.month) &
        (df["Date"].dt.year == today.year)
    ]
else:
    monthly_expenses = df

total_spending = monthly_expenses["Amount"].sum()
total_transactions = len(monthly_expenses)
daily_average = total_spending / today.day

st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# Sidebar
st.sidebar.title("💰 SpendFree")
st.sidebar.write("Personal Expense Tracker")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "History", "Settings"]
)


# Dashboard
if page == "Dashboard":

    st.title("💰 Personal Expense Tracker")

    st.caption(
        "Track your daily expenses, monitor your monthly budget, "
        "and analyze your spending habits."
    )

    st.divider()

   
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.metric(
                "💳 Spent This Month",
                f"₹{total_spending:,.2f}"
            )

    with col2:
        with st.container(border=True):
            st.metric(
                "🧾 Transactions",
                total_transactions
            )

    with col3:
        with st.container(border=True):
            st.metric(
                "📈 Daily Average",
                f"₹{daily_average:,.2f}"
            )


    st.divider()

    # Monthly Budget Tracker
    st.subheader("💰 Monthly Budget Tracker")

    remaining_budget = saved_budget - total_spending

    if saved_budget > 0:
        budget_percentage = (total_spending / saved_budget) * 100
    else:
        budget_percentage = 0

    budget_col1, budget_col2 = st.columns(2)

    
    with budget_col1:
        with st.container(border=True):
            st.metric(
                "💰 Monthly Budget",
                f"₹{saved_budget:,.2f}"
            )

    with budget_col2:
        with st.container(border=True):
            st.metric(
                "💚 Remaining Budget",
                f"₹{remaining_budget:,.2f}"
            )

    st.progress(min(budget_percentage / 100, 1.0))

    st.write(f"Budget Used: {budget_percentage:.1f}%")

    if remaining_budget < 0:
        st.error("⚠️ You have exceeded your monthly budget!")

    # Spending Chart
    st.subheader("📊 Spending by Category")

    if monthly_expenses.empty:
        st.info("No spending data available for this month.")

    else:
        category_spending = monthly_expenses.groupby(
            "Category",
            as_index=False
        )["Amount"].sum()

        fig = px.pie(
            category_spending,
            names="Category",
            values="Amount",
            hole=0.5,
            title="Monthly Spending Breakdown"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Recent Expenses
    st.subheader("🧾 Recent Expenses")

    if df.empty:
        st.info("No expenses added yet.")

    else:
        recent_expenses = df.tail(5).iloc[::-1]

        st.dataframe(
            recent_expenses,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # Add Expense Form
    st.subheader("➕ Add New Expense")

    with st.form("expense_form"):

        expense_name = st.text_input("Expense Name")

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=10.0
        )

        category = st.selectbox(
            "Category",
            ["Food", "Travel", "Shopping", "Bills", "Other"]
        )

        submitted = st.form_submit_button("Add Expense")

        if submitted:

            if expense_name.strip() == "":
                st.error("Please enter an expense name!")

            elif amount <= 0:
                st.error("Amount must be greater than zero!")

            else:
                new_expense = pd.DataFrame([{
                    "Date": str(date.today()),
                    "Expense Name": expense_name.strip(),
                    "Amount": amount,
                    "Category": category
                }])

                new_expense.to_csv(
                    FILE_NAME,
                    mode="a",
                    header=False,
                    index=False
                )

                st.success("Expense Added Successfully!")
                st.rerun()


# History Page
elif page == "History":

    st.title("📜 Expense History")
    st.write("View all your recorded expenses.")

    if df.empty:
        st.info("No expenses recorded yet.")

    else:
        selected_category = st.selectbox(
            "Filter by Category",
            [
                "All Categories",
                "Food",
                "Travel",
                "Shopping",
                "Bills",
                "Other"
            ]
        )

        if selected_category == "All Categories":
            history_df = df.iloc[::-1]

        else:
            history_df = df[
                df["Category"] == selected_category
            ].iloc[::-1]

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

        st.metric(
            "Filtered Total Spending",
            f"₹{history_df['Amount'].sum():,.2f}"
        )

        st.divider()

        # Delete Expense
        st.subheader("🗑️ Delete Expense")

        if not history_df.empty:

            selected_expense = st.selectbox(
                "Select Expense to Delete",
                history_df.index.tolist(),
                format_func=lambda i: (
                    f"{df.loc[i, 'Expense Name']} - "
                    f"₹{df.loc[i, 'Amount']:.2f} - "
                    f"{df.loc[i, 'Category']}"
                )
            )

            st.write(
                "Selected Expense:",
                df.loc[selected_expense, "Expense Name"]
            )

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this expense."
            )

            if st.button(
                "🗑️ Delete Selected Expense",
                disabled=not confirm_delete
            ):

                df = df.drop(index=selected_expense)

                df.to_csv(
                    FILE_NAME,
                    index=False,
                    date_format="%Y-%m-%d"
                )

                st.rerun()

        else:
            st.info("No expenses available to delete.")


# Settings Page
elif page == "Settings":

    st.title("⚙️ Settings")
    st.subheader("💰 Monthly Budget")

    monthly_budget = st.number_input(
        "Enter Your Monthly Budget (₹)",
        min_value=0.0,
        value=saved_budget,
        step=500.0
    )

    if st.button("💾 Save Budget"):

        with open(BUDGET_FILE, "w") as file:
            file.write(str(monthly_budget))

        st.success("Monthly Budget Saved Successfully!")
