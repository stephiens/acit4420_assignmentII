import csv
import re

from fitness.models import Participant, Observation, Session


class InvalidIdentifierError(ValueError):
    """Raised when an identifier has an invalid format."""
    pass


class InvalidRecordError(ValueError):
    """Raised when a CSV record contains invalid data."""
    pass


def valid_participant_id(participant_id):
    """Check participant ID format."""
    pattern = r"^P\d{3}$"
    return re.fullmatch(pattern, participant_id) is not None


def valid_session_id(session_id):
    """Check fitness session ID format."""
    pattern = r"^FIT-\d{4}-\d{3}$"
    return re.fullmatch(pattern, session_id) is not None


def load_participants(filename):
    """Load participants from a CSV file."""
    participants = {}

    try:
        with open(
            filename,
            "r",
            encoding="utf-8",
            newline="",
        ) as file:

            reader = csv.DictReader(file)

            for row_number, row in enumerate(reader, start=2):
                try:
                    if None in row:
                        raise InvalidRecordError(
                            "record: unexpected number of fields"
                        )

                    required_fields = [
                        "participant_id",
                        "name",
                        "baseline_heart_rate",
                        "baseline_skin_response",
                        "baseline_temperature",
                    ]

                    for field in required_fields:
                        value = row.get(field)

                        if value is None or value.strip() == "":
                            raise InvalidRecordError(
                                f"{field}: missing value"
                            )

                    participant_id = row["participant_id"]

                    if not valid_participant_id(participant_id):
                        raise InvalidIdentifierError(
                            f"participant_id: invalid format "
                            f"'{participant_id}'"
                        )

                    participant = Participant(
                        participant_id=participant_id,
                        name=row["name"],
                        baseline_heart_rate=float(
                            row["baseline_heart_rate"]
                        ),
                        baseline_skin_response=float(
                            row["baseline_skin_response"]
                        ),
                        baseline_temperature=float(
                            row["baseline_temperature"]
                        ),
                    )

                    participants[participant_id] = participant

                except (
                    InvalidIdentifierError,
                    InvalidRecordError,
                    ValueError,
                    KeyError,
                ) as error:
                    print(
                        f"{filename} row {row_number}: {error}"
                    )

    except FileNotFoundError:
        print(f"File not found: {filename}")

    except PermissionError:
        print(f"Permission denied: {filename}")

    except csv.Error as error:
        print(f"CSV error in {filename}: {error}")

    return participants


