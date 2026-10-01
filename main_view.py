import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class MainView:

    def __init__(self, root, controller=None):
        self.root = root
        self.controller = controller

        self.root.title("Smart Automatic Attendance Analyzer")
        self.root.geometry("1150x720")
        self.root.configure(bg="#2b2d3a")

        self._build_ui()

    # ================= CONTROLLER INJECTION =================
    def set_controller(self, controller):
        self.controller = controller

    # ================= UI BUILD =================
    def _build_ui(self):

        # ===== TITLE =====
        title_frame = tk.Frame(self.root, bg="#3a3d4f")
        title_frame.pack(fill="x", padx=20, pady=15)

        tk.Label(
            title_frame,
            text="SMART AUTOMATIC ATTENDANCE ANALYZER",
            font=("Segoe UI", 18, "bold"),
            bg="#3a3d4f",
            fg="white",
            pady=10
        ).pack()

        # ===== INPUT CONFIGURATION =====
        input_box = tk.LabelFrame(
            self.root,
            text="  Input Configuration  ",
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg="#2b2d3a",
            bd=2
        )
        input_box.pack(fill="x", padx=25, pady=10)

        tk.Label(input_box, text="Select Attendance Folder:",
                 bg="#2b2d3a", fg="white")\
            .grid(row=0, column=0, padx=10, pady=8, sticky="w")

        self.folder_entry = tk.Entry(input_box, width=55)
        self.folder_entry.grid(row=0, column=1, padx=5)

        tk.Button(
            input_box,
            text="Select Folder",
            width=15,
            command=self._select_folder
        ).grid(row=0, column=2, padx=10)

        # Late Threshold
        tk.Label(input_box,
                 text="Late Threshold (minutes):",
                 bg="#2b2d3a",
                 fg="white")\
            .grid(row=1, column=0, padx=10, pady=6, sticky="w")

        self.late_entry = tk.Entry(input_box, width=10)
        self.late_entry.grid(row=1, column=1, sticky="w")
        self.late_entry.insert(0, "10")

        # Absent Threshold
        tk.Label(input_box,
                 text="Absent Threshold (minutes):",
                 bg="#2b2d3a",
                 fg="white")\
            .grid(row=1, column=2, padx=10, pady=6, sticky="w")

        self.absent_entry = tk.Entry(input_box, width=10)
        self.absent_entry.grid(row=1, column=3, sticky="w")
        self.absent_entry.insert(0, "30")

        # Scoring Info
        tk.Label(input_box,
                 text="Scoring Rule:",
                 bg="#2b2d3a",
                 fg="white")\
            .grid(row=2, column=0, padx=10, pady=6, sticky="w")

        tk.Label(input_box,
                 text="Total = 10 | Late -0.5 | Absent -1",
                 bg="#2b2d3a",
                 fg="#00ffcc")\
            .grid(row=2, column=1, columnspan=3, sticky="w")

        # Buttons
        tk.Button(
            input_box,
            text="Process Attendance",
            width=25,
            height=2,
            command=self._on_process_clicked
        ).grid(row=3, column=1, padx=10, pady=15)

        tk.Button(
            input_box,
            text="Export Report",
            width=25,
            height=2,
            command=self._on_export_clicked
        ).grid(row=3, column=2, padx=10, pady=15)

        # ===== SEARCH =====
        search_frame = tk.Frame(self.root, bg="#2b2d3a")
        search_frame.pack(fill="x", padx=25, pady=5)

        tk.Label(
            search_frame,
            text="Search Student:",
            bg="#2b2d3a",
            fg="white"
        ).pack(side="left")

        self.search_entry = tk.Entry(search_frame, width=40, state="disabled")
        self.search_entry.pack(side="left", padx=10)
        self.search_entry.bind("<KeyRelease>", self._on_search)

        # ===== MAIN CONTENT =====
        content_frame = tk.Frame(self.root, bg="#2b2d3a")
        content_frame.pack(fill="both", expand=True, padx=25, pady=10)

        # TABLE
        table_frame = tk.Frame(content_frame)
        table_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))

        columns = ("Name", "Email", "Normal", "Late", "Absent", "Score")

        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.table.pack(fill="both", expand=True)

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=120)

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        # PIE PANEL
        self.pie_frame = tk.LabelFrame(
            content_frame,
            text=" Attendance Distribution ",
            bg="#2b2d3a",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            width=320,
            height=400
        )
        self.pie_frame.pack(side="right", fill="y")
        self.pie_frame.pack_propagate(False)

        self._show_pie_placeholder()

    # ================= PUBLIC METHODS =================

    def update_table(self, data_list):
        for row in self.table.get_children():
            self.table.delete(row)

        for student in data_list:
            self.table.insert(
                "",
                "end",
                values=(
                    student.get("name", "N/A"),
                    student.get("email", "N/A"),
                    student.get("normal_count", "N/A"),
                    student.get("late_count", "N/A"),
                    student.get("absent_count", "N/A"),
                    student.get("score", "N/A")
                )
            )

    def _show_pie_placeholder(self):
        for widget in self.pie_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.pie_frame,
            text="No chart available.\nProcess attendance to display chart.",
            bg="#2b2d3a",
            fg="gray",
            justify="center"
        ).pack(expand=True)

    def update_chart(self, chart_widget):
    # 1. Identify all current children EXCEPT the one we just received
        for widget in self.pie_frame.winfo_children():
            if widget != chart_widget:
                widget.destroy()
        # 2. Now it is safe to pack
        chart_widget.pack(fill="both", expand=True)
        
    def enable_search(self):
        self.search_entry.config(state="normal")

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def show_info(self, message):
        messagebox.showinfo("Success", message)

    # ================= EVENTS =================

    def _select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, path)

    def _on_process_clicked(self):
        path = self.folder_entry.get().strip()

        if not path:
            self.show_error("Please select a folder first.")
            return

        try:
            late_threshold = int(self.late_entry.get())
            absent_threshold = int(self.absent_entry.get())
        except ValueError:
            self.show_error("Thresholds must be numbers.")
            return

        if late_threshold > absent_threshold:
            self.show_error("Late threshold cannot be greater than Absent threshold.")
            return

        if self.controller:
            self.controller.handle_process(path, late_threshold, absent_threshold)
            self.enable_search()

    def _on_export_clicked(self):
        if not self.controller:
            return

        success = self.controller.handle_export()

        if success:
            self.show_info("Report exported successfully!")
        else:
            self.show_error("Export failed.")

    def _on_search(self, event):
        if not self.controller:
            return

        keyword = self.search_entry.get()
        self.controller.handle_search(keyword)
