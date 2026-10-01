def usable_observations(observations):
    """Return observations that are valid and have acceptable signal quality."""
    return [
        observation
        for observation in observations
        if observation.is_valid() and observation.signal_quality >= 0.5
    ]


def average_heart_rate(observations):
    """Calculate average heart rate from usable observations."""
    usable = usable_observations(observations)

    if not usable:
        return None

    heart_rates = [
        observation.heart_rate
        for observation in usable
    ]

    return sum(heart_rates) / len(heart_rates)


def min_max_activity(observations):
    """Find the lowest and highest activity level among usable observations."""
    usable = usable_observations(observations)

    if not usable:
        return None, None

    activity_levels = [
        observation.activity_level
        for observation in usable
    ]

    return min(activity_levels), max(activity_levels)


def classify_session(session):
    """Classify a fitness session and explain the result."""
    total_count = len(session.observations)
    usable = usable_observations(session.observations)
    usable_count = len(usable)

    if total_count == 0:
        return {
            "classification": "insufficient data",
            "reason": "The session contains no observations.",
        }

    if usable_count < total_count / 2:
        return {
            "classification": "insufficient data",
            "reason": (
                "Fewer than half of the observations have "
                "acceptable signal quality."
            ),
        }

    average_hr = average_heart_rate(usable)
    baseline = session.participant.baseline_heart_rate
    heart_rate_offset = average_hr - baseline

    midpoint = len(usable) // 2

    if midpoint > 0:
        first_half = usable[:midpoint]
        second_half = usable[midpoint:]

        first_half_hr = average_heart_rate(first_half)
        second_half_hr = average_heart_rate(second_half)

        first_activity = (
            sum(
                observation.activity_level
                for observation in first_half
            )
            / len(first_half)
        )

        second_activity = (
            sum(
                observation.activity_level
                for observation in second_half
            )
            / len(second_half)
        )

        if (
            first_half_hr is not None
            and second_half_hr is not None
            and first_half_hr - second_half_hr > 15
            and first_activity > second_activity
        ):
            return {
                "classification": "recovering",
                "reason": (
                    "Heart rate and activity both declined "
                    "toward the end of the session."
                ),
            }

    if heart_rate_offset < 15:
        return {
            "classification": "resting",
            "reason": (
                "Average heart rate stayed close to the "
                "participant's baseline heart rate."
            ),
        }

    if heart_rate_offset < 45:
        return {
            "classification": "moderate activity",
            "reason": (
                "Average heart rate was moderately above the "
                "participant's baseline heart rate."
            ),
        }

    return {
        "classification": "high activity",
        "reason": (
            "Average heart rate was substantially above the "
            "participant's baseline heart rate."
        ),
    }


def format_report(session, result):
    """Build a readable report describing the session."""
    total_count = len(session.observations)
    usable_count = len(
        usable_observations(session.observations)
    )

    average_hr = average_heart_rate(
        session.observations
    )

    min_activity, max_activity = min_max_activity(
        session.observations
    )

    lines = []

    lines.append(
        f"Session Report for {session.participant.participant_id}"
    )
    lines.append(
        f"Participant: {session.participant.name}"
    )
    lines.append(
        f"Classification: {result['classification']}"
    )
    lines.append(
        f"Reason: {result['reason']}"
    )
    lines.append(
        f"Baseline heart rate: "
        f"{session.participant.baseline_heart_rate} bpm"
    )

    if average_hr is not None:
        lines.append(
            f"Average heart rate: {average_hr:.1f} bpm"
        )
    else:
        lines.append(
            "Average heart rate: not available"
        )

    if min_activity is not None:
        lines.append(
            f"Activity level range: "
            f"{min_activity:.2f} to {max_activity:.2f}"
        )
    else:
        lines.append(
            "Activity level range: not available"
        )

    lines.append(
        f"Usable observations: "
        f"{usable_count} out of {total_count}"
    )

    poor_quality_count = total_count - usable_count

    if poor_quality_count > 0:
        lines.append(
            f"Poor-quality observations: {poor_quality_count}"
        )

    return "\n".join(lines)