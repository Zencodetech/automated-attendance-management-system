import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from report_generator import ReportGenerator
from tkinter import filedialog


class AttendanceController:
    def __init__(self, view, processor):
        self.view = view
        self.processor = processor

        self.current_participants = []
        self.chart_canvas = None  # keep reference to current matplotlib canvas

    # =========================
    # PROCESS
    # =========================
    def handle_process(self, folder_path, late_threshold, absent_threshold):
        try:
            # thresholds come from UI; still safe-cast
            self.processor.set_thresholds(int(late_threshold), int(absent_threshold))

            participants = self.processor.process_directory(folder_path)
            self.current_participants = participants

            total = self.processor.total_sessions
            table_data = self._convert_to_table_format(participants,total)
            self.view.update_table(table_data)

            # overall class pie
            self._generate_overall_pie_chart()

        except Exception as e:
            self.view.show_error(str(e))

    # =========================
    # SEARCH
    # =========================
    def handle_search(self, keyword):
        try:
            results = self.processor.search_participants(keyword)
            total = self.processor.total_sessions
            table_data = self._convert_to_table_format(results, total)
            self.view.update_table(table_data)
        except Exception as e:
            self.view.show_error(str(e))

    # =========================
    # EXPORT (CSV ONLY)
    # =========================
    def handle_export(self):
        try:
            if not self.current_participants:
                self.view.show_error("No data to export. Please process attendance first.")
                return False

            data_list = self._convert_to_table_format(self.current_participants, self.processor.total_sessions)

            file_path = filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV Files", "*.csv"),])
            if not file_path:
                return False  # user cancelled

            ReportGenerator.export_to_csv(data_list, file_path)
            return True

        except Exception as e:
            self.view.show_error(f"Export failed: {e}")
            return False

    # =========================
    # PIE CHART (OVERALL CLASS)
    # =========================
    def _generate_overall_pie_chart(self):
        stats = self.processor.get_analytics_data()

        # ✅ destroy previous canvas safely (prevents bad window path name)
        self._destroy_existing_chart()

        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie([stats["normal"], stats["late"], stats["absent"]], labels=["Normal", "Late", "Absent"], autopct="%1.1f%%")
        ax.set_title("Overall Class Attendance Distribution")

        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.view.pie_frame)
        self.chart_canvas.draw()

        self.view.update_chart(self.chart_canvas.get_tk_widget())

        # ✅ prevent RAM leak
        plt.close(fig)

    def _destroy_existing_chart(self):
        if self.chart_canvas is not None:
            try:
                self.chart_canvas.get_tk_widget().destroy()
            except Exception:
                pass
            self.chart_canvas = None

    # =========================
    # HELPER
    # =========================
    def _convert_to_table_format(self, participants,total_sessions):
        table_data = []
        for p in participants:
            display_score = f"{p.score} / {total_sessions}"
            table_data.append({
                "name": p.name,
                "email": p.email,
                "normal_count": p.normal_count,
                "late_count": p.late_count,
                "absent_count": p.absent_count,
                "score": display_score
            })
        return table_data
