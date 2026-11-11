"""
Expense Management Module for Personal Expense & Budget Tracker.

Implements CRUD operations (Create, Read, Update, Delete) for daily expenses,
handles default and custom categories, provides instant budget threshold alerts,
and supports multi-attribute searching, filtering, and sorting.
"""

from datetime import datetime
from typing import Any

from storage import save_expenses
from utils import (
    format_inr,
    print_formatted_grid,
    prompt_amount,
    prompt_date_ymd,
    prompt_menu_choice,
    prompt_month_ym,
    prompt_non_empty_string,
    prompt_yes_no,
)

# Standard default expense categories
DEFAULT_CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Education",
    "Other",
]


def get_all_categories(
    expenses: list[dict[str, Any]],
    custom_categories: set[str] | None = None
) -> list[str]:
    """
    Retrieve a sorted list of all unique categories available.

    Combines standard default categories with custom categories and any
    already present in existing expense records.

    Args:
        expenses: List of existing expense dictionaries.
        custom_categories: Set of user-defined custom categories.

    Returns:
        Alphabetically sorted list of distinct category names.
    """
    unique_cats = set(DEFAULT_CATEGORIES)
    if custom_categories:
        unique_cats.update(custom_categories)
    for record in expenses:
        cat_name = record.get("category")
        if cat_name:
            unique_cats.add(cat_name.strip().title())
    return sorted(unique_cats)


def choose_or_create_category(category_list: list[str]) -> str:
    """
    Display available categories and prompt user to select one or add a new custom category.

    Args:
        category_list: Currently available category names.

    Returns:
        The selected or newly created category string.
    """
    print("\n--- Select Expense Category ---")
    for idx, name in enumerate(category_list, start=1):
        print(f"  [{idx}] {name}")
    print(f"  [{len(category_list) + 1}] + Add New Custom Category")

    allowed_choices = [str(i) for i in range(1, len(category_list) + 2)]
    selected_idx = int(prompt_menu_choice("Select category number: ", allowed_choices))

    if selected_idx <= len(category_list):
        return category_list[selected_idx - 1]

    # Prompt for custom category name
    while True:
        custom_name = prompt_non_empty_string("Enter new category name").strip().title()
        if not custom_name:
            print("  [!] Category name cannot be empty.")
            continue
        return custom_name


def compute_next_id(expenses: list[dict[str, Any]]) -> int:
    """
    Compute the next unique incremental integer ID for a new expense record.

    Args:
        expenses: Existing expense list.

    Returns:
        Next unique integer identifier.
    """
    if not expenses:
        return 1
    return max(int(rec.get("id", 0)) for rec in expenses) + 1


def add_expense_flow(
    expenses: list[dict[str, Any]],
    budgets: dict[str, Any],
    custom_categories: set[str] | None = None
) -> list[dict[str, Any]]:
    """
    Interactive flow to add a new expense.

    Validates date, amount, category, and description.
    Auto-saves to persistent JSON storage and instantly checks against monthly budget.

    Args:
        expenses: List of expense dictionaries.
        budgets: Current budget configurations.
        custom_categories: Set of custom categories.

    Returns:
        Updated list of expenses.
    """
    print("\n" + "=" * 55)
    print("                  ADD NEW EXPENSE")
    print("=" * 55)

    # 1. Date (default today)
    expense_date = prompt_date_ymd("Enter expense date (YYYY-MM-DD)", default_today=True)

    # 2. Amount (> 0, non-negative)
    expense_amount = prompt_amount("Enter expense amount (₹)")

    # 3. Category (select from list or create new)
    available_cats = get_all_categories(expenses, custom_categories)
    selected_cat = choose_or_create_category(available_cats)
    if custom_categories is not None and selected_cat not in DEFAULT_CATEGORIES:
        custom_categories.add(selected_cat)

    # 4. Description (non-empty string)
    expense_desc = prompt_non_empty_string("Enter description / note", permit_empty=False)

    # Generate unique ID and build record
    new_id = compute_next_id(expenses)
    new_record = {
        "id": new_id,
        "date": expense_date,
        "amount": expense_amount,
        "category": selected_cat,
        "description": expense_desc,
    }

    expenses.append(new_record)

    if save_expenses(expenses):
        print(f"\n[OK] Expense ID #{new_id} recorded successfully!")
        print_formatted_grid(
            headers=["ID", "Date", "Amount", "Category", "Description"],
            rows=[[str(new_id), expense_date, format_inr(expense_amount), selected_cat, expense_desc]],
            column_alignments=["^", "^", ">", "<", "<"],
        )

        # Check for immediate budget threshold warnings/alerts
        month_key = expense_date[:7]
        _evaluate_instant_budget_alert(expenses, budgets, month_key, selected_cat)
    else:
        print("\n[!] Error: Failed to save expense record to storage.")

    return expenses