def load_sessions(filename, participants):
    """Load session data and record rejected rows."""
    session_data = {}
    rejected_records = []
    accepted_rows = 0

    try:
        with open(
            filename,
            "r",
            encoding="utf-8",
            newline="",
        ) as file:

            reader = csv.DictReader(file)

            for row_number, row in enumerate(reader, start=2):

                try:
                    if None in row:
                        raise InvalidRecordError(
                            "record: unexpected number of fields"
                        )

                    required_fields = [
                        "session_id",
                        "participant_id",
                        "timestamp",
                        "heart_rate",
                        "skin_response",
                        "temperature",
                        "activity_level",
                        "signal_quality",
                    ]

                    for field in required_fields:
                        value = row.get(field)

                        if value is None or value.strip() == "":
                            raise InvalidRecordError(
                                f"{field}: missing value"
                            )

                    session_id = row["session_id"]
                    participant_id = row["participant_id"]

                    if not valid_session_id(session_id):
                        raise InvalidIdentifierError(
                            f"session_id: invalid format "
                            f"'{session_id}'"
                        )

                    if not valid_participant_id(participant_id):
                        raise InvalidIdentifierError(
                            f"participant_id: invalid format "
                            f"'{participant_id}'"
                        )

                    if participant_id not in participants:
                        raise InvalidRecordError(
                            f"participant_id: unknown participant "
                            f"'{participant_id}'"
                        )

                    numeric_fields = [
                        "timestamp",
                        "heart_rate",
                        "skin_response",
                        "temperature",
                        "activity_level",
                        "signal_quality",
                    ]

                    values = {}

                    for field in numeric_fields:
                        value = row[field]

                        try:
                            values[field] = float(value)

                        except ValueError as error:
                            raise InvalidRecordError(
                                f"{field}: '{value}' is not "
                                f"a valid number"
                            ) from error

                    timestamp = values["timestamp"]
                    heart_rate = values["heart_rate"]
                    skin_response = values["skin_response"]
                    temperature = values["temperature"]
                    activity_level = values["activity_level"]
                    signal_quality = values["signal_quality"]

                    if timestamp < 0:
                        raise InvalidRecordError(
                            "timestamp: must be non-negative"
                        )

                    if not 35 <= heart_rate <= 205:
                        raise InvalidRecordError(
                            "heart_rate: must be between 35 and 205"
                        )

                    if skin_response < 0:
                        raise InvalidRecordError(
                            "skin_response: must be non-negative"
                        )

                    if not 20 <= temperature <= 45:
                        raise InvalidRecordError(
                            "temperature: must be between 20 and 45"
                        )

                    if not 0 <= activity_level <= 1:
                        raise InvalidRecordError(
                            "activity_level: must be between 0 and 1"
                        )

                    if not 0 <= signal_quality <= 1:
                        raise InvalidRecordError(
                            "signal_quality: must be between 0 and 1"
                        )

                    observation = Observation(
                        timestamp=timestamp,
                        heart_rate=heart_rate,
                        skin_response=skin_response,
                        temperature=temperature,
                        activity_level=activity_level,
                        signal_quality=signal_quality,
                    )

                    observation.validate()

                    if session_id not in session_data:
                        session_data[session_id] = {
                            "participant": participants[
                                participant_id
                            ],
                            "observations": [],
                        }

                    session_data[session_id][
                        "observations"
                    ].append(observation)

                    accepted_rows += 1

                except (
                    InvalidIdentifierError,
                    InvalidRecordError,
                ) as error:

                    message = str(error)

                    if ":" in message:
                        field, reason = message.split(":", 1)
                    else:
                        field = "record"
                        reason = message

                    rejected_records.append(
                        {
                            "filename": filename,
                            "row_number": row_number,
                            "field": field.strip(),
                            "reason": reason.strip(),
                        }
                    )

                except KeyError as error:
                    rejected_records.append(
                        {
                            "filename": filename,
                            "row_number": row_number,
                            "field": str(error).strip("'"),
                            "reason": "missing required field",
                        }
                    )

    except FileNotFoundError:
        print(f"File not found: {filename}")

    except PermissionError:
        print(f"Permission denied: {filename}")

    except csv.Error as error:
        print(f"CSV error in {filename}: {error}")

    sessions = {}

    for session_id, data in session_data.items():
        sessions[session_id] = Session(
            participant=data["participant"],
            observations=data["observations"],
        )

    return sessions, rejected_records, accepted_rows


def write_analysis_summary(filename, sessions):
    """Write one summary row for every processed session."""

    from fitness.analysis import (
        average_heart_rate,
        min_max_activity,
        classify_session,
        usable_observations,
    )

    try:
        with open(
            filename,
            "w",
            encoding="utf-8",
            newline="",
        ) as file:

            fieldnames = [
                "session_id",
                "participant_id",
                "classification",
                "average_heart_rate",
                "min_activity",
                "max_activity",
                "usable_observations",
                "total_observations",
            ]

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            for session_id, session in sessions.items():
                result = classify_session(session)

                average_hr = average_heart_rate(
                    session.observations
                )

                min_activity, max_activity = min_max_activity(
                    session.observations
                )

                usable_count = len(
                    usable_observations(
                        session.observations
                    )
                )

                writer.writerow(
                    {
                        "session_id": session_id,
                        "participant_id":
                            session.participant.participant_id,
                        "classification":
                            result["classification"],
                        "average_heart_rate": (
                            f"{average_hr:.1f}"
                            if average_hr is not None
                            else ""
                        ),
                        "min_activity": (
                            f"{min_activity:.2f}"
                            if min_activity is not None
                            else ""
                        ),
                        "max_activity": (
                            f"{max_activity:.2f}"
                            if max_activity is not None
                            else ""
                        ),
                        "usable_observations":
                            usable_count,
                        "total_observations":
                            len(session.observations),
                    }
                )

    except PermissionError:
        print(
            f"Permission denied when writing: {filename}"
        )

    except csv.Error as error:
        print(
            f"CSV error while writing {filename}: {error}"
        )


def write_analysis_report(filename, sessions):
    """Write the readable analysis report."""

    from fitness.analysis import (
        classify_session,
        format_report,
    )

    try:
        with open(
            filename,
            "w",
            encoding="utf-8",
        ) as file:

            for session_id, session in sessions.items():
                result = classify_session(session)

                file.write(
                    f"Session ID: {session_id}\n"
                )

                file.write(
                    format_report(session, result)
                )

                file.write("\n\n")

    except PermissionError:
        print(
            f"Permission denied when writing: {filename}"
        )