class Participant:
    """Represents one person taking part in a fitness session and their baseline measurements."""

    def __init__(self, participant_id, name, baseline_heart_rate, baseline_skin_response, baseline_temperature):
        self.participant_id = participant_id
        self.name = name
        self.baseline_heart_rate = baseline_heart_rate
        self.baseline_skin_response = baseline_skin_response
        self.baseline_temperature = baseline_temperature

class Observation:
    """Represents one sensor reading taken at a specific point in time during a session."""

    def __init__(self, timestamp, heart_rate, skin_response, temperature, activity_level, signal_quality):
        self.timestamp = timestamp
        self.heart_rate = heart_rate
        self.skin_response = skin_response
        self.temperature = temperature
        self.activity_level = activity_level
        self.signal_quality = signal_quality
        self._is_valid = True

    def mark_invalid(self):
        """Flip observation's validity flag to False (called when check fails)."""
        self._is_valid = False

    def is_valid(self):
        """Return whether observation is currently considered valid."""
        return self._is_valid

    def validate(self):
        """Check observation's heart_rate and activity_level, marking it invalid if either fails."""
        heart_rate_validator = HeartRateValidator()
        activity_validator = ActivityLevelValidator()

        if not heart_rate_validator.check(self.heart_rate):
            self.mark_invalid()

        if not activity_validator.check(self.activity_level):
            self.mark_invalid()

class Session:
    """Groups Participant together with a list of Observation objects for a single workout session."""

    def __init__(self, participant, observations):
        self.participant = participant
        self.observations = observations

class Validator:
    """Base class for validation rule. Subclasses override check() with their own logic."""

    def check(self, value):
        """Return True if value passes this rule. The base version accepts everything; subclasses override this."""
        return True

class HeartRateValidator(Validator):
    """Validates that heart rate readings falls within a physically realistic range for humans."""

    def check(self, value):
        """Return True if heart rate is a real number within a realistic human range."""
        if value is None:
            return False
        return 35 <= value <=205

class ActivityLevelValidator(Validator):
    """Validates that activity level reading falls within the expected 0-1 range."""

    def check(self, value):
        """Return True if the activity level is a real number between 0 and 1."""
        if value is None:
            return False
        return 0 <= value <=1