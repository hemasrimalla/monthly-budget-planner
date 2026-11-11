# Personal Expense & Budget Tracker

A complete, beginner-friendly, and robust menu-driven Python CLI application designed for a Python internship project. It enables users to record daily expenses, organize them into standard and custom categories, set monthly and category-wise budgets with smart visual alerts, analyze spending habits with neat tabular summaries, and export data to CSV.

---

## Table of Contents
- [Project Description](#project-description)
- [Key Features](#key-features)
- [Tech Stack & Requirements](#tech-stack--requirements)
- [Project Structure](#project-structure)
- [Installation & How to Run](#installation--how-to-run)
- [Menu Overview](#menu-overview)
- [Feature Details & Usage Walkthrough](#feature-details--usage-walkthrough)
- [Data Storage & Sample Files](#data-storage--sample-files)
- [Error Handling & Edge Cases](#error-handling--edge-cases)
- [Code Quality & Standards](#code-quality--standards)

---

## Project Description

Managing personal finances is a critical daily necessity. The **Personal Expense & Budget Tracker** provides an intuitive, modular terminal interface to track where money goes, maintain financial discipline through monthly budgets, and visualize spending distributions.

Built purely using Python standard library modules with zero external dependencies, it exemplifies core computer science and Python concepts:
- **Modular Architecture**: Clean separation of concerns across input validation, storage, expense management, budgeting, reporting, and CLI flow.
- **Data Structures**: Effective use of dictionaries, lists, sets, and tuples for in-memory manipulation and filtering.
- **Robust Persistence**: Atomic file writes for JSON serialization, corrupted file auto-recovery with timestamped backups, and RFC 4180-compliant CSV export.
- **Defensive Programming**: Comprehensive exception handling (`ValueError`, `OSError`, `json.JSONDecodeError`, `KeyboardInterrupt`) ensuring the application never crashes on invalid input.
- **Professional Formatting**: ASCII table rendering, UTF-8 Indian Rupee (`₹`) currency formatting, and dynamic ASCII progress bars.

---

## Key Features

1. **Expense Tracking (CRUD Operations)**:
   - **Add Expense**: Assigns an auto-incrementing unique integer ID, date (defaults to today `YYYY-MM-DD`), positive amount, category, and description.
   - **View All Expenses**: Displays all recorded transactions in a neat ASCII table with total counts and sum spent. Includes a quick action to view by a specific category.
   - **Edit Expense**: Update date, amount, category, or note for any expense by ID. Press Enter to keep the existing value.
   - **Delete Expense**: Remove an expense by ID with confirmation prompt (`y/n`).

2. **Category-wise Management**:
   - **Default Categories**: `Food`, `Transport`, `Shopping`, `Bills`, `Entertainment`, `Health`, `Education`, and `Other`.
   - **Custom Categories**: Users can dynamically define custom categories (e.g., `Rent`, `Gym`, `Investment`) on the fly when adding/editing expenses or filtering.
   - **View by Category**: Filter and aggregate expenses by any category.

3. **Monthly Budgeting & Smart Thresholds**:
   - **Flexible Budgets**: Set an overall monthly budget and optional category-specific budgets for any month (`YYYY-MM`).
   - **Visual Progress Bar**: Terminal-rendered ASCII progress bar showing utilization percentage (e.g., `[█████████████████░░░] 86.7%`).
   - **80% Warning**: Triggers a clear warning message when total or category spending reaches 80% to 100% of the allocated budget.
   - **100% Exceeded Alert**: Displays a high-visibility alert when spending crosses 100%, reporting the exact overage amount.
   - **Instant Alerts**: Automatically checks and prints budget warnings immediately when a new expense is logged.

4. **Spending Reports & Analytics**:
   - **Monthly Summary**: High-level report showing total spend, transaction count, average per transaction, calendar-aware average daily spend, highest and lowest spending categories, and the single largest transaction.
   - **Distribution Chart**: Category breakdown table with percentage share and horizontal ASCII bars (`████░░░░░░`).
   - **Month-over-Month Comparison**: Chronological tracking across all recorded months showing spending trends and MoM percentage changes.
   - **All-Time Breakdown**: Cumulative category analysis over the entire transaction history.

5. **Search, Filtering, and Sorting**:
   - **Keyword Search**: Case-insensitive substring search in expense descriptions.
   - **Filter by Category**: View all items matching a selected category.
   - **Filter by Date Range**: View records between start and end dates (`YYYY-MM-DD`).
   - **Filter by Month**: Quick filter for any specific month (`YYYY-MM`).
   - **Filter by Amount Range**: View expenses within custom minimum and maximum thresholds.
   - **Multi-directional Sorting**: Sort by date (newest/oldest) or by amount (highest/lowest).

6. **Data Storage & CSV Export**:
   - Auto-saves changes after every addition, edit, or deletion.
   - Auto-creates data folders and missing JSON files.
   - Gracefully handles corrupted JSON by preserving a backup and resetting cleanly.
   - Exports all expenses to CSV format (`data/expenses_export.csv` or user-defined destination).

---

## Tech Stack & Requirements

- **Python Version**: Python 3.10+ (tested on Python 3.14)
- **Standard Library Modules Only**:
  - `csv`: Reading and writing tabular CSV export files.
  - `json`: Persistent storage and parsing of expenses and budgets.
  - `datetime`: Date manipulation, validation, and defaults.
  - `calendar`: Days-in-month calculations for calendar-aware daily averages.
  - `os` & `pathlib`: Cross-platform filesystem navigation and atomic file operations.
  - `sys`: Terminal encoding reconfiguration and exit status codes.
- **External Dependencies**: None (Zero `pip install` required).

---

## Project Structure

```
expense-budget-tracker/
├── main.py              # CLI entry point, welcome banner, and main menu routing
├── expense_manager.py   # Expense CRUD, category handling, searching, filtering, and sorting
├── budget_manager.py    # Monthly/category budget calculations, thresholds & alerts
├── storage.py           # Atomic JSON persistence, corruption recovery & CSV export
├── reports.py           # Monthly summaries, daily averages, MoM comparisons, and charts
├── utils.py             # Robust input validators (amount, date, month, string), table formatting
├── data/
│   ├── expenses.json    # JSON storage containing sample expenses across 3 months
│   ├── budgets.json     # JSON storage containing configured monthly and category budgets
│   ├── sample_expenses.csv # Reference CSV dataset with 25 pre-seeded transactions
│   └── expenses_export.csv # Default target file for CSV exports
├── sample_output/
│   ├── cli_session_walkthrough.txt  # Complete terminal walkthrough of a user session
│   ├── budget_report_sample.txt     # Sample budget status outputs (OK, Warning, Exceeded)
│   └── spending_report_sample.txt   # Sample monthly summary and comparison reports
├── README.md            # Comprehensive project documentation
└── .gitignore           # Git ignore rules for Python bytecode and temporary files
```

---

## Installation & How to Run

### 1. Prerequisites
Ensure Python 3.10 or higher is installed:
```bash
python --version
```

### 2. Navigate to Project Directory
```bash
cd expense-budget-tracker
```

### 3. Launch the Application
```bash
python main.py
```

The application automatically loads the pre-seeded sample dataset from `data/expenses.json` and `data/budgets.json`, allowing instant testing of all 10 menu options.

---

## Menu Overview

Upon launching, the interactive menu presents 10 clearly organized choices:

```text
=================================================================
       PERSONAL EXPENSE & BUDGET TRACKER
       Take control of your finances, one rupee at a time
=================================================================

Loaded 25 expenses and 3 monthly budget configurations.

=============================================
                 MAIN MENU
=============================================
  [1]  Add Expense
  [2]  View All Expenses
  [3]  Edit Expense
  [4]  Delete Expense
  [5]  Set Monthly Budget
  [6]  Check Budget Status
  [7]  Spending Summary
  [8]  Search / Filter Expenses
  [9]  Export to CSV
  [10] Exit
=============================================
Select an option [1-10]: 
```

---

## Feature Details & Usage Walkthrough

### 1. Add Expense
Prompts for date (press Enter for today's date), amount in ₹ (must be positive), category (from default list or custom), and description. If a monthly budget exists for that month, it immediately alerts the user if spending crosses 80% or 100%.

```text
Enter expense date (YYYY-MM-DD) [default: 2026-11-11]: 2026-11-11
Enter expense amount (₹): 1200.00

--- Select Expense Category ---
  [1] Food
  [2] Transport
  [3] Shopping
  [4] Bills
  [5] Entertainment
  [6] Health
  [7] Education
  [8] Other
  [9] + Add New Custom Category
Select category number: 1
Enter description / note: Weekly organic vegetables
[OK] Expense ID #26 recorded successfully!
```

### 2. View All Expenses
Renders all recorded expenses in an aligned ASCII table with currency formatting:

```text
+----+------------+------------+---------------+-----------------------------------------------+
| ID | Date       |     Amount | Category      | Description                                   |
+----+------------+------------+---------------+-----------------------------------------------+
| 17 | 2026-11-01 | ₹12,000.00 | Rent          | Monthly apartment rental payment              |
| 18 | 2026-11-03 |  ₹1,650.00 | Bills         | Electricity and water utility bill            |
| 19 | 2026-11-05 |  ₹2,480.00 | Food          | Monthly supermarket grocery restock           |
| 20 | 2026-11-06 |    ₹450.00 | Transport     | Auto rickshaw fare to railway station         |
| 21 | 2026-11-07 |  ₹4,200.00 | Shopping      | Amazon Great Indian Festival - winter wear    |
| 22 | 2026-11-08 |    ₹980.00 | Health        | Prescription eye drops and medicines          |
| 23 | 2026-11-09 |  ₹3,600.00 | Education     | AWS Cloud Practitioner certification exam     |
| 24 | 2026-11-10 |  ₹2,890.00 | Food          | Weekend restaurant lunch with family          |
| 25 | 2026-11-11 |  ₹1,499.00 | Other         | GitHub Copilot annual developer subscription  |
+----+------------+------------+---------------+-----------------------------------------------+
 Total Records: 25 | Total Spending: ₹73,367.00
```

### 3. Check Budget Status
Displays total budget, total spent, remaining balance, utilization progress bar, and status badge:
- **On Track**: Spent is under 80% of budget.
- **Warning**: Spent is between 80% and 100% of budget.
- **Exceeded Alert**: Spent exceeds 100% of budget.

```text
=================================================================
                        BUDGET STATUS FOR 2026-11                
=================================================================

Total Budget : ₹28,000.00
Total Spent  : ₹29,749.00
Remaining    : -₹1,749.00
Utilization  : [████████████████████] 106.2%
Status       : [!] ALERT: Budget EXCEEDED by ₹1,749.00 (6.2% over budget)!

Category-wise Budget Breakdown:
+-----------+------------+------------+-----------+--------+---------------+
| Category  |     Budget |      Spent | Remaining | Used % |     Status    |
+-----------+------------+------------+-----------+--------+---------------+
| Bills     |  ₹2,000.00 |  ₹1,650.00 |   ₹350.00 |  82.5% |  [!] WARNING  |
| Education |  ₹4,000.00 |  ₹3,600.00 |   ₹400.00 |  90.0% |  [!] WARNING  |
| Food      |  ₹5,500.00 |  ₹5,370.00 |   ₹130.00 |  97.6% |  [!] WARNING  |
| Health    |  No Budget |    ₹980.00 |         - |      - |   Untracked   |
| Other     |  No Budget |  ₹1,499.00 |         - |      - |   Untracked   |
| Rent      | ₹12,000.00 | ₹12,000.00 |     ₹0.00 | 100.0% |  [!] WARNING  |
| Shopping  |  ₹3,500.00 |  ₹4,200.00 |  -₹700.00 | 120.0% |  [!] EXCEEDED |
| Transport |  ₹1,000.00 |    ₹450.00 |   ₹550.00 |  45.0% | [OK] On Track |
+-----------+------------+------------+-----------+--------+---------------+
```

### 4. Spending Summary
Generates comprehensive statistics and horizontal ASCII distribution charts for any chosen month:

```text
=================================================================
                     MONTHLY SPENDING REPORT: 2026-11            
=================================================================

  • Total Monthly Spending: ₹29,749.00
  • Total Transactions    : 9
  • Average per Expense   : ₹3,305.44
  • Average Daily Spend   : ₹2,704.45 (based on 11 days elapsed in current month)
  • Top Spending Category : Rent (₹12,000.00 - 40.3%)
  • Lowest Category       : Transport (₹450.00 - 1.5%)
  • Largest Single Expense: ₹12,000.00 (Monthly apartment rental payment on 2026-11-01)

--- Category-wise Breakdown ---
+-----------+-------------+------------+-------+------------------+
| Category  | Total Spent | % of Month | Count | Distribution     |
+-----------+-------------+------------+-------+------------------+
| Rent      |  ₹12,000.00 |      40.3% |   1   | ██████░░░░░░░░░░ |
| Food      |   ₹5,370.00 |      18.1% |   2   | ███░░░░░░░░░░░░░ |
| Shopping  |   ₹4,200.00 |      14.1% |   1   | ██░░░░░░░░░░░░░░ |
| Education |   ₹3,600.00 |      12.1% |   1   | ██░░░░░░░░░░░░░░ |
| Bills     |   ₹1,650.00 |       5.5% |   1   | █░░░░░░░░░░░░░░░ |
| Other     |   ₹1,499.00 |       5.0% |   1   | █░░░░░░░░░░░░░░░ |
| Health    |     ₹980.00 |       3.3% |   1   | █░░░░░░░░░░░░░░░ |
| Transport |     ₹450.00 |       1.5% |   1   | ░░░░░░░░░░░░░░░░ |
+-----------+-------------+------------+-------+------------------+
```

### 5. Month-over-Month Comparison
Tracks budget growth, transaction volume, and percentage changes across calendar months:

```text
+---------+-------------+--------------+--------------+------------+
|  Month  | Total Spent | Transactions | Top Category | MoM Change |
+---------+-------------+--------------+--------------+------------+
| 2026-09 |  ₹19,349.00 |      7       | Rent         |   Baseline |
| 2026-10 |  ₹24,269.00 |      9       | Rent         |     +25.4% |
| 2026-11 |  ₹29,749.00 |      9       | Rent         |     +22.6% |
+---------+-------------+--------------+--------------+------------+
```

---

## Data Storage & Sample Files

### JSON Data Structure

#### `data/expenses.json`
```json
[
  {
    "id": 1,
    "date": "2026-09-02",
    "amount": 12000.0,
    "category": "Rent",
    "description": "Monthly apartment rental payment"
  }
]
```

#### `data/budgets.json`
```json
{
  "2026-11": {
    "total_budget": 28000.0,
    "category_budgets": {
      "Rent": 12000.0,
      "Food": 5500.0,
      "Shopping": 3500.0,
      "Education": 4000.0,
      "Bills": 2000.0,
      "Transport": 1000.0
    }
  }
}
```

### Pre-seeded Sample Data
The project includes 25 realistic sample expenses spanning 3 consecutive months:
- **September 2026**: Total spend ₹19,349 against ₹26,000 budget (**74.4%**, `[OK] On Track`).
- **October 2026**: Total spend ₹24,269 against ₹28,000 budget (**86.7%**, `[!] WARNING: 80%+ Utilized`).
- **November 2026**: Total spend ₹29,749 against ₹28,000 budget (**106.2%**, `[!] ALERT: EXCEEDED by ₹1,749.00`).

---

## Error Handling & Edge Cases

| Scenario | Handled Gracefully By |
| :--- | :--- |
| **Negative Amounts** | Validated in `prompt_amount()`; displays error and re-prompts. |
| **Invalid Date Formats** | Parsed via `datetime.strptime`; rejects invalid days like `2026-02-31`. |
| **Empty Strings** | Validated in `prompt_non_empty_string()`; prompts user until non-empty input is received. |
| **Missing Files** | `storage.py` creates default directories and initializes empty datasets without crashing. |
| **Corrupted JSON** | Catches `json.JSONDecodeError`, backs up corrupted file with timestamp, and initializes cleanly. |
| **Write Collisions** | Uses atomic `.tmp` file creation followed by rename/replace. |
| **Ctrl+C Interrupts** | Catches `KeyboardInterrupt` gracefully and requests confirmation before exiting. |
| **Windows Console ₹** | Automatically detects and reconfigures terminal stdout/stderr to UTF-8 on Windows. |

---

## Code Quality & Standards

- **PEP 8 Compliance**: Consistent snake_case function naming, clear variable names, and standard spacing.
- **Type Annotations**: Functions annotated with type hints (`list[dict]`, `float`, `str`, `set[str]`).
- **Comprehensive Docstrings**: Every module and function includes clear Google-style docstrings describing parameters, return values, and behavior.
- **Modular Design**: Zero coupling between UI logic, calculations, and storage handlers.
