import unittest

from fitness.models import Observation
from fitness.analysis import average_heart_rate
from fitness.file_handler import (
    load_participants,
    load_sessions,
    valid_participant_id,
    valid_session_id,
)


class TestIdentifiers(unittest.TestCase):
    """Tests the regular-expression identifier validation."""

    def test_valid_identifiers(self):
        self.assertTrue(valid_participant_id("P001"))
        self.assertTrue(valid_session_id("FIT-2026-001"))

    def test_invalid_identifiers(self):
        self.assertFalse(valid_participant_id("001"))
        self.assertFalse(valid_session_id("FIT-26-001"))


class TestObservationValidation(unittest.TestCase):
    """Tests valid, invalid and boundary observation values."""

    def test_valid_observation(self):
        observation = Observation(
            timestamp=0,
            heart_rate=100,
            skin_response=2.5,
            temperature=33.0,
            activity_level=0.5,
            signal_quality=0.9,
        )

        observation.validate()

        self.assertTrue(observation.is_valid())

    def test_invalid_heart_rate(self):
        observation = Observation(
            timestamp=0,
            heart_rate=300,
            skin_response=2.5,
            temperature=33.0,
            activity_level=0.5,
            signal_quality=0.9,
        )

        observation.validate()

        self.assertFalse(observation.is_valid())

    def test_heart_rate_boundaries(self):
        low = Observation(
            0, 35, 2.5, 33.0, 0.5, 0.9
        )

        high = Observation(
            0, 205, 2.5, 33.0, 0.5, 0.9
        )

        low.validate()
        high.validate()

        self.assertTrue(low.is_valid())
        self.assertTrue(high.is_valid())

    def test_activity_boundaries(self):
        low = Observation(
            0, 100, 2.5, 33.0, 0, 0.9
        )

        high = Observation(
            0, 100, 2.5, 33.0, 1, 0.9
        )

        low.validate()
        high.validate()

        self.assertTrue(low.is_valid())
        self.assertTrue(high.is_valid())


class TestFileHandling(unittest.TestCase):
    """Tests the official valid, invalid and missing-file cases."""

    def test_valid_official_file(self):
        participants = load_participants(
            "data/participants.csv"
        )

        sessions, rejected, accepted = load_sessions(
            "data/fitness_sessions.csv",
            participants,
        )

        self.assertGreater(len(sessions), 0)
        self.assertGreater(accepted, 0)
        self.assertEqual(len(rejected), 0)

    def test_invalid_official_file(self):
        participants = load_participants(
            "data/participants.csv"
        )

        sessions, rejected, accepted = load_sessions(
            "data/fitness_sessions_invalid.csv",
            participants,
        )

        self.assertGreater(len(rejected), 0)

    def test_missing_file(self):
        participants = load_participants(
            "data/participants.csv"
        )

        sessions, rejected, accepted = load_sessions(
            "data/does_not_exist.csv",
            participants,
        )

        self.assertEqual(sessions, {})
        self.assertEqual(rejected, [])
        self.assertEqual(accepted, 0)


class TestSignalQuality(unittest.TestCase):
    """Tests the documented poor signal-quality rule."""

    def test_poor_signal_quality_is_not_used_in_average(self):
        good = Observation(
            0, 100, 2.5, 33.0, 0.5, 0.9
        )

        poor = Observation(
            1, 200, 2.5, 33.0, 0.5, 0.4
        )

        good.validate()
        poor.validate()

        self.assertEqual(
            average_heart_rate([good, poor]),
            100,
        )


if __name__ == "__main__":
    unittest.main()