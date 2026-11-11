"""
Persistent Storage Module for Personal Expense & Budget Tracker.

Handles JSON persistence for expenses and monthly budgets, provides atomic writes,
manages automated corrupted file quarantining and recovery, and supports CSV export.
"""

import csv
from datetime import datetime
import json
import os
from pathlib import Path
from typing import Any

# Default filesystem paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPENSES_FILE = DATA_DIR / "expenses.json"
BUDGETS_FILE = DATA_DIR / "budgets.json"
SAMPLE_CSV_FILE = DATA_DIR / "sample_expenses.csv"
DEFAULT_EXPORT_CSV = DATA_DIR / "expenses_export.csv"


def ensure_storage_ready(target_directory: Path = DATA_DIR) -> None:
    """
    Ensure the target data storage directory exists on the filesystem.

    Args:
        target_directory: Path to the target directory.
    """
    target_directory.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Expenses Storage (JSON)
# ---------------------------------------------------------------------------

def load_expenses(file_path: Path = EXPENSES_FILE) -> list[dict[str, Any]]:
    """
    Load expense records from the JSON storage file.

    Recovers gracefully if the file is missing or contains invalid/corrupted JSON.
    Corrupted files are backed up safely with a timestamp before initializing an empty list.

    Args:
        file_path: Path to the expenses JSON file.

    Returns:
        List of expense dictionaries.
    """
    ensure_storage_ready(file_path.parent)

    if not file_path.exists():
        return []

    try:
        with open(file_path, mode="r", encoding="utf-8") as json_stream:
            records = json.load(json_stream)
            if isinstance(records, list):
                return records
            print(f"  [!] Storage Warning: {file_path.name} does not contain a list. Resetting gracefully.")
            _quarantine_corrupt_file(file_path)
            return []
    except json.JSONDecodeError as decode_error:
        print(f"  [!] Storage Warning: Corrupted JSON detected in {file_path.name} ({decode_error}).")
        _quarantine_corrupt_file(file_path)
        return []
    except OSError as sys_err:
        print(f"  [!] Storage Error: Unable to read {file_path.name}: {sys_err}")
        return []


def save_expenses(expenses: list[dict[str, Any]], file_path: Path = EXPENSES_FILE) -> bool:
    """
    Persist the list of expenses to the JSON storage file.

    Uses an atomic write pattern (writes to a temporary file, then renames)
    to protect against corrupted data if the process is terminated mid-write.

    Args:
        expenses: List of expense dictionaries.
        file_path: Destination JSON file path.

    Returns:
        True if successfully saved, False otherwise.
    """
    ensure_storage_ready(file_path.parent)
    temp_path = file_path.with_suffix(".tmp")
    try:
        with open(temp_path, mode="w", encoding="utf-8") as json_stream:
            json.dump(expenses, json_stream, indent=2, ensure_ascii=False)
        temp_path.replace(file_path)
        return True
    except OSError as sys_err:
        print(f"  [!] Storage Error: Unable to save expenses to {file_path.name}: {sys_err}")
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        return False


# ---------------------------------------------------------------------------
# Budgets Storage (JSON)
# ---------------------------------------------------------------------------

def load_budgets(file_path: Path = BUDGETS_FILE) -> dict[str, Any]:
    """
    Load monthly budget configurations from the JSON storage file.

    Data format:
    {
        "YYYY-MM": {
            "total_budget": float,
            "category_budgets": {
                "CategoryName": float
            }
        }
    }

    Args:
        file_path: Path to the budgets JSON file.

    Returns:
        Dictionary mapping month keys to budget configurations.
    """
    ensure_storage_ready(file_path.parent)

    if not file_path.exists():
        return {}

    try:
        with open(file_path, mode="r", encoding="utf-8") as json_stream:
            budget_data = json.load(json_stream)
            if isinstance(budget_data, dict):
                return budget_data
            print(f"  [!] Storage Warning: {file_path.name} does not contain a dictionary. Resetting gracefully.")
            _quarantine_corrupt_file(file_path)
            return {}
    except json.JSONDecodeError as decode_error:
        print(f"  [!] Storage Warning: Corrupted JSON detected in {file_path.name} ({decode_error}).")
        _quarantine_corrupt_file(file_path)
        return []
    except OSError as sys_err:
        print(f"  [!] Storage Error: Unable to read {file_path.name}: {sys_err}")
        return []


def save_budgets(budgets: dict[str, Any], file_path: Path = BUDGETS_FILE) -> bool:
    """
    Persist the monthly budget configurations to the JSON storage file.

    Uses an atomic write pattern (writes to temporary file, then renames).

    Args:
        budgets: Budget dictionary.
        file_path: Destination JSON file path.

    Returns:
        True if successfully saved, False otherwise.
    """
    ensure_storage_ready(file_path.parent)
    temp_path = file_path.with_suffix(".tmp")
    try:
        with open(temp_path, mode="w", encoding="utf-8") as json_stream:
            json.dump(budgets, json_stream, indent=2, ensure_ascii=False)
        temp_path.replace(file_path)
        return True
    except OSError as sys_err:
        print(f"  [!] Storage Error: Unable to save budgets to {file_path.name}: {sys_err}")
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        return False


# ---------------------------------------------------------------------------
# CSV Export
# ---------------------------------------------------------------------------

def export_expenses_to_csv(expenses: list[dict[str, Any]], export_path: Path | str) -> bool:
    """
    Export all expense records to a CSV file.

    Args:
        expenses: List of expense dictionaries.
        export_path: Destination CSV file path.

    Returns:
        True if export succeeded, False on error.
    """
    destination = Path(export_path)
    ensure_storage_ready(destination.parent)

    columns = ["ID", "Date", "Amount", "Category", "Description"]

    try:
        with open(destination, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=columns)
            writer.writeheader()
            for record in expenses:
                writer.writerow({
                    "ID": record.get("id", ""),
                    "Date": record.get("date", ""),
                    "Amount": f"{float(record.get('amount', 0.0)):.2f}",
                    "Category": record.get("category", ""),
                    "Description": record.get("description", "")
                })
        return True
    except OSError as sys_err:
        print(f"  [!] CSV Export Error: {sys_err}")
        return False


# ---------------------------------------------------------------------------
# Internal Helper
# ---------------------------------------------------------------------------

def _quarantine_corrupt_file(file_path: Path) -> None:
    """
    Rename an invalid/corrupted JSON file by appending a timestamped suffix
    so the user does not lose raw data while the app continues running safely.

    Args:
        file_path: Path to the corrupted file.
    """
    time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.with_name(f"{file_path.stem}_quarantine_{time_tag}{file_path.suffix}")
    try:
        file_path.replace(backup_path)
        print(f"  [i] Corrupted file preserved for inspection as: {backup_path.name}")
    except OSError:
        pass
