"""
Reports and Financial Analytics Module for Personal Expense & Budget Tracker.

Calculates monthly spending summaries, category-wise percentage contributions,
identifies highest and lowest expense categories, calculates average daily burn rates,
and provides month-over-month comparative analytics with ASCII visualizations.
"""

import calendar
from datetime import datetime
from typing import Any

from utils import (
    format_inr,
    print_formatted_grid,
    prompt_menu_choice,
    prompt_month_ym,
)


def get_days_in_month(year: int, month: int) -> int:
    """
    Return the total number of days in the specified year and month.

    Args:
        year: Full calendar year (e.g., 2026).
        month: Month number (1-12).

    Returns:
        Total days count in that month.
    """
    return calendar.monthrange(year, month)[1]


def render_distribution_bar(fraction: float, bar_span: int = 16) -> str:
    """
    Render a horizontal ASCII distribution bar representing relative category proportion.

    Args:
        fraction: Numeric ratio between 0.0 and 1.0.
        bar_span: Maximum character length of the bar.

    Returns:
        String composed of solid and shaded block characters.
    """
    clamped = max(0.0, min(fraction, 1.0))
    solid_count = int(round(clamped * bar_span))
    return "█" * solid_count + "░" * (bar_span - solid_count)


def generate_monthly_summary(
    expenses: list[dict[str, Any]],
    month_key: str | None = None
) -> None:
    """
    Generate and print an analytical spending summary for a specific calendar month.

    Displays:
    - Total monthly spend
    - Total transaction volume
    - Average expenditure per transaction
    - Calendar-aware average daily spend
    - Highest & lowest spending categories with percentage shares
    - Largest single transaction
    - Category-wise breakdown table with percentage share and horizontal ASCII bars

    Args:
        expenses: Full list of recorded expenses.
        month_key: Target month string 'YYYY-MM'. If None, prompts user.
    """
    if month_key is None:
        month_key = prompt_month_ym("Enter month for summary (YYYY-MM)", default_current=True)

    month_records = [
        rec for rec in expenses
        if str(rec.get("date", "")).startswith(month_key)
    ]

    print("\n" + "=" * 65)
    print(f"        MONTHLY SPENDING REPORT: {month_key}".center(65))
    print("=" * 65)

    if not month_records:
        print(f"\n  No expenses recorded for {month_key}.\n")
        return

    total_spent = sum(float(rec.get("amount", 0.0)) for rec in month_records)
    transaction_count = len(month_records)

    # Category totals and counts
    cat_spend_map: dict[str, float] = {}
    cat_count_map: dict[str, int] = {}
    for rec in month_records:
        cat = str(rec.get("category", "Other"))
        amt = float(rec.get("amount", 0.0))
        cat_spend_map[cat] = cat_spend_map.get(cat, 0.0) + amt
        cat_count_map[cat] = cat_count_map.get(cat, 0) + 1

    sorted_categories = sorted(cat_spend_map.items(), key=lambda item: item[1], reverse=True)
    top_cat, top_cat_amt = sorted_categories[0]
    lowest_cat, lowest_cat_amt = sorted_categories[-1]

    # Largest single expense
    largest_expense = max(month_records, key=lambda r: float(r.get("amount", 0.0)))

    # Calendar-aware daily burn rate calculation
    year_val, month_val = map(int, month_key.split("-"))
    days_in_month = get_days_in_month(year_val, month_val)
    today = datetime.now()

    if year_val == today.year and month_val == today.month:
        effective_days = max(1, today.day)
        daily_average = total_spent / effective_days
        days_annotation = f"(based on {effective_days} days elapsed in current month)"
    else:
        daily_average = total_spent / days_in_month
        days_annotation = f"(based on {days_in_month} days in month)"

    # Print executive metrics
    print(f"\n  • Total Monthly Spending: {format_inr(total_spent)}")
    print(f"  • Total Transactions    : {transaction_count}")
    print(f"  • Average per Expense   : {format_inr(total_spent / transaction_count)}")
    print(f"  • Average Daily Spend   : {format_inr(daily_average)} {days_annotation}")
    print(f"  • Top Spending Category : {top_cat} ({format_inr(top_cat_amt)} - {(top_cat_amt / total_spent * 100):.1f}%)")
    print(f"  • Lowest Category       : {lowest_cat} ({format_inr(lowest_cat_amt)} - {(lowest_cat_amt / total_spent * 100):.1f}%)")
    print(f"  • Largest Single Expense: {format_inr(float(largest_expense['amount']))} ({largest_expense['description']} on {largest_expense['date']})")

    # Category breakdown table
    print("\n--- Category-wise Breakdown ---")
    headers = ["Category", "Total Spent", "% of Month", "Count", "Distribution"]
    rows = []

    for cat_name, amt_val in sorted_categories:
        pct_share = (amt_val / total_spent * 100.0) if total_spent > 0 else 0.0
        bar_viz = render_distribution_bar(amt_val / total_spent if total_spent > 0 else 0.0, bar_span=16)
        rows.append([
            cat_name,
            format_inr(amt_val),
            f"{pct_share:.1f}%",
            str(cat_count_map.get(cat_name, 0)),
            bar_viz,
        ])

    print_formatted_grid(headers, rows, column_alignments=["<", ">", ">", "^", "<"])
    print()


