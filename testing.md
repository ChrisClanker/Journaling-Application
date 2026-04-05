# Testing Guide

This document describes how to run tests for the Journaling Application.

## Prerequisites

- Python 3.12+
- Virtual environment with dependencies installed
- PostgreSQL client libraries (for PostgreSQL) or SQLite (default for testing)

## Installation

```bash
cd Journaling-Application
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running Tests with Pytest (Recommended)

Pytest is the recommended way to run tests. It provides better output, fixtures, and plugin support.

### Basic Test Run

Run all tests from the project root:

```bash
cd Journaling-Application
pytest
```

Pytest will automatically discover all tests in `journalmain/tests.py` and run them with the correct Django settings and environment variables (configured in `pytest.ini` and `conftest.py`).

### Verbose Output

```bash
pytest -v
```

### Run Specific Test Classes

```bash
# Run only model tests
pytest -k JournalEntryModelTest

# Run only view tests
pytest -k LoginViewTest

# Run only form tests
pytest -k JournalFormTest
```

### Run Specific Tests

```bash
pytest -k test_create_journal_entry
```

### Run Tests Matching a Pattern

```bash
# Run all tests related to goals
pytest -k Goal

# Run all tests related to tags
pytest -k Tag

# Run all dashboard tests
pytest -k Dashboard
```

### Run with Coverage

```bash
pip install pytest-cov
pytest --cov=journalmain --cov-report=html
```

## Running Tests with Django Test Runner

You can also use Django's built-in test runner if preferred.

### Basic Test Run

Run all tests in the journalmain app:

```bash
cd journal_project
DEBUG=True SECRET_KEY=test123 ../venv/bin/python manage.py test journalmain
```

### Verbose Output

For more detailed test output:

```bash
cd journal_project
DEBUG=True SECRET_KEY=test123 ../venv/bin/python manage.py test journalmain --verbosity=2
```

### Run Specific Test Classes

```bash
# Run only model tests
../venv/bin/python manage.py test journalmain.JournalEntryModelTest

# Run only view tests
../venv/bin/python manage.py test journalmain.LoginViewTest

# Run only form tests
../venv/bin/python manage.py test journalmain.JournalFormTest
```

### Run Specific Tests

```bash
../venv/bin/python manage.py test journalmain.JournalEntryModelTest.test_create_journal_entry
```

## Test Coverage

The test suite covers:

### Models (6 test classes)
- `JournalEntryModelTest` - Journal entry creation, string representation, mood handling
- `GoalModelTest` - Goal creation, length choices, parent-child relationships
- `BlurbModelTest` - Blurb creation and journal associations
- `ReportModelTest` - Report creation and type choices
- `MoodListCreationTest` - Mood list parsing and display
- `TagModelTest` - Tag model tests

### Forms (3 test classes)
- `JournalFormTest` - Journal entry form validation
- `GoalFormTest` - Goal form validation
- `AskJournalFormTest` - AI question form validation

### Views (7 test classes)
- `LoginViewTest` - Login page, authentication, error handling
- `JournalsViewTest` - Journal listing, access control
- `JournalCreateViewTest` - Journal creation, form handling
- `JournalDetailViewTest` - Journal detail view, permissions
- `GoalsViewTest` - Goal listing
- `GoalCreateViewTest` - Goal creation
- `GoalDetailViewTest` - Goal detail view
- `ReportDetailViewTest` - Report detail view

### Management Commands (1 test class)
- `GenerateWeeklyReportCommandTest` - Weekly report generation command, user filtering, duplicate detection, entry linking, content validation

### New Views (1 test class)
- `ReportListViewTest` - Report listing, access control, user scoping

### Pagination (1 test class)
- `PaginationTest` - Pagination on journals (15/page), goals (10/page), reports (10/page), tags (20/page), tag detail (15/page), filter preservation, edge cases

### Navigation (1 test class)
- `NavigationBarTest` - Nav bar inclusion across all templates, link verification

### Code Quality (1 test class)
- `NoDebugPrintTest` - Verifies no debug print() statements remain in views.py

## Test Database

Tests use an in-memory SQLite database that is created and destroyed for each test run. No data is persisted.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DEBUG | Enable debug mode | True |
| SECRET_KEY | Django secret key | test123 |
| JOURNAL_APP_DB_HOST | PostgreSQL host (if set, uses PostgreSQL) | Not set |

## CI/CD

For continuous integration, run:

```bash
cd journal_project
export DEBUG=True
export SECRET_KEY=ci-secret-key
../venv/bin/python manage.py test journalmain
```

## Troubleshooting

### Import Errors
Ensure you're running tests with the virtual environment's Python:
```bash
../venv/bin/python manage.py test journalmain
```

### Database Errors
Tests use SQLite in-memory by default. If you have `JOURNAL_APP_DB_HOST` set, tests may fail. Unset it or configure PostgreSQL for testing.
