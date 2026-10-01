# ACIT4420 Assignment II
## Smart Fitness Session Analyzer

This project is my solution for Python Programming Assignment II in ACIT4420 Problem-Solving with Scripting.

It continues Option A from Assignment I: Smart Fitness Session Analyzer. The program reads participant and fitness-session data from CSV files, validates the data, analyzes the fitness sessions, and creates output reports.

## Project structure

The project is organized into a small Python package:

- `main.py` runs the application
- `fitness/models.py` contains the Participant, Observation, Session and validator classes
- `fitness/file_handler.py` handles CSV input, validation and output files
- `fitness/analysis.py` contains the analysis and classification functions
- `tests.py` contains the automated tests
- `data/` contains the official CSV input files
- `output/` contains the generated reports

## Input files

The program uses the three official files provided for Option A:

- `participants.csv`
- `fitness_sessions.csv`
- `fitness_sessions_invalid.csv`

Both the valid and intentionally invalid session files are processed.

## Validation

Participant IDs must follow the format `P` followed by three digits, for example `P001`.

Session IDs must follow the format `FIT-YYYY-NNN`, for example `FIT-2026-001`.

Regular expressions are used to validate both identifier formats.

The program also checks for missing fields, unexpected row lengths, invalid numeric values, impossible or out-of-range measurements, and unknown participant IDs.

Invalid rows are rejected without stopping the rest of the program. Information about the filename, row number, field and reason is saved for each rejected row.

## Signal quality

`signal_quality` must be between 0 and 1.

I use `0.5` as the minimum acceptable signal quality for analysis. An observation with a signal quality below `0.5` is treated as poor-quality sensor data.

Poor-quality observations are not rejected as malformed rows if their value is still within the valid 0 to 1 range. Instead, they are excluded from calculations such as average heart rate and activity range.

If fewer than half of the observations in a session have acceptable signal quality, the session is classified as `insufficient data`.

## Session analysis

The program compares the participant's session measurements with their personal baseline heart rate.

A session can be classified as:

- resting
- moderate activity
- high activity
- recovering
- insufficient data

The program also gives a reason for each classification.

Recovery is detected by comparing the earlier and later parts of a session. A session can be classified as recovering when both heart rate and activity decrease toward the end of the session.

## Output

The program automatically creates the `output` directory if it does not already exist.

It creates three files:

- `analysis_summary.csv`
- `analysis_report.txt`
- `rejected_records.txt`

`analysis_summary.csv` contains one row for each processed session.

`analysis_report.txt` contains a readable report for each session, including the classification and reason.

`rejected_records.txt` contains information about rows that could not be accepted and why they were rejected.

Running the program again replaces the previous report contents so that the output remains predictable.

## Error handling

The project uses the custom exceptions `InvalidIdentifierError` and `InvalidRecordError`.

It also handles relevant errors such as invalid values, missing keys, missing files, permission errors and CSV errors without using a broad `except Exception` as the main error-handling strategy.

## Running the program

The program can be run from the repository root with:

```bash
python3 main.py
```

The tests can be run with:

```bash
python3 tests.py
```

During development, I normally run the Python files directly in VS Code using the Run button or my `Cmd + Enter` shortcut.

## Tests

The project uses Python's built-in `unittest` module.

The tests cover:

- valid data
- invalid data
- identifier validation
- missing files
- boundary values
- poor signal quality

The current test suite contains 10 tests.

## Requirements

The project uses only the Python standard library. No external packages are required.