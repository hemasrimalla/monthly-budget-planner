"""
Utility and Helper Module for Personal Expense & Budget Tracker.

Provides input validation routines with defensive looping, currency formatting
with the Indian Rupee symbol (₹), visual budget meters, and ASCII table rendering.
"""

from datetime import datetime
import os
import sys


# ---------------------------------------------------------------------------
# Terminal Configuration & Formatting Helpers
# ---------------------------------------------------------------------------

def format_inr(amount: float) -> str:
    """
    Format a floating-point number into Indian Rupee currency format (₹).

    Handles positive, zero, and negative balances accurately.

    Args:
        amount: Numeric monetary value.

    Returns:
        Formatted currency string, e.g. '₹1,250.00' or '-₹500.00'.
    """
    if amount < 0:
        return f"-₹{abs(amount):,.2f}"
    return f"₹{amount:,.2f}"


def build_progress_meter(percentage: float, meter_width: int = 20) -> str:
    """
    Generate an ASCII visualization meter representing budget utilization.

    Args:
        percentage: Budget utilization percentage (e.g., 85.5).
        meter_width: Total number of character blocks in the bar.

    Returns:
        Rendered string bar, e.g., '[██████████░░░░░░░░░░] 50.0%'.
    """
    clamped_value = max(0.0, min(percentage, 100.0))
    filled_blocks = int(round(meter_width * (clamped_value / 100.0)))
    unfilled_blocks = meter_width - filled_blocks
    meter_bar = "█" * filled_blocks + "░" * unfilled_blocks
    return f"[{meter_bar}] {percentage:.1f}%"


def print_formatted_grid(
    headers: list[str],
    rows: list[list[str]],
    column_alignments: list[str] | None = None
) -> None:
    """
    Render a clean ASCII table with custom alignment and dynamic column padding.

    Args:
        headers: Column header titles.
        rows: Data rows, where each row is a list of cell strings.
        column_alignments: Optional alignment list per column:
                           '<' for left, '>' for right, '^' for center.
                           Defaults to left-alignment.
    """
    if not headers:
        return

    num_columns = len(headers)
    if column_alignments is None:
        column_alignments = ["<"] * num_columns

    # Determine maximum character width required for each column
    column_widths = [len(str(h)) for h in headers]
    for row in rows:
        for col_idx in range(min(num_columns, len(row))):
            column_widths[col_idx] = max(column_widths[col_idx], len(str(row[col_idx])))

    # Add two spaces of interior padding
    padded_widths = [w + 2 for w in column_widths]

    # Build border divider line
    divider = "+" + "+".join("-" * w for w in padded_widths) + "+"

    # Build header line
    header_segments = []
    for col_idx, header_text in enumerate(headers):
        align = column_alignments[col_idx] if col_idx < len(column_alignments) else "<"
        cell_content = f" {header_text} "
        if align == ">":
            header_segments.append(cell_content.rjust(padded_widths[col_idx]))
        elif align == "^":
            header_segments.append(cell_content.center(padded_widths[col_idx]))
        else:
            header_segments.append(cell_content.ljust(padded_widths[col_idx]))

    print(divider)
    print("|" + "|".join(header_segments) + "|")
    print(divider)

    # Empty rows handling
    if not rows:
        total_inner_span = sum(padded_widths) + num_columns - 1
        empty_note = " No records available ".center(total_inner_span)
        print(f"|{empty_note}|")
        print(divider)
        return

    # Print data rows
    for row in rows:
        row_segments = []
        for col_idx in range(num_columns):
            raw_val = str(row[col_idx]) if col_idx < len(row) else ""
            align = column_alignments[col_idx] if col_idx < len(column_alignments) else "<"
            cell_content = f" {raw_val} "
            if align == ">":
                row_segments.append(cell_content.rjust(padded_widths[col_idx]))
            elif align == "^":
                row_segments.append(cell_content.center(padded_widths[col_idx]))
            else:
                row_segments.append(cell_content.ljust(padded_widths[col_idx]))
        print("|" + "|".join(row_segments) + "|")

    print(divider)


# ---------------------------------------------------------------------------
# Input Validation Helpers (Continuous Loop Until Valid)
# ---------------------------------------------------------------------------

def prompt_amount(
    prompt_label: str = "Enter amount (₹)",
    default_val: float | None = None,
    permit_zero: bool = False
) -> float:
    """
    Prompt the user for a valid monetary amount. Loops defensively until valid.

    Args:
        prompt_label: Prompt message displayed to the user.
        default_val: Optional default float returned if user presses Enter.
        permit_zero: Whether 0.0 is permissible as a valid input.

    Returns:
        Positive float rounded to two decimal places.
    """
    while True:
        default_hint = f" [default: {format_inr(default_val)}]: " if default_val is not None else ": "
        raw_input = input(prompt_label + default_hint).strip().replace(",", "")

        if not raw_input and default_val is not None:
            return float(default_val)

        if not raw_input:
            print("  [!] Validation Error: Amount cannot be empty. Please enter a valid number.")
            continue

        try:
            numeric_val = float(raw_input)
            if numeric_val < 0:
                print("  [!] Validation Error: Amount cannot be negative. Please enter a positive value.")
                continue
            if numeric_val == 0 and not permit_zero:
                print("  [!] Validation Error: Amount must be greater than zero.")
                continue
            return round(numeric_val, 2)
        except ValueError:
            print("  [!] Validation Error: Invalid numeric format. Example: 350 or 1250.75")


