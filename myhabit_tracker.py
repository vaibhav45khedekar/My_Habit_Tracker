import customtkinter as ctk
from tkinter import messagebox
import json
import datetime
import calendar
import os

class HabitTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("Habit Tracker")
        master.geometry("800x600")
        ctk.set_appearance_mode("System") 
        ctk.set_default_color_theme("green") 

        self.data_file = "habit_data.json"
        self.habits = {}
        self.load_data()

        self.create_widgets()
        self.update_habit_list()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.habits = json.load(f)
            except json.JSONDecodeError:
                self.habits = {}
                messagebox.showerror("Error", "Could not load habit data. Starting fresh.")
        else:
            self.habits = {}

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.habits, f, indent=4)

    def create_widgets(self):
        # Grid layout for main frame
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        # Navigation Frame
        self.navigation_frame = ctk.CTkFrame(self.master, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.navigation_frame, text="HabitFlow",
                                        font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        self.dashboard_button = ctk.CTkButton(self.navigation_frame, text="Dashboard",
                                              command=self.show_dashboard)
        self.dashboard_button.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        self.add_habit_button = ctk.CTkButton(self.navigation_frame, text="Add Habit",
                                              command=self.show_add_habit_dialog)
        self.add_habit_button.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        self.progress_button = ctk.CTkButton(self.navigation_frame, text="View Progress",
                                             command=self.show_progress_view)
        self.progress_button.grid(row=3, column=0, sticky="ew", padx=20, pady=10)

        # Content Frame
        self.content_frame = ctk.CTkFrame(self.master, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Dashboard View
        self.dashboard_view = ctk.CTkScrollableFrame(self.content_frame, label_text="My Habits Today")
        self.dashboard_view.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.dashboard_view.grid_columnconfigure(0, weight=1)

        # Progress View
        self.progress_view = ctk.CTkFrame(self.content_frame) # Initially not gridded
        self.progress_view.grid_columnconfigure(0, weight=1)
        self.progress_view.grid_rowconfigure(2, weight=1) # Row for progress_text

        ctk.CTkLabel(self.progress_view, text="Habit Progress", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=10)

        self.progress_habit_selection = ctk.CTkComboBox(self.progress_view, state="readonly", width=300)
        self.progress_habit_selection.grid(row=1, column=0, pady=10)
        self.progress_habit_selection.bind("<<ComboboxSelected>>", self.display_habit_progress)

        self.progress_text = ctk.CTkTextbox(self.progress_view, wrap="word")
        self.progress_text.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)
        self.progress_text.configure(state="disabled") # Make it read-only

        self.show_dashboard() # Set initial view

    def show_frame(self, frame_to_show):
        for frame in [self.dashboard_view, self.progress_view]:
            if frame.winfo_ismapped(): # Check if it's currently gridded
                frame.grid_forget()
        frame_to_show.grid(row=0, column=0, sticky="nsew")

    def show_dashboard(self):
        self.show_frame(self.dashboard_view)
        self.update_habit_list()

    def show_add_habit_dialog(self):
        dialog = ctk.CTkInputDialog(text="Enter habit name and optional description:", title="Add New Habit")
        # CustomTkinterInputDialog doesn't support multiple entries directly, so we'll simulate.
        # A more complex dialog would involve a custom CTkTopLevel.
        input_string = dialog.get_input()

        if input_string is None: # User cancelled
            return

        parts = input_string.split(',')
        habit_name = parts[0].strip()
        habit_description = parts[1].strip() if len(parts) > 1 else ""

        if not habit_name:
            messagebox.showwarning("Input Error", "Habit name cannot be empty.")
            return

        if habit_name in self.habits:
            messagebox.showwarning("Input Error", f"Habit '{habit_name}' already exists.")
            return

        today = datetime.date.today().isoformat()
        self.habits[habit_name] = {
            "description": habit_description,
            "creation_date": today,
            "completion_history": {}
        }
        self.save_data()
        self.update_habit_list()
        messagebox.showinfo("Success", f"Habit '{habit_name}' added successfully!")

    def update_habit_list(self):
        for widget in self.dashboard_view.winfo_children():
            widget.destroy()

        today = datetime.date.today().isoformat()

        if not self.habits:
            ctk.CTkLabel(self.dashboard_view, text="No habits added  Click 'Add Habit' to start!",
                         font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=20)
            return

        row_num = 0
        for habit_name, data in self.habits.items():
            habit_frame = ctk.CTkFrame(self.dashboard_view, fg_color=("gray85", "gray25"))
            habit_frame.grid(row=row_num, column=0, sticky="ew", pady=5, padx=5)
            habit_frame.grid_columnconfigure(0, weight=1) # Habit name takes most space

            status_text = "Not Done"
            status_color = "red"
            if today in data["completion_history"] and data["completion_history"][today]:
                status_text = "DONE"
                status_color = "green"

            ctk.CTkLabel(habit_frame, text=habit_name, font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
            ctk.CTkLabel(habit_frame, text=status_text, text_color=status_color, font=("Arial", 12, "italic")).grid(row=0, column=1, padx=5)

            if today not in data["completion_history"] or not data["completion_history"][today]:
                mark_button = ctk.CTkButton(habit_frame, text="Mark Done", command=lambda h=habit_name: self.mark_habit_done(h), width=80)
            else:
                mark_button = ctk.CTkButton(habit_frame, text="Mark Undone", command=lambda h=habit_name: self.mark_habit_undone(h), width=80)
            mark_button.grid(row=0, column=2, padx=5)

            delete_button = ctk.CTkButton(habit_frame, text="Delete", command=lambda h=habit_name: self.confirm_delete_habit(h), fg_color="red", hover_color="darkred", width=80)
            delete_button.grid(row=0, column=3, padx=5)
            row_num += 1

    def mark_habit_done(self, habit_name):
        today = datetime.date.today().isoformat()
        if habit_name in self.habits:
            self.habits[habit_name]["completion_history"][today] = True
            self.save_data()
            self.update_habit_list()
            messagebox.showinfo("Habit Updated", f"'{habit_name}' marked as DONE for today.")

    def mark_habit_undone(self, habit_name):
        today = datetime.date.today().isoformat()
        if habit_name in self.habits and today in self.habits[habit_name]["completion_history"]:
            del self.habits[habit_name]["completion_history"][today]
            self.save_data()
            self.update_habit_list()
            messagebox.showinfo("Habit Updated", f"'{habit_name}' marked as UNDONE for today.")

    def confirm_delete_habit(self, habit_name):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the habit '{habit_name}'? This action cannot be undone."):
            self.delete_habit(habit_name)

    def delete_habit(self, habit_name):
        if habit_name in self.habits:
            del self.habits[habit_name]
            self.save_data()
            self.update_habit_list()
            messagebox.showinfo("Habit Deleted", f"Habit '{habit_name}' has been deleted.")

    def show_progress_view(self):
        self.show_frame(self.progress_view)
        self.update_progress_habit_selection()

    def update_progress_habit_selection(self):
        habit_names = sorted(list(self.habits.keys()))
        self.progress_habit_selection.configure(values=habit_names)
        if habit_names:
            self.progress_habit_selection.set(habit_names[0])
            self.display_habit_progress()
        else:
            self.progress_habit_selection.set("")
            self.progress_text.configure(state="normal")
            self.progress_text.delete(1.0, "end")
            self.progress_text.insert("end", "No habits to display progress for.")
            self.progress_text.configure(state="disabled")

    def display_habit_progress(self, event=None):
        selected_habit = self.progress_habit_selection.get()
        self.progress_text.configure(state="normal")
        self.progress_text.delete(1.0, "end")

        if not selected_habit or selected_habit not in self.habits:
            self.progress_text.insert("end", "Please select a habit to view its progress.")
            self.progress_text.configure(state="disabled")
            return

        habit_data = self.habits[selected_habit]
        creation_date_str = habit_data["creation_date"]
        completion_history = habit_data["completion_history"]

        self.progress_text.insert("end", f"Progress for: {selected_habit}\n")
        self.progress_text.insert("end", f"Description: {habit_data['description'] if habit_data['description'] else 'N/A'}\n")
        self.progress_text.insert("end", f"Created on: {creation_date_str}\n\n")

        # Calculate streak
        current_date = datetime.date.today()
        streak = 0
        longest_streak = 0
        temp_streak = 0

        sorted_dates = sorted(completion_history.keys(), key=lambda d: datetime.date.fromisoformat(d))

        for i in range(len(sorted_dates) - 1, -1, -1):
            date_str = sorted_dates[i]
            date_obj = datetime.date.fromisoformat(date_str)

            if completion_history[date_str]:
                temp_streak += 1
                if i == len(sorted_dates) - 1 or (date_obj + datetime.timedelta(days=1)).isoformat() in completion_history:
                    if date_obj == current_date - datetime.timedelta(days=(len(sorted_dates) - 1 - i)): # Check for current streak continuity from today
                        streak += 1
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 0
        longest_streak = max(longest_streak, temp_streak)

        # Recalculate current streak more robustly from today backwards
        streak = 0
        check_date = current_date
        while check_date.isoformat() in completion_history and completion_history[check_date.isoformat()]:
            streak += 1
            check_date -= datetime.timedelta(days=1)


        # Calculate completion percentage
        start_date = datetime.date.fromisoformat(creation_date_str)
        total_days = (current_date - start_date).days + 1
        completed_days = sum(1 for completed in completion_history.values() if completed)
        completion_percentage = (completed_days / total_days) * 100 if total_days > 0 else 0

        self.progress_text.insert("end", f"Current Streak: {streak} days\n")
        self.progress_text.insert("end", f"Longest Streak: {longest_streak} days\n")
        self.progress_text.insert("end", f"Completion Percentage: {completion_percentage:.2f}%\n\n")

        # Calendar View
        self.progress_text.insert("end", "Completion Calendar:\n")
        first_recorded_date = datetime.date.fromisoformat(sorted_dates[0]) if sorted_dates else current_date
        year_month_iterator = first_recorded_date.replace(day=1)

        while year_month_iterator <= current_date.replace(day=1):
            self.progress_text.insert("end", f"\n--- {calendar.month_name[year_month_iterator.month]} {year_month_iterator.year} ---\n")
            cal = calendar.monthcalendar(year_month_iterator.year, year_month_iterator.month)
            self.progress_text.insert("end", "Mo Tu We Th Fr Sa Su\n")
            for week in cal:
                week_str = ""
                for day in week:
                    if day == 0:
                        week_str += "   "
                    else:
                        date_obj = datetime.date(year_month_iterator.year, year_month_iterator.month, day)
                        date_iso = date_obj.isoformat()
                        if date_iso in completion_history and completion_history[date_iso]:
                            week_str += f"{day:2d}*"
                        else:
                            week_str += f"{day:2d} "
                    week_str += " "
                self.progress_text.insert("end", week_str.strip() + "\n")

            if year_month_iterator.month == 12:
                year_month_iterator = year_month_iterator.replace(year=year_month_iterator.year + 1, month=1)
            else:
                year_month_iterator = year_month_iterator.replace(month=year_month_iterator.month + 1)

        self.progress_text.configure(state="disabled")

def main():
    root = ctk.CTk()
    app = HabitTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
