import streamlit as st
import pandas as pd
import plotly.express as px

from recommendations import generate_recommendations

st.set_page_config(
    page_title="AI-Powered Personal Finance Budget Chatbot",
    layout="wide"
)

st.title("AI-Powered Personal Finance Budget Chatbot")

# Load CSV files safely
try:
    transactions = pd.read_csv("personal_transactions.csv")
    budget = pd.read_csv("budget.csv")
except FileNotFoundError as e:
    st.error(f"Missing file: {e.filename}")
    st.stop()

# Clean column names
transactions.columns = transactions.columns.str.strip()
budget.columns = budget.columns.str.strip()

st.sidebar.header("Filters")

# Convert date column
transactions["Transaction Date"] = pd.to_datetime(
    transactions["Transaction Date"],
    errors="coerce"
)

transactions = transactions.dropna(subset=["Transaction Date"])

transactions["Month"] = transactions["Transaction Date"].dt.month_name()

selected_month = st.sidebar.selectbox(
    "Select Month",
    sorted(transactions["Month"].unique())
)

filtered_transactions = transactions[
    transactions["Month"] == selected_month
]

st.subheader(f"Transactions for {selected_month}")
st.dataframe(filtered_transactions)

# Summary
total_spent = filtered_transactions["Amount"].sum()
st.metric("Total Spending", f"₹{total_spent:,.2f}")

# Category spending chart
if "Category" in filtered_transactions.columns:
    category_spending = (
        filtered_transactions
        .groupby("Category")["Amount"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        category_spending,
        x="Category",
        y="Amount",
        title="Spending by Category"
    )

    st.plotly_chart(fig, use_container_width=True)

# Budget comparison
st.subheader("Budget Overview")
st.dataframe(budget)

# Recommendations
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