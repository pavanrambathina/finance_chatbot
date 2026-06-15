import streamlit as st
import pandas as pd
import plotly.express as px

from recommendations import generate_recommendations

st.set_page_config(
    page_title="AI-Powered Personal Finance Budget Chatbot",
    layout="wide"
)

st.title("AI-Powered Personal Finance Budget Chatbot")

try:
    transactions = pd.read_csv("personal_transactions.csv")
    budget = pd.read_csv("budget.csv")
except FileNotFoundError as e:
    st.error(f"Missing file: {e.filename}")
    st.stop()

transactions.columns = transactions.columns.str.strip()
budget.columns = budget.columns.str.strip()

required_columns = ["Date", "Description", "Amount", "Transaction Type", "Category", "Account Name"]

missing_columns = [col for col in required_columns if col not in transactions.columns]

if missing_columns:
    st.error(f"Missing columns in personal_transactions.csv: {missing_columns}")
    st.write("Available columns:", transactions.columns.tolist())
    st.stop()

transactions["Date"] = pd.to_datetime(transactions["Date"], errors="coerce")
transactions["Amount"] = pd.to_numeric(transactions["Amount"], errors="coerce")

transactions = transactions.dropna(subset=["Date", "Amount"])

transactions["Month"] = transactions["Date"].dt.month_name()

st.sidebar.header("Filters")

months = sorted(transactions["Month"].unique())

selected_month = st.sidebar.selectbox(
    "Select Month",
    months
)

filtered_transactions = transactions[
    transactions["Month"] == selected_month
]

st.subheader(f"Transactions for {selected_month}")
st.dataframe(filtered_transactions, use_container_width=True)

total_spent = filtered_transactions[
    filtered_transactions["Transaction Type"].str.lower() == "debit"
]["Amount"].sum()

total_income = filtered_transactions[
    filtered_transactions["Transaction Type"].str.lower() == "credit"
]["Amount"].sum()

balance = total_income - total_spent

col1, col2, col3 = st.columns(3)

col1.metric("Total Income", f"₹{total_income:,.2f}")
col2.metric("Total Spending", f"₹{total_spent:,.2f}")
col3.metric("Balance", f"₹{balance:,.2f}")

st.subheader("Spending by Category")

debit_transactions = filtered_transactions[
    filtered_transactions["Transaction Type"].str.lower() == "debit"
]

if not debit_transactions.empty:
    category_spending = (
        debit_transactions
        .groupby("Category")["Amount"]
        .sum()
        .reset_index()
        .sort_values(by="Amount", ascending=False)
    )

    fig = px.bar(
        category_spending,
        x="Category",
        y="Amount",
        title="Category-wise Spending"
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No debit transactions found for this month.")

st.subheader("Budget Overview")
st.dataframe(budget, use_container_width=True)

st.subheader("Top Expenses")

top_expenses = debit_transactions.sort_values(by="Amount", ascending=False).head(10)

if not top_expenses.empty:
    st.dataframe(top_expenses, use_container_width=True)
else:
    st.info("No expenses available.")

st.subheader("AI Recommendations")

try:
    recommendations = generate_recommendations(filtered_transactions, budget)

    if isinstance(recommendations, list):
        for item in recommendations:
            st.write(f"- {item}")
    else:
        st.write(recommendations)

except Exception as e:
    st.warning("Recommendations could not be generated.")
    st.write(e)