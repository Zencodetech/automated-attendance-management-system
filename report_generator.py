import pandas as pd
import os
from datetime import datetime




class ReportGenerator:
    @staticmethod
    def export_to_csv(data_list, file_path):
        """
        Converts a list of dictionaries into a CSV file.
        """
        if not isinstance(data_list, list):
            raise TypeError("data_list must be a list of dictionaries.")
        if not data_list:
            raise ValueError("No data available to export.")

        # Create DataFrame from the list of dictionaries
        df = pd.DataFrame(data_list)

        # Rename columns for professional look
        column_map = {
            "name": "Name",
            "email": "Email",
            "normal_count": "Normal",
            "late_count": "Late",
            "absent_count": "Absent",
            "score": "Score",
        }
        df = df.rename(columns=column_map)

        # Ensure output directory exists
        dirpath = os.path.dirname(file_path)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)

        # Export
        df.to_csv(file_path, index=False, encoding="utf-8-sig")  # utf-8-sig for Excel compatibility