def _evaluate_instant_budget_alert(
    expenses: list[dict[str, Any]],
    budgets: dict[str, Any],
    month_key: str,
    category: str
) -> None:
    """Evaluate and print immediate budget alerts upon recording an expense."""
    month_info = budgets.get(month_key)
    if not month_info:
        return

    # Check overall monthly spending
    total_budget = float(month_info.get("total_budget", 0.0))
    if total_budget > 0:
        total_spent = sum(
            float(rec.get("amount", 0.0))
            for rec in expenses
            if str(rec.get("date", "")).startswith(month_key)
        )
        utilization = (total_spent / total_budget) * 100.0
        if utilization > 100.0:
            excess = total_spent - total_budget
            print(f"\n>>> [BUDGET ALERT] Overall budget for {month_key} EXCEEDED by {format_inr(excess)} ({utilization:.1f}%)!")
            print(f"    Total Spent: {format_inr(total_spent)} / Budget: {format_inr(total_budget)}")
        elif utilization >= 80.0:
            leftover = total_budget - total_spent
            print(f"\n>>> [BUDGET WARNING] Overall budget for {month_key} reached {utilization:.1f}% ({format_inr(leftover)} remaining).")
            print(f"    Total Spent: {format_inr(total_spent)} / Budget: {format_inr(total_budget)}")

    # Check category spending if configured
    cat_budgets = month_info.get("category_budgets", {})
    if category in cat_budgets and float(cat_budgets[category]) > 0:
        c_budget = float(cat_budgets[category])
        c_spent = sum(
            float(rec.get("amount", 0.0))
            for rec in expenses
            if str(rec.get("date", "")).startswith(month_key) and rec.get("category") == category
        )
        c_utilization = (c_spent / c_budget) * 100.0
        if c_utilization > 100.0:
            c_excess = c_spent - c_budget
            print(f">>> [CATEGORY ALERT] Budget for '{category}' in {month_key} EXCEEDED by {format_inr(c_excess)} ({c_utilization:.1f}%)!")
        elif c_utilization >= 80.0:
            c_leftover = c_budget - c_spent
            print(f">>> [CATEGORY WARNING] Budget for '{category}' in {month_key} reached {c_utilization:.1f}% ({format_inr(c_leftover)} remaining).")


def view_expenses_table(
    expenses: list[dict[str, Any]],
    title: str = "ALL RECORDED EXPENSES"
) -> None:
    """
    Render a clean ASCII table of expenses with count and total spend.

    Args:
        expenses: List of expense dictionaries.
        title: Table header title.
    """
    print("\n" + "=" * 70)
    print(title.center(70))
    print("=" * 70)

    if not expenses:
        print("\n  No expense records found.\n")
        return

    headers = ["ID", "Date", "Amount", "Category", "Description"]
    rows = []
    total_spending = 0.0

    for rec in expenses:
        amt = float(rec.get("amount", 0.0))
        total_spending += amt
        rows.append([
            str(rec.get("id", "")),
            str(rec.get("date", "")),
            format_inr(amt),
            str(rec.get("category", "")),
            str(rec.get("description", "")),
        ])

    print_formatted_grid(headers, rows, column_alignments=["^", "^", ">", "<", "<"])
    print(f" Total Records: {len(expenses)} | Total Spending: {format_inr(total_spending)}\n")


