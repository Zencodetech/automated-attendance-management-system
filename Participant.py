class Participant:
    """Represents a participant and tracks attendance.

    Attributes:
        name (str): participant full name
        email (str): participant email
        normal_count (int): number of on-time attendances
        late_count (int): number of late attendances
        absent_count (int): number of absences
        score (float): computed attendance score

    Methods:
        update_attendance(status): increment count; raises ValueError for invalid status.
        calculate_score(total_sessions): compute and store score.
        to_dict(total_sessions): serialize participant to a dict.
    """

    def __init__(self, name, email):
        # Basic identity
        self.name = name
        self.email = email
        # Attendance counters
        self.normal_count = 0
        self.late_count = 0
        self.absent_count = 0
        # Cached score (updated by calculate_score)
        self.score = 0.0

    def update_attendance(self, status):
        # Increment the appropriate counter for a single attendance entry.
        # Valid statuses: 'normal', 'late', 'absent'
        if status == 'normal':
            self.normal_count += 1
        elif status == 'late':
            self.late_count += 1
        elif status == 'absent':
            self.absent_count += 1
        else:
            # Protect against typos or unexpected values
            raise ValueError(f"Invalid attendance status: {status}")
            
    def calculate_score(self, total_sessions):
        # Compute a score based on total sessions and penalties:
        # - late = 0.5 penalty per late
        # - absent = 1.0 penalty per absence
        # Store result in `self.score` (mutable cache).
        self.score = total_sessions  - (self.late_count * 0.5) - (self.absent_count)
        
    def to_dict(self, total_sessions):
        # Return a serializable representation. Note: `score` should be
        # up-to-date by calling `calculate_score(total_sessions)` first.
        return {
            'name': self.name,
            'email': self.email,
            'normal_count': self.normal_count,
            'late_count': self.late_count,
            'absent_count': self.absent_count,
            "max_score": total_sessions,
            'score': self.score
        }