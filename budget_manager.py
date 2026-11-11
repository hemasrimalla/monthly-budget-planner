"""
Budget Management Module for Personal Expense & Budget Tracker.

Handles setting, updating, and reviewing monthly overall and category budgets.
Computes real-time spending vs budget, calculates remaining balances, renders
progress meters, and issues 80% warnings and >100% exceeded alerts.
"""

from typing import Any

from expense_manager import get_all_categories
from storage import save_budgets
from utils import (
    build_progress_meter,
    format_inr,
    print_formatted_grid,
    prompt_amount,
    prompt_menu_choice,
    prompt_month_ym,
    prompt_yes_no,
)


def compute_month_totals(
    expenses: list[dict[str, Any]],
    month_key: str
) -> tuple[float, dict[str, float]]:
    """
    Calculate the total spend and category-wise spending breakdown for a specific month.

    Args:
        expenses: List of all recorded expenses.
        month_key: Target month string in 'YYYY-MM' format.

    Returns:
        A tuple of (total_monthly_spent, dict_of_category_spending).
    """
    total_spent = 0.0
    category_map: dict[str, float] = {}

    for record in expenses:
        date_str = str(record.get("date", ""))
        if date_str.startswith(month_key):
            amt = float(record.get("amount", 0.0))
            cat = str(record.get("category", "Other"))
            total_spent += amt
            category_map[cat] = category_map.get(cat, 0.0) + amt

    return total_spent, category_map


def view_monthly_budget_status(
    budgets: dict[str, Any],
    expenses: list[dict[str, Any]],
    month_key: str | None = None
) -> None:
    """
    Display comprehensive budget status for a given month.

    Shows budget vs. spent, remaining balance, visual progress meter,
    and automatic warnings (80%+) or alerts (>100%).

    Args:
        budgets: Current dictionary of monthly budget configurations.
        expenses: List of expense dictionaries.
        month_key: Target month 'YYYY-MM'. If None, prompts the user.
    """
    if month_key is None:
        month_key = prompt_month_ym("Enter month to check budget (YYYY-MM)", default_current=True)

    month_data = budgets.get(month_key, {})
    total_budget = float(month_data.get("total_budget", 0.0))
    cat_budgets: dict[str, float] = {
        k: float(v) for k, v in month_data.get("category_budgets", {}).items()
    }

    total_spent, cat_spending = compute_month_totals(expenses, month_key)

    print("\n" + "=" * 65)
    print(f"       BUDGET STATUS FOR {month_key}".center(65))
    print("=" * 65)

    if total_budget <= 0 and not cat_budgets:
        print(f"\n  [i] Notice: No budget is currently configured for {month_key}.")
        print(f"  Total Spending recorded in {month_key}: {format_inr(total_spent)}")
        if cat_spending:
            print("  Category Spending Breakdown:")
            for cat, amt in sorted(cat_spending.items(), key=lambda x: x[1], reverse=True):
                print(f"    - {cat}: {format_inr(amt)}")
        print("\n  Tip: Use Menu option [5] to set a monthly budget for this month.\n")
        return

    # 1. Total Monthly Budget Summary
    remaining = total_budget - total_spent
    pct_used = (total_spent / total_budget * 100.0) if total_budget > 0 else 0.0

    print(f"\nTotal Budget : {format_inr(total_budget)}")
    print(f"Total Spent  : {format_inr(total_spent)}")
    print(f"Remaining    : {format_inr(remaining)}")
    print(f"Utilization  : {build_progress_meter(pct_used)}")

    # Warning / Exceeded status badge
    if total_budget > 0:
        if pct_used > 100.0:
            excess = total_spent - total_budget
            print(f"Status       : [!] ALERT: Budget EXCEEDED by {format_inr(excess)} ({(pct_used - 100):.1f}% over budget)!")
        elif pct_used >= 80.0:
            print(f"Status       : [!] WARNING: 80%+ Utilized ({pct_used:.1f}% consumed, {format_inr(remaining)} remaining).")
        else:
            print(f"Status       : [OK] On Track ({(100 - pct_used):.1f}% remaining)")

    # 2. Category Budgets Table
    all_categories = sorted(set(list(cat_budgets.keys()) + list(cat_spending.keys())))
    if all_categories:
        print("\nCategory-wise Budget Breakdown:")
        cat_headers = ["Category", "Budget", "Spent", "Remaining", "Used %", "Status"]
        cat_rows = []

        for cat in all_categories:
            c_budget = cat_budgets.get(cat, 0.0)
            c_spent = cat_spending.get(cat, 0.0)
            c_rem = c_budget - c_spent if c_budget > 0 else -c_spent

            if c_budget > 0:
                c_pct = (c_spent / c_budget) * 100.0
                c_pct_str = f"{c_pct:.1f}%"
                if c_pct > 100.0:
                    status_badge = "[!] EXCEEDED"
                elif c_pct >= 80.0:
                    status_badge = "[!] WARNING"
                else:
                    status_badge = "[OK] On Track"
                budget_str = format_inr(c_budget)
                rem_str = format_inr(c_rem)
            else:
                budget_str = "No Budget"
                c_pct_str = "-"
                status_badge = "Untracked"
                rem_str = "-"

            cat_rows.append([
                cat,
                budget_str,
                format_inr(c_spent),
                rem_str,
                c_pct_str,
                status_badge,
            ])

        print_formatted_grid(
            cat_headers,
            cat_rows,
            column_alignments=["<", ">", ">", ">", ">", "^"]
        )
    print()