def generate_monthly_comparison(expenses: list[dict[str, Any]]) -> None:
    """
    Display a chronological month-over-month comparison of spending habits.

    Calculates:
    - Monthly total spend
    - Transaction count
    - Leading category
    - Percentage change compared to the preceding month
    """
    print("\n" + "=" * 65)
    print("            MONTH-OVER-MONTH SPENDING COMPARISON".center(65))
    print("=" * 65)

    if not expenses:
        print("\n  No expense records available for comparison.\n")
        return

    # Group expenses by month
    monthly_groups: dict[str, list[dict[str, Any]]] = {}
    for rec in expenses:
        m_tag = str(rec.get("date", ""))[:7]
        if m_tag:
            monthly_groups.setdefault(m_tag, []).append(rec)

    chronological_months = sorted(monthly_groups.keys())
    if not chronological_months:
        print("\n  No valid month records found.\n")
        return

    headers = ["Month", "Total Spent", "Transactions", "Top Category", "MoM Change"]
    rows = []
    previous_month_spend: float | None = None

    for m_tag in chronological_months:
        records_in_month = monthly_groups[m_tag]
        monthly_total = sum(float(r.get("amount", 0.0)) for r in records_in_month)
        txn_count = len(records_in_month)

        # Leading category
        cat_tally: dict[str, float] = {}
        for r in records_in_month:
            c = str(r.get("category", "Other"))
            cat_tally[c] = cat_tally.get(c, 0.0) + float(r.get("amount", 0.0))
        lead_cat = max(cat_tally.items(), key=lambda x: x[1])[0] if cat_tally else "None"

        # Month-over-month delta
        if previous_month_spend is None or previous_month_spend == 0:
            mom_display = "Baseline"
        else:
            diff = monthly_total - previous_month_spend
            pct_delta = (diff / previous_month_spend) * 100.0
            sign = "+" if pct_delta > 0 else ""
            mom_display = f"{sign}{pct_delta:.1f}%"

        rows.append([
            m_tag,
            format_inr(monthly_total),
            str(txn_count),
            lead_cat,
            mom_display,
        ])
        previous_month_spend = monthly_total

    print()
    print_formatted_grid(headers, rows, column_alignments=["^", ">", "^", "<", ">"])
    print()


def generate_all_time_category_summary(expenses: list[dict[str, Any]]) -> None:
    """Display cumulative all-time category spending summary and share."""
    print("\n" + "=" * 65)
    print("              ALL-TIME CATEGORY SPENDING".center(65))
    print("=" * 65)

    if not expenses:
        print("\n  No expense records available.\n")
        return

    total_all_time = sum(float(r.get("amount", 0.0)) for r in expenses)
    cumulative_cat_map: dict[str, float] = {}
    cumulative_cat_counts: dict[str, int] = {}

    for rec in expenses:
        c = str(rec.get("category", "Other"))
        amt = float(rec.get("amount", 0.0))
        cumulative_cat_map[c] = cumulative_cat_map.get(c, 0.0) + amt
        cumulative_cat_counts[c] = cumulative_cat_counts.get(c, 0) + 1

    ranked_categories = sorted(cumulative_cat_map.items(), key=lambda x: x[1], reverse=True)

    headers = ["Category", "All-Time Spend", "% Share", "Transactions", "Visual Share"]
    rows = []

    for cat_name, total_cat_amt in ranked_categories:
        pct_all = (total_cat_amt / total_all_time * 100.0) if total_all_time > 0 else 0.0
        bar = render_distribution_bar(total_cat_amt / total_all_time if total_all_time > 0 else 0.0, bar_span=16)
        rows.append([
            cat_name,
            format_inr(total_cat_amt),
            f"{pct_all:.1f}%",
            str(cumulative_cat_counts.get(cat_name, 0)),
            bar,
        ])

    print()
    print_formatted_grid(headers, rows, column_alignments=["<", ">", ">", "^", "<"])
    print(f" Total Records: {len(expenses)} | Cumulative Outflow: {format_inr(total_all_time)}\n")


def spending_summary_flow(expenses: list[dict[str, Any]]) -> None:
    """
    Menu option 7 flow: Interactive menu for spending reports and analytics.

    Args:
        expenses: List of expense dictionaries.
    """
    while True:
        print("\n" + "=" * 50)
        print("               SPENDING SUMMARY")
        print("=" * 50)
        print("  [1] Monthly Spending Summary & Report")
        print("  [2] Month-over-Month Spending Comparison")
        print("  [3] All-Time Category Breakdown")
        print("  [0] Return to Main Menu")
        print("=" * 50)

        opt = prompt_menu_choice("Enter choice [0-3]: ", ["0", "1", "2", "3"])

        if opt == "0":
            break
        elif opt == "1":
            generate_monthly_summary(expenses)
        elif opt == "2":
            generate_monthly_comparison(expenses)
        elif opt == "3":
            generate_all_time_category_summary(expenses)
