"""
Personal Expense & Budget Tracker.

Main CLI Entry Point providing an interactive menu-driven interface to track expenses,
manage category and monthly budgets, generate spending reports, and export to CSV.
"""

from pathlib import Path
import sys

from budget_manager import (
    check_budget_status_flow,
    set_monthly_budget_flow,
)
from expense_manager import (
    DEFAULT_CATEGORIES,
    add_expense_flow,
    delete_expense_flow,
    edit_expense_flow,
    search_and_filter_flow,
    view_all_expenses_flow,
)
from reports import spending_summary_flow
from storage import (
    BUDGETS_FILE,
    DEFAULT_EXPORT_CSV,
    EXPENSES_FILE,
    export_expenses_to_csv,
    load_budgets,
    load_expenses,
)
from utils import (
    pause_terminal,
    prompt_menu_choice,
    prompt_yes_no,
)

# Ensure proper UTF-8 console output for currency symbol (₹) on Windows systems
if sys.platform == "win32":
    try:
        if sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr.encoding.lower() != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def display_welcome_banner() -> None:
    """Print the welcome header banner."""
    print("=" * 65)
    print("       PERSONAL EXPENSE & BUDGET TRACKER")
    print("       Take control of your finances, one rupee at a time")
    print("=" * 65)


def display_main_menu() -> None:
    """Display the primary CLI options."""
    print("\n" + "=" * 45)
    print("                 MAIN MENU")
    print("=" * 45)
    print("  [1]  Add Expense")
    print("  [2]  View All Expenses")
    print("  [3]  Edit Expense")
    print("  [4]  Delete Expense")
    print("  [5]  Set Monthly Budget")
    print("  [6]  Check Budget Status")
    print("  [7]  Spending Summary")
    print("  [8]  Search / Filter Expenses")
    print("  [9]  Export to CSV")
    print("  [10] Exit")
    print("=" * 45)


def export_csv_flow(expenses: list[dict]) -> None:
    """
    Prompt user and export expenses to a CSV file.

    Args:
        expenses: Current list of expenses.
    """
    print("\n" + "=" * 50)
    print("              EXPORT TO CSV")
    print("=" * 50)

    if not expenses:
        print("  [!] No expenses to export.")
        return

    default_path = DEFAULT_EXPORT_CSV
    default_str = f"data/{default_path.name}"

    filename_input = input(f"Enter destination filename or path [default: {default_str}]: ").strip()
    target_path = Path(filename_input) if filename_input else default_path

    if export_expenses_to_csv(expenses, target_path):
        print(f"\n[OK] Successfully exported {len(expenses)} expenses to:")
        print(f"     {target_path.resolve()}")
    else:
        print("\n[!] Failed to export to CSV.")


def main() -> None:
    """Main application loop."""
    display_welcome_banner()

    # Load persistent data from JSON storage
    expenses = load_expenses(EXPENSES_FILE)
    budgets = load_budgets(BUDGETS_FILE)

    # Initialize custom categories from existing data
    custom_categories: set[str] = set()
    for exp in expenses:
        cat = exp.get("category")
        if cat and cat not in DEFAULT_CATEGORIES:
            custom_categories.add(str(cat))

    print(f"\nLoaded {len(expenses)} expenses and {len(budgets)} monthly budget configurations.")

    menu_choices = [str(i) for i in range(1, 11)]

    while True:
        try:
            display_main_menu()
            choice = prompt_menu_choice("Select an option [1-10]: ", menu_choices)

            if choice == "1":
                expenses = add_expense_flow(expenses, budgets, custom_categories)
                pause_terminal()

            elif choice == "2":
                view_all_expenses_flow(expenses, custom_categories)
                pause_terminal()

            elif choice == "3":
                expenses = edit_expense_flow(expenses, custom_categories)
                pause_terminal()

            elif choice == "4":
                expenses = delete_expense_flow(expenses)
                pause_terminal()

            elif choice == "5":
                budgets = set_monthly_budget_flow(budgets, expenses, custom_categories)

            elif choice == "6":
                check_budget_status_flow(budgets, expenses)
                pause_terminal()

            elif choice == "7":
                spending_summary_flow(expenses)

            elif choice == "8":
                search_and_filter_flow(expenses, custom_categories)

            elif choice == "9":
                export_csv_flow(expenses)
                pause_terminal()

            elif choice == "10":
                confirm_exit = prompt_yes_no("Are you sure you want to exit?", default_no=False)
                if confirm_exit:
                    print("\nThank you for using Personal Expense & Budget Tracker. Goodbye!\n")
                    sys.exit(0)

        except KeyboardInterrupt:
            print("\n\nOperation interrupted by user.")
            if prompt_yes_no("Exit application?", default_no=True):
                print("Goodbye!")
                sys.exit(0)
        except Exception as err:
            print(f"\n[!] Unexpected error encountered: {err}")
            pause_terminal("Press Enter to continue...")


if __name__ == "__main__":
    main()