def set_monthly_budget(budgets: dict[str, Any]) -> dict[str, Any]:
    """
    Configure or update the overall budget amount for a month.

    Args:
        budgets: Budget dictionary.

    Returns:
        Updated budgets dictionary.
    """
    print("\n" + "=" * 50)
    print("           SET MONTHLY OVERALL BUDGET")
    print("=" * 50)

    month_key = prompt_month_ym("Enter month (YYYY-MM)", default_current=True)
    existing_budget = float(budgets.get(month_key, {}).get("total_budget", 0.0))

    if existing_budget > 0:
        print(f"Current overall budget for {month_key}: {format_inr(existing_budget)}")

    budget_amount = prompt_amount("Enter overall budget amount for the month (₹)")

    if month_key not in budgets:
        budgets[month_key] = {"total_budget": budget_amount, "category_budgets": {}}
    else:
        budgets[month_key]["total_budget"] = budget_amount

    if save_budgets(budgets):
        print(f"\n[OK] Monthly budget of {format_inr(budget_amount)} saved for {month_key}!")
    else:
        print("\n[!] Error: Failed to save budget configuration to storage.")

    return budgets


def set_category_budget(
    budgets: dict[str, Any],
    expenses: list[dict[str, Any]],
    custom_categories: set[str] | None = None
) -> dict[str, Any]:
    """
    Configure or update a specific category budget within a month.

    Args:
        budgets: Budget dictionary.
        expenses: Expense list.
        custom_categories: Custom categories set.

    Returns:
        Updated budgets dictionary.
    """
    print("\n" + "=" * 50)
    print("           SET CATEGORY-WISE BUDGET")
    print("=" * 50)

    month_key = prompt_month_ym("Enter month (YYYY-MM)", default_current=True)
    if month_key not in budgets:
        budgets[month_key] = {"total_budget": 0.0, "category_budgets": {}}
    elif "category_budgets" not in budgets[month_key]:
        budgets[month_key]["category_budgets"] = {}

    available_cats = get_all_categories(expenses, custom_categories)
    print(f"\nAvailable Categories for {month_key}:")
    for idx, c in enumerate(available_cats, start=1):
        curr_b = float(budgets[month_key]["category_budgets"].get(c, 0.0))
        curr_tag = f" [Current: {format_inr(curr_b)}]" if curr_b > 0 else ""
        print(f"  [{idx}] {c}{curr_tag}")

    choice_idx = int(prompt_menu_choice("Select category number: ", [str(i) for i in range(1, len(available_cats) + 1)]))
    chosen_cat = available_cats[choice_idx - 1]

    print(f"\nSetting budget for category: '{chosen_cat}' in month {month_key}")
    cat_amount = prompt_amount("Enter budget amount (₹, enter 0 to remove budget)", permit_zero=True)

    if cat_amount == 0:
        if chosen_cat in budgets[month_key]["category_budgets"]:
            del budgets[month_key]["category_budgets"][chosen_cat]
            print(f"[OK] Category budget for '{chosen_cat}' removed.")
    else:
        budgets[month_key]["category_budgets"][chosen_cat] = cat_amount
        print(f"[OK] Category budget for '{chosen_cat}' set to {format_inr(cat_amount)} for {month_key}!")

    save_budgets(budgets)
    return budgets


def list_all_budgets(budgets: dict[str, Any]) -> None:
    """Display a summary overview of all months with configured budgets."""
    print("\n" + "=" * 65)
    print("              ALL CONFIGURED BUDGETS".center(65))
    print("=" * 65)

    if not budgets:
        print("\n  No budgets configured yet.\n")
        return

    headers = ["Month", "Overall Budget", "Category Budgets Defined"]
    rows = []

    for month_key in sorted(budgets.keys(), reverse=True):
        m_info = budgets[month_key]
        total_b = float(m_info.get("total_budget", 0.0))
        cat_count = len(m_info.get("category_budgets", {}))
        rows.append([
            month_key,
            format_inr(total_b) if total_b > 0 else "Not set",
            f"{cat_count} categories" if cat_count > 0 else "None",
        ])

    print_formatted_grid(headers, rows, column_alignments=["^", ">", "^"])
    print()


def set_monthly_budget_flow(
    budgets: dict[str, Any],
    expenses: list[dict[str, Any]],
    custom_categories: set[str] | None = None
) -> dict[str, Any]:
    """
    Menu option 5 flow: Submenu for setting overall and category-specific budgets.

    Args:
        budgets: Current budget dictionary.
        expenses: Expense list.
        custom_categories: Set of custom categories.

    Returns:
        Updated budgets dictionary.
    """
    while True:
        print("\n" + "=" * 50)
        print("              SET MONTHLY BUDGET")
        print("=" * 50)
        print("  [1] Set / Update Total Monthly Budget (Overall)")
        print("  [2] Set / Update Category-Specific Budget")
        print("  [3] View All Configured Budgets")
        print("  [0] Return to Main Menu")
        print("=" * 50)

        opt = prompt_menu_choice("Enter choice [0-3]: ", ["0", "1", "2", "3"])

        if opt == "0":
            break
        elif opt == "1":
            budgets = set_monthly_budget(budgets)
        elif opt == "2":
            budgets = set_category_budget(budgets, expenses, custom_categories)
        elif opt == "3":
            list_all_budgets(budgets)

    return budgets


def check_budget_status_flow(
    budgets: dict[str, Any],
    expenses: list[dict[str, Any]]
) -> None:
    """
    Menu option 6 flow: Prompt for month and check budget status.

    Args:
        budgets: Budget dictionary.
        expenses: Expense list.
    """
    month_key = prompt_month_ym("Enter month to check budget (YYYY-MM)", default_current=True)
    view_monthly_budget_status(budgets, expenses, month_key)
