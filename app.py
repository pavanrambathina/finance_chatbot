import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from recommendations import generate_recommendations

st.set_page_config(
    page_title="Finance Budget Chatbot",
    layout="wide"
)

st.title("Smart Personal Finance Budget Chatbot")

@st.cache_data
def load_data():
    transactions = pd.read_csv("personal_transactions.csv")
    budget = pd.read_csv("budget.csv")

    transactions.columns = transactions.columns.str.strip()
    budget.columns = budget.columns.str.strip()

    transactions["Date"] = pd.to_datetime(transactions["Date"], errors="coerce")
    transactions = transactions.dropna(subset=["Date"])

    transactions["Month"] = transactions["Date"].dt.strftime("%Y-%m")

    return transactions, budget


transactions, budget = load_data()

st.sidebar.header("Filters")

months = sorted(transactions["Month"].unique())

selected_month = st.sidebar.selectbox(
    "Select Month",
    months
)

month_data = transactions[transactions["Month"] == selected_month]

expenses = month_data[
    month_data["Transaction Type"].str.lower() == "debit"
]

income_data = month_data[
    month_data["Transaction Type"].str.lower() == "credit"
]

st.subheader(" Monthly Summary")

total_income = income_data["Amount"].sum()
total_spent = expenses["Amount"].sum()
balance = total_income - total_spent

col1, col2, col3 = st.columns(3)
col1.metric("Income", f"${total_income:.2f}")
col2.metric("Expenses", f"${total_spent:.2f}")
col3.metric("Balance", f"${balance:.2f}")

st.subheader("Category-wise Spending")

category_spending = (
    expenses.groupby("Category")["Amount"]
    .sum()
    .reset_index()
    .sort_values("Amount", ascending=False)
)

st.dataframe(category_spending, use_container_width=True)

if not category_spending.empty:
    top = category_spending.iloc[0]

    st.success(
        f" Highest Spending Category: {top['Category']} (${top['Amount']:.2f})"
    )

    if total_income > 0:
        savings_rate = (balance / total_income) * 100
        st.info(f" Savings Rate: {savings_rate:.2f}%")

    st.info(f" Transactions this month: {len(month_data)}")

st.subheader(" Top 10 Spending Categories")

if not category_spending.empty:
    chart_data = category_spending.sort_values("Amount", ascending=True).tail(10)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(chart_data["Category"], chart_data["Amount"])
    ax.set_xlabel("Amount Spent")
    ax.set_ylabel("Category")
    ax.set_title("Top Spending Categories")

    st.pyplot(fig)
else:
    st.warning("No expense data available for this month.")

st.subheader("💡 Smart Financial Recommendations")

recommendations = generate_recommendations(
    total_income,
    total_spent,
    balance,
    category_spending
)

for rec in recommendations:
    st.warning(rec)

st.subheader(" Download Financial Report")

if not category_spending.empty:
    top = category_spending.iloc[0]
    highest_category_text = f"{top['Category']} - ${top['Amount']:.2f}"
else:
    highest_category_text = "No spending data available"

report = f"""
Smart Personal Finance Budget Report

Month: {selected_month}

Income: ${total_income:.2f}
Expenses: ${total_spent:.2f}
Balance: ${balance:.2f}

Highest Spending Category:
{highest_category_text}

Recommendations:
"""

for rec in recommendations:
    report += f"- {rec}\n"

st.download_button(
    label="Download Report",
    data=report,
    file_name=f"finance_report_{selected_month}.txt",
    mime="text/plain"
)

st.subheader("Budget vs Actual")

budget.columns = budget.columns.str.strip()
category_spending.columns = category_spending.columns.str.strip()

if "Category" in budget.columns:
    merged = pd.merge(
        budget,
        category_spending,
        on="Category",
        how="left"
    )

    merged["Amount"] = merged["Amount"].fillna(0)

    budget_col = [
        col for col in merged.columns
        if col.lower() != "category" and col.lower() != "amount"
    ][0]

    merged["Status"] = merged.apply(
        lambda row: "Over Budget"
        if row["Amount"] > row[budget_col]
        else "Within Budget",
        axis=1
    )

    st.dataframe(merged, use_container_width=True)
else:
    st.error("budget.csv must contain a Category column.")
    merged = pd.DataFrame()

st.subheader("🤖 Finance Chatbot")

question = st.text_input("Ask a finance question")

if question:
    q = question.lower()

    if "income" in q:
        st.write(f"Your income in {selected_month} is ${total_income:.2f}.")

    elif "expense" in q or "spent" in q or "total" in q:
        st.write(f"You spent ${total_spent:.2f} in {selected_month}.")

    elif "balance" in q or "saving" in q:
        st.write(f"Your balance/savings in {selected_month} is ${balance:.2f}.")

    elif "highest" in q or "most" in q:
        if not category_spending.empty:
            top = category_spending.iloc[0]
            st.write(
                f"You spent the most on {top['Category']} = ${top['Amount']:.2f}."
            )
        else:
            st.write("No expense data available for this month.")

    elif "save" in q or "money" in q:
        if not category_spending.empty:
            top = category_spending.iloc[0]
            reduce_amount = top["Amount"] * 0.10

            st.write(
                f"To save more money, reduce spending on {top['Category']}. "
                f"If you cut it by 10%, you can save around ${reduce_amount:.2f}."
            )
        else:
            st.write("No spending data available to generate savings advice.")

    elif "budget" in q:
        if not merged.empty:
            over_budget = merged[merged["Status"] == "Over Budget"]

            if not over_budget.empty:
                st.write("These categories are over budget:")
                st.dataframe(over_budget, use_container_width=True)
            else:
                st.write("Good. No category crossed the budget.")
        else:
            st.write("Budget data is not available.")

    else:
        st.write(
            "Ask questions like: income, expenses, balance, highest spending, "
            "how to save money, or budget status."
        )