def prompt_date_ymd(
    prompt_label: str = "Enter date (YYYY-MM-DD)",
    default_today: bool = True,
    fallback_date: str | None = None
) -> str:
    """
    Prompt the user for a valid calendar date in YYYY-MM-DD format.
    Loops defensively until a real calendar date is entered.

    Args:
        prompt_label: Input prompt message.
        default_today: If True and fallback_date is None, defaults to current date.
        fallback_date: Specific preset default date string.

    Returns:
        Validated date string in 'YYYY-MM-DD' format.
    """
    current_date_str = datetime.now().strftime("%Y-%m-%d")
    effective_default = fallback_date if fallback_date is not None else (current_date_str if default_today else None)

    while True:
        default_hint = f" [default: {effective_default}]: " if effective_default else ": "
        raw_input = input(prompt_label + default_hint).strip()

        if not raw_input and effective_default:
            return effective_default

        if not raw_input:
            print("  [!] Validation Error: Date field cannot be empty. Format: YYYY-MM-DD.")
            continue

        try:
            parsed_date = datetime.strptime(raw_input, "%Y-%m-%d")
            if parsed_date.year < 2000 or parsed_date.year > 2099:
                print("  [!] Validation Error: Year must be within the range 2000-2099.")
                continue
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            print("  [!] Validation Error: Invalid calendar date or format. Please use YYYY-MM-DD (e.g., 2026-11-10).")


def prompt_month_ym(
    prompt_label: str = "Enter month (YYYY-MM)",
    default_current: bool = True,
    fallback_month: str | None = None
) -> str:
    """
    Prompt the user for a valid month in YYYY-MM format. Loops defensively.

    Args:
        prompt_label: Input prompt message.
        default_current: If True and fallback_month is None, defaults to current month.
        fallback_month: Specific preset default month string.

    Returns:
        Validated month string in 'YYYY-MM' format.
    """
    current_month_str = datetime.now().strftime("%Y-%m")
    effective_default = fallback_month if fallback_month is not None else (current_month_str if default_current else None)

    while True:
        default_hint = f" [default: {effective_default}]: " if effective_default else ": "
        raw_input = input(prompt_label + default_hint).strip()

        if not raw_input and effective_default:
            return effective_default

        if not raw_input:
            print("  [!] Validation Error: Month cannot be empty. Format: YYYY-MM.")
            continue

        try:
            parsed_month = datetime.strptime(raw_input, "%Y-%m")
            if parsed_month.year < 2000 or parsed_month.year > 2099:
                print("  [!] Validation Error: Year must be within the range 2000-2099.")
                continue
            return parsed_month.strftime("%Y-%m")
        except ValueError:
            print("  [!] Validation Error: Invalid month format. Please use YYYY-MM (e.g., 2026-11).")


def prompt_non_empty_string(
    prompt_label: str,
    default_text: str | None = None,
    permit_empty: bool = False
) -> str:
    """
    Prompt the user for text input. Loops until non-empty input or default is provided.

    Args:
        prompt_label: Display prompt.
        default_text: Text returned if user presses Enter without typing.
        permit_empty: If True, empty strings are allowed.

    Returns:
        Sanitized string.
    """
    while True:
        default_hint = f" [default: {default_text}]: " if default_text is not None else ": "
        raw_input = input(prompt_label + default_hint).strip()

        if not raw_input and default_text is not None:
            return default_text

        if not raw_input and not permit_empty:
            print("  [!] Validation Error: Input cannot be empty. Please enter text.")
            continue

        return raw_input


def prompt_menu_choice(prompt_label: str, valid_options: list[str] | set[str]) -> str:
    """
    Prompt the user until they input an option present in valid_options.

    Args:
        prompt_label: Input message.
        valid_options: Collection of allowable choices.

    Returns:
        Selected option string in lowercase.
    """
    allowed_set = {str(opt).strip().lower() for opt in valid_options}
    while True:
        user_choice = input(prompt_label).strip().lower()
        if user_choice in allowed_set:
            return user_choice
        print(f"  [!] Invalid choice. Please choose from: {', '.join(sorted(valid_options))}")


def prompt_yes_no(prompt_label: str = "Are you sure? (y/n)", default_no: bool = True) -> bool:
    """
    Prompt the user for a binary yes/no decision. Loops until 'y' or 'n'.

    Args:
        prompt_label: Question prompt.
        default_no: If True, hitting Enter defaults to No.

    Returns:
        True if confirmed (y/yes), False if declined (n/no).
    """
    default_hint = " [y/N]: " if default_no else " [Y/n]: "
    while True:
        choice = input(prompt_label + default_hint).strip().lower()
        if not choice:
            return not default_no
        if choice in ("y", "yes"):
            return True
        elif choice in ("n", "no"):
            return False
        print("  [!] Please enter 'y' for yes or 'n' for no.")


def pause_terminal(message: str = "\nPress Enter to return to main menu...") -> None:
    """Pause execution until the user presses Enter."""
    try:
        input(message)
    except (KeyboardInterrupt, EOFError):
        pass
