from pathlib import Path

from fitness.file_handler import (
    load_participants,
    load_sessions,
    write_analysis_summary,
    write_analysis_report,
)
from fitness.analysis import classify_session, format_report


participants = load_participants(
    "data/participants.csv"
)


valid_sessions, valid_rejected, valid_accepted = load_sessions(
    "data/fitness_sessions.csv",
    participants,
)

invalid_sessions, invalid_rejected, invalid_accepted = load_sessions(
    "data/fitness_sessions_invalid.csv",
    participants,
)


all_sessions = valid_sessions | invalid_sessions
all_rejected = valid_rejected + invalid_rejected

total_accepted = valid_accepted + invalid_accepted


# Create output folder
output_directory = Path("output")
output_directory.mkdir(exist_ok=True)


# Analyze and print sessions
print("SESSION ANALYSIS")
print("================")

for session_id, session in all_sessions.items():
    result = classify_session(session)

    print(f"\nSession ID: {session_id}")
    print(format_report(session, result))


# Create analysis output files
write_analysis_summary(
    output_directory / "analysis_summary.csv",
    all_sessions,
)

write_analysis_report(
    output_directory / "analysis_report.txt",
    all_sessions,
)


# Print rejected records
print("\nREJECTED RECORDS")
print("================")

for record in all_rejected:
    print(
        record["filename"],
        f"row {record['row_number']}",
        record["field"],
        record["reason"],
    )


# Create rejected_records.txt
rejected_file = (
    output_directory / "rejected_records.txt"
)

try:
    with open(
        rejected_file,
        "w",
        encoding="utf-8",
    ) as file:

        for record in all_rejected:
            file.write(
                f"{record['filename']} "
                f"row {record['row_number']} "
                f"{record['field']} "
                f"{record['reason']}\n"
            )

except PermissionError:
    print(
        f"Permission denied when writing: "
        f"{rejected_file}"
    )


# Completion summary
print("\nCOMPLETION SUMMARY")
print("==================")
print(f"Accepted rows: {total_accepted}")
print(f"Rejected rows: {len(all_rejected)}")
print("Created: output/analysis_summary.csv")
print("Created: output/analysis_report.txt")
print("Created: output/rejected_records.txt")