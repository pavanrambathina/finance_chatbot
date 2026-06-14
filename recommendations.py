def generate_recommendations(total_income, total_spent, balance, category_spending):
    recommendations = []

    if total_income > 0:
        savings_rate = (balance / total_income) * 100

        if savings_rate < 20:
            recommendations.append("Your savings rate is below 20%. Reduce non-essential spending.")
        else:
            recommendations.append("Your savings rate is healthy. Maintain your current spending control.")

    if not category_spending.empty:
        top = category_spending.sort_values("Amount", ascending=False).iloc[0]
        cut_amount = top["Amount"] * 0.10

        recommendations.append(
            f"Your highest spending category is {top['Category']}. "
            f"Reducing it by 10% can save around ${cut_amount:.2f}."
        )

    if total_spent > total_income:
        recommendations.append("Your expenses are higher than your income. Fix this immediately.")

    return recommendations