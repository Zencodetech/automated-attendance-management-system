import tkinter as tk
from main_view import MainView
from attendance_controller import AttendanceController
from attendance_processor import AttendanceProcessor


def main():
    root = tk.Tk()

    view = MainView(root)
    processor = AttendanceProcessor()
    controller = AttendanceController(view, processor)

    view.set_controller(controller)

    root.mainloop()


if __name__ == "__main__":
    main()
