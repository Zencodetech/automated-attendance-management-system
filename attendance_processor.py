import os
import pandas as pd
from Participant import Participant


class AttendanceProcessor:
    """Process attendance files and compute participant scores.

    Attributes:
        participants (dict): mapping email -> Participant instance
        total_sessions (int): number of session files processed
    """

    def __init__(self):
        self.participants = {}   # email -> Participant
        self.total_sessions = 0
        self.late_threshold = 10 # Default 10 minutes
        self.absent_threshold = 30 # Default 30 minutes

    # ==========================================================
    # PUBLIC METHODS
    # ==========================================================
    
    def set_thresholds(self, late_minutes, absent_minutes):
        """
        Updates the rules for the next processing run.
        Values are passed from the Controller.
        """
        if late_minutes >= absent_minutes:
            raise ValueError("Late threshold must be less than absent threshold.")
        
        self.late_threshold = int(late_minutes)
        self.absent_threshold = int(absent_minutes)

    def process_file(self, file_path):
        # Read and parse the attendance export (CSV expected)
        if file_path.endswith('.xlsx'):
            print(f"Skipping .xlsx file for now: {file_path}")
            return

        df = self._read_mt_csv(file_path)
        class_start_time = self._extract_class_start(df)
        participants_df = self._extract_participants_table(df)

        # Process rows and collect emails seen in this session
        present_emails = self._process_attendance_rows(participants_df, class_start_time)

        # Mark known participants who were not present as absent (after first session)
        if self.total_sessions > 0:
            for email in list(self.participants.keys()):
                if email not in present_emails:
                    self.participants[email].update_attendance('absent')

        self.total_sessions += 1

    def process_directory(self, directory_path):
        """Reset info and process all attendance files when process new directory."""
        self.participants = {}
        self.total_sessions = 0
        """Walk the directory, read each attendance file and update participants."""
        for file_name in os.listdir(directory_path):
            if file_name.endswith(".csv"):
                file_path = os.path.join(directory_path, file_name)
                try:
                    self.process_file(file_path)
                except Exception as e:
                    print(f"Error processing {file_name}: {e}")

        # After all files are processed, compute final scores for each participant
        self.calculate_all_scores()
        return self.get_all_participants()

    def update_participant(self, name, email, status):
        """Ensure a Participant instance exists and record attendance entry."""
        if email not in self.participants:
            self.participants[email] = Participant(name, email)
        self.participants[email].update_attendance(status)

    def calculate_all_scores(self):
        """Recalculate and store scores for every participant."""
        for participant in self.participants.values():
            participant.calculate_score(self.total_sessions)

    def get_all_participants(self):
        """Return a list of all Participant objects."""
        return list(self.participants.values())

    def search_participants(self, keyword):
        """
        Returns a filtered list of Participant objects.
        If keyword is empty, returns all.
        """
        if not keyword or keyword.strip() == "":
            return self.get_all_participants()

        keyword_lower = keyword.lower().strip()
        results = []
        for p in self.participants.values():
            if keyword_lower in p.name.lower() or keyword_lower in p.email.lower():
                results.append(p)
        return results
    
    def get_analytics_data(self):
        """
        Aggregates attendance counts for all participants.
        Returns a dictionary for the Controller/Visualization logic.
        """
        stats = {
            "normal": 0,
            "late": 0,
            "absent": 0
        }

        # Safety Check: If no participants exist, return zeros to avoid crashes
        if not self.participants:
            return stats

        for p in self.participants.values():
            stats["normal"] += p.normal_count
            stats["late"] += p.late_count
            stats["absent"] += p.absent_count

        return stats

    # ==========================================================
    # PRIVATE METHODS
    # ==========================================================

    def _read_mt_csv(self, file_path):
        """Read MT CSV export with no header (contains summary rows)."""
        # Read as plain text, then parse sections manually
        # Try UTF-16 first (Teams Default)
        try:
            with open(file_path, encoding="utf-16") as f:
                lines = f.readlines()
        except UnicodeError:
            # Fallback to UTF-8 (Standard CSV/Manual edits)
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
        
        # Convert lines to a DataFrame-like structure
        data = []
        for line in lines:
            if "\t" in line:
                cols = line.rstrip("\n").split("\t")
            else:
                cols = line.rstrip("\n").split(",")
            data.append(cols)
        
        # Create DataFrame with variable column counts (fill missing with NaN)
        max_cols = max(len(row) for row in data) if data else 1
        data = [row + [None] * (max_cols - len(row)) for row in data]
        
        return pd.DataFrame(data)

    def _extract_class_start(self, df):
        """Extract and parse the meeting start time."""
        first_col = df.iloc[:, 0].astype(str).str.strip().str.lower()
        start_row = df[first_col == "start time"]

        if start_row.empty:
            raise ValueError("Start time not found in MT file.")

        start_time_str = start_row.iloc[0, 1]
        class_start_time = pd.to_datetime(start_time_str, errors="coerce")

        if pd.isna(class_start_time):
            raise ValueError("Invalid class start time format.")

        return class_start_time

    def _extract_participants_table(self, df):
        """Extract the participants table section."""
        first_col = df.iloc[:, 0].astype(str).str.strip().str.lower()

        name_rows = df[first_col == "name"].index
        if len(name_rows) == 0:
            raise ValueError("Participants header row not found.")

        header_index = name_rows[0]

        participants_df = df.iloc[header_index + 1:].copy()
        participants_df.columns = df.iloc[header_index].astype(str)
        participants_df = participants_df.reset_index(drop=True)
        
        # Remove rows where the first column equals the header name (duplicates)
        participants_df = participants_df[participants_df.iloc[:, 0].astype(str).str.strip().str.lower() != "name"]

        return participants_df

    def _find_column(self, columns, keywords):
        """Find a column by keyword match (case-insensitive)."""
        for col in columns:
            col_str = str(col).strip().lower()
            for keyword in keywords:
                if keyword in col_str:
                    return col
        return None

    def _process_attendance_rows(self, participants_df, class_start_time):
        """Process attendance for each participant row."""
        present_emails = set()
        name_col = self._find_column(participants_df.columns, ["name"])
        email_col = self._find_column(participants_df.columns, ["email"])
        join_col = self._find_column(
            participants_df.columns,
            ["first join", "join time"]
        )

        if name_col is None or email_col is None:
            raise ValueError("Required participant columns not found.")

        # Remove rows with missing email
        participants_df = participants_df.dropna(subset=[email_col])

        # Handle duplicate emails (keep earliest join time)
        if join_col:
            participants_df[join_col] = pd.to_datetime(
                participants_df[join_col],
                errors="coerce",
                format="%m/%d/%y, %I:%M:%S %p"
            )

            participants_df = (
                participants_df
                .sort_values(join_col)
                .groupby(email_col, as_index=False)
                .first()
            )

        for _, row in participants_df.iterrows():
            name = str(row[name_col])
            email = str(row[email_col]).strip()
            join_time = row[join_col] if join_col else pd.NaT

            if email not in self.participants:
                self.participants[email] = Participant(name, email)
                # If they join late, they missed previous sessions
                self.participants[email].absent_count = self.total_sessions

            status = self._determine_status(join_time, class_start_time)
            self.participants[email].update_attendance(status)
            present_emails.add(email)

        return present_emails

    def _determine_status(self, join_time, class_start_time):
        """Determine attendance status based on join time."""
        if pd.isna(join_time):
            return "absent"

        if pd.isna(class_start_time):
            return "normal"

        diff_minutes = (join_time - class_start_time).total_seconds() / 60

        if diff_minutes > self.absent_threshold:
            return "absent"
        elif diff_minutes > self.late_threshold:
            return "late"
        else:
            return "normal"