def view_all_expenses_flow(
    expenses: list[dict[str, Any]],
    custom_categories: set[str] | None = None
) -> None:
    """
    Menu option 2 flow: Displays all expenses in an aligned table,
    plus an optional quick action to filter and view by category.

    Args:
        expenses: List of expense dictionaries.
        custom_categories: Optional set of custom categories.
    """
    view_expenses_table(expenses, title="ALL RECORDED EXPENSES")

    if not expenses:
        return

    print("Quick Actions:")
    print("  [Enter] Return to Main Menu")
    print("  [C]     View Expenses by Specific Category")
    quick_act = input("Enter choice: ").strip().lower()

    if quick_act == "c":
        all_cats = get_all_categories(expenses, custom_categories)
        print("\nSelect Category to View:")
        for idx, cat_name in enumerate(all_cats, start=1):
            print(f"  [{idx}] {cat_name}")
        choice_key = prompt_menu_choice("Select category number: ", [str(i) for i in range(1, len(all_cats) + 1)])
        chosen = all_cats[int(choice_key) - 1]
        matches = filter_by_category(expenses, chosen)
        view_expenses_table(matches, title=f"EXPENSES IN CATEGORY: {chosen.upper()}")


def edit_expense_flow(
    expenses: list[dict[str, Any]],
    custom_categories: set[str] | None = None
) -> list[dict[str, Any]]:
    """
    Interactive flow to edit an existing expense record by ID.
    Allows user to press Enter on any field to keep the current value.

    Args:
        expenses: List of expense dictionaries.
        custom_categories: Set of custom categories.

    Returns:
        Updated list of expenses.
    """
    print("\n" + "=" * 55)
    print("                   EDIT EXPENSE")
    print("=" * 55)

    if not expenses:
        print("  No expense records available to edit.")
        return expenses

    while True:
        id_str = input("Enter Expense ID to edit (or 'c' to cancel): ").strip()
        if id_str.lower() == "c":
            return expenses

        try:
            target_id = int(id_str)
            break
        except ValueError:
            print("  [!] Please enter a valid numerical ID.")

    target_rec = next((r for r in expenses if r.get("id") == target_id), None)
    if not target_rec:
        print(f"  [!] Expense with ID #{target_id} not found.")
        return expenses

    print("\nCurrent Record Details:")
    print_formatted_grid(
        headers=["ID", "Date", "Amount", "Category", "Description"],
        rows=[[
            str(target_rec.get("id")),
            str(target_rec.get("date", "")),
            format_inr(float(target_rec.get("amount", 0.0))),
            str(target_rec.get("category", "")),
            str(target_rec.get("description", "")),
        ]],
        column_alignments=["^", "^", ">", "<", "<"],
    )
    print("Press Enter to keep current value, or type a new value:\n")

    # 1. Date
    new_date = prompt_date_ymd("Enter new date (YYYY-MM-DD)", fallback_date=target_rec.get("date"))

    # 2. Amount
    new_amount = prompt_amount("Enter new amount (₹)", default_val=float(target_rec.get("amount", 0.0)))

    # 3. Category
    current_category = str(target_rec.get("category", "Other"))
    print(f"\nCurrent category is: '{current_category}'")
    modify_cat = prompt_yes_no("Do you want to change the category?", default_no=True)
    if modify_cat:
        available_cats = get_all_categories(expenses, custom_categories)
        new_category = choose_or_create_category(available_cats)
        if custom_categories is not None and new_category not in DEFAULT_CATEGORIES:
            custom_categories.add(new_category)
    else:
        new_category = current_category

    # 4. Description
    new_desc = prompt_non_empty_string("Enter new description", default_text=target_rec.get("description"))

    # Apply updates
    target_rec["date"] = new_date
    target_rec["amount"] = new_amount
    target_rec["category"] = new_category
    target_rec["description"] = new_desc

    if save_expenses(expenses):
        print(f"\n[OK] Expense ID #{target_id} updated successfully!")
        print_formatted_grid(
            headers=["ID", "Date", "Amount", "Category", "Description"],
            rows=[[str(target_id), new_date, format_inr(new_amount), new_category, new_desc]],
            column_alignments=["^", "^", ">", "<", "<"],
        )
    else:
        print("\n[!] Failed to save updated expense to storage.")

    return expenses


def delete_expense_flow(expenses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Prompt user to delete an existing expense record by ID after confirmation.

    Args:
        expenses: List of expense dictionaries.

    Returns:
        Updated list of expenses.
    """
    print("\n" + "=" * 55)
    print("                  DELETE EXPENSE")
    print("=" * 55)

    if not expenses:
        print("  No expense records available to delete.")
        return expenses

    while True:
        id_str = input("Enter Expense ID to delete (or 'c' to cancel): ").strip()
        if id_str.lower() == "c":
            return expenses

        try:
            target_id = int(id_str)
            break
        except ValueError:
            print("  [!] Please enter a valid numerical ID.")

    target_rec = next((r for r in expenses if r.get("id") == target_id), None)
    if not target_rec:
        print(f"  [!] Expense with ID #{target_id} not found.")
        return expenses

    print("\nTarget Expense to Delete:")
    print_formatted_grid(
        headers=["ID", "Date", "Amount", "Category", "Description"],
        rows=[[
            str(target_rec.get("id")),
            str(target_rec.get("date", "")),
            format_inr(float(target_rec.get("amount", 0.0))),
            str(target_rec.get("category", "")),
            str(target_rec.get("description", "")),
        ]],
        column_alignments=["^", "^", ">", "<", "<"],
    )

    confirm_del = prompt_yes_no(f"Are you sure you want to permanently delete Expense #{target_id}?", default_no=True)
    if confirm_del:
        expenses.remove(target_rec)
        if save_expenses(expenses):
            print(f"\n[OK] Expense #{target_id} deleted successfully.")
        else:
            print("\n[!] Failed to save changes after deletion.")
    else:
        print("\n[i] Deletion canceled by user.")

    return expenses


# ---------------------------------------------------------------------------
# Search, Filtering, and Sorting Helpers
# ---------------------------------------------------------------------------

def filter_by_keyword(expenses: list[dict[str, Any]], query_keyword: str) -> list[dict[str, Any]]:
    """Filter expenses whose description contains the keyword (case-insensitive)."""
    term = query_keyword.strip().lower()
    return [r for r in expenses if term in str(r.get("description", "")).lower()]


def filter_by_category(expenses: list[dict[str, Any]], category_name: str) -> list[dict[str, Any]]:
    """Filter expenses matching a specific category (case-insensitive)."""
    return [r for r in expenses if str(r.get("category", "")).lower() == category_name.lower()]


def filter_by_date_range(
    expenses: list[dict[str, Any]],
    start_ymd: str,
    end_ymd: str
) -> list[dict[str, Any]]:
    """Filter expenses within start and end calendar dates (inclusive)."""
    return [r for r in expenses if start_ymd <= str(r.get("date", "")) <= end_ymd]


def filter_by_month(expenses: list[dict[str, Any]], month_ym: str) -> list[dict[str, Any]]:
    """Filter expenses belonging to a specific month (YYYY-MM)."""
    return [r for r in expenses if str(r.get("date", "")).startswith(month_ym)]


def filter_by_amount_range(
    expenses: list[dict[str, Any]],
    min_amount: float,
    max_amount: float
) -> list[dict[str, Any]]:
    """Filter expenses whose amount is between min_amount and max_amount (inclusive)."""
    return [r for r in expenses if min_amount <= float(r.get("amount", 0.0)) <= max_amount]


def sort_expenses(
    expenses: list[dict[str, Any]],
    sort_attribute: str = "date",
    descending: bool = False
) -> list[dict[str, Any]]:
    """
    Sort expense records by date or amount.

    Args:
        expenses: List of expenses to sort.
        sort_attribute: 'date' or 'amount'.
        descending: If True, sorts highest/newest first.

    Returns:
        New sorted list of expenses.
    """
    if sort_attribute == "amount":
        return sorted(expenses, key=lambda x: float(x.get("amount", 0.0)), reverse=descending)
    return sorted(expenses, key=lambda x: (str(x.get("date", "")), int(x.get("id", 0))), reverse=descending)


def search_and_filter_flow(
    expenses: list[dict[str, Any]],
    custom_categories: set[str] | None = None
) -> None:
    """
    Menu option 8 flow: Interactive menu for searching, filtering, and sorting expenses.

    Args:
        expenses: List of expense dictionaries.
        custom_categories: Set of custom categories.
    """
    while True:
        print("\n" + "=" * 55)
        print("              SEARCH & FILTER EXPENSES")
        print("=" * 55)
        print("  [1] Search Description by Keyword")
        print("  [2] Filter by Category")
        print("  [3] Filter by Date Range (Start Date - End Date)")
        print("  [4] Filter by Month (YYYY-MM)")
        print("  [5] Filter by Amount Range (Min - Max ₹)")
        print("  [6] Sort All Expenses (Date or Amount)")
        print("  [0] Return to Main Menu")
        print("=" * 55)

        opt = prompt_menu_choice("Enter choice [0-6]: ", ["0", "1", "2", "3", "4", "5", "6"])

        if opt == "0":
            break

        elif opt == "1":
            search_term = prompt_non_empty_string("Enter search keyword").strip()
            matches = filter_by_keyword(expenses, search_term)
            view_expenses_table(matches, title=f"SEARCH RESULTS FOR: '{search_term.upper()}'")

        elif opt == "2":
            cats = get_all_categories(expenses, custom_categories)
            if not cats:
                print("  No categories available.")
                continue
            print("\nSelect Category:")
            for idx, c in enumerate(cats, start=1):
                print(f"  [{idx}] {c}")
            choice_num = int(prompt_menu_choice("Choose category: ", [str(i) for i in range(1, len(cats) + 1)]))
            selected = cats[choice_num - 1]
            matches = filter_by_category(expenses, selected)
            view_expenses_table(matches, title=f"EXPENSES IN CATEGORY: {selected.upper()}")

        elif opt == "3":
            print("\nEnter Date Range Boundaries:")
            s_date = prompt_date_ymd("Enter start date (YYYY-MM-DD)", default_today=False)
            e_date = prompt_date_ymd("Enter end date (YYYY-MM-DD)", default_today=True)
            if s_date > e_date:
                print("  [!] Notice: Start date was after end date. Dates swapped automatically.")
                s_date, e_date = e_date, s_date
            matches = filter_by_date_range(expenses, s_date, e_date)
            view_expenses_table(matches, title=f"EXPENSES FROM {s_date} TO {e_date}")

        elif opt == "4":
            m_str = prompt_month_ym("Enter month (YYYY-MM)")
            matches = filter_by_month(expenses, m_str)
            view_expenses_table(matches, title=f"EXPENSES FOR MONTH: {m_str}")

        elif opt == "5":
            print("\nEnter Amount Range Boundaries:")
            min_a = prompt_amount("Enter minimum amount (₹)", permit_zero=True, default_val=0.0)
            max_a = prompt_amount("Enter maximum amount (₹)", permit_zero=False)
            if min_a > max_a:
                print("  [!] Notice: Minimum was greater than maximum. Amounts swapped automatically.")
                min_a, max_a = max_a, min_a
            matches = filter_by_amount_range(expenses, min_a, max_a)
            view_expenses_table(matches, title=f"EXPENSES BETWEEN {format_inr(min_a)} AND {format_inr(max_a)}")

        elif opt == "6":
            print("\nSort by:")
            print("  [1] Date (Newest first)")
            print("  [2] Date (Oldest first)")
            print("  [3] Amount (Highest first)")
            print("  [4] Amount (Lowest first)")
            sort_choice = prompt_menu_choice("Choose sort option [1-4]: ", ["1", "2", "3", "4"])
            if sort_choice == "1":
                sorted_res = sort_expenses(expenses, sort_attribute="date", descending=True)
                view_expenses_table(sorted_res, title="EXPENSES SORTED BY DATE (NEWEST FIRST)")
            elif sort_choice == "2":
                sorted_res = sort_expenses(expenses, sort_attribute="date", descending=False)
                view_expenses_table(sorted_res, title="EXPENSES SORTED BY DATE (OLDEST FIRST)")
            elif sort_choice == "3":
                sorted_res = sort_expenses(expenses, sort_attribute="amount", descending=True)
                view_expenses_table(sorted_res, title="EXPENSES SORTED BY AMOUNT (HIGHEST FIRST)")
            elif sort_choice == "4":
                sorted_res = sort_expenses(expenses, sort_attribute="amount", descending=False)
                view_expenses_table(sorted_res, title="EXPENSES SORTED BY AMOUNT (LOWEST FIRST)")
