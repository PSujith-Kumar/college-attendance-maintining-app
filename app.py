import tkinter as tk
from tkinter import ttk, messagebox
from data_manager import DataManager
from notification_handler import NotificationHandler
from datetime import datetime
import pandas as pd

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("College Attendance & Marks Management (WhatsApp)")
        self.root.geometry("900x700")
        
        # UI Styling
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6)
        self.style.configure("Header.TLabel", font=("Arial", 16, "bold"))

        self.db = DataManager()
        # You can add real credentials here. Note: from_number must be 'whatsapp:+...'
        self.notifier = NotificationHandler()

        self.create_widgets()

    def create_widgets(self):
        # Notebook for Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', pady=10, padx=10)

        # Tab 1: Attendance
        self.attn_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.attn_frame, text="Mark Attendance")
        self.setup_attendance_tab()

        # Tab 2: Marks Management
        self.marks_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.marks_frame, text="Marks Entry")
        self.setup_marks_tab()

        # Tab 3: Student Master (Registration/Update)
        self.reg_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reg_frame, text="Student Data")
        self.setup_registration_tab()

        # Tab 4: View Records
        self.view_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.view_frame, text="View Records")
        self.setup_view_tab()

    def setup_attendance_tab(self):
        lbl_title = ttk.Label(self.attn_frame, text="Daily Attendance Marking", style="Header.TLabel")
        lbl_title.grid(row=0, column=0, columnspan=2, pady=20)

        ttk.Label(self.attn_frame, text="Select Student:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.student_combo = ttk.Combobox(self.attn_frame, width=50, state="readonly")
        self.student_combo.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        self.refresh_student_lists()

        ttk.Label(self.attn_frame, text="Status:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.status_var = tk.StringVar(value="Present")
        ttk.Radiobutton(self.attn_frame, text="Present", variable=self.status_var, value="Present", command=self.toggle_reason).grid(row=2, column=1, padx=10, pady=5, sticky='w')
        ttk.Radiobutton(self.attn_frame, text="Absent", variable=self.status_var, value="Absent", command=self.toggle_reason).grid(row=3, column=1, padx=10, pady=5, sticky='w')

        self.lbl_reason = ttk.Label(self.attn_frame, text="Reason for Leave:")
        self.entry_reason = ttk.Entry(self.attn_frame, width=53)
        
        self.lbl_reason.grid(row=4, column=0, padx=10, pady=5, sticky='e')
        self.entry_reason.grid(row=4, column=1, padx=10, pady=5, sticky='w')
        self.lbl_reason.grid_remove()
        self.entry_reason.grid_remove()

        btn_mark = ttk.Button(self.attn_frame, text="Mark Attendance & Notify Parent", command=self.handle_attendance)
        btn_mark.grid(row=5, column=0, columnspan=2, pady=30)

    def toggle_reason(self):
        if self.status_var.get() == "Absent":
            self.lbl_reason.grid()
            self.entry_reason.grid()
        else:
            self.lbl_reason.grid_remove()
            self.entry_reason.grid_remove()

    def setup_marks_tab(self):
        lbl_title = ttk.Label(self.marks_frame, text="Enter Student Marks", style="Header.TLabel")
        lbl_title.grid(row=0, column=0, columnspan=2, pady=20)

        ttk.Label(self.marks_frame, text="Select Student:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.marks_student_combo = ttk.Combobox(self.marks_frame, width=50, state="readonly")
        self.marks_student_combo.grid(row=1, column=1, padx=10, pady=5, sticky='w')

        ttk.Label(self.marks_frame, text="Subject:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.entry_subject = ttk.Entry(self.marks_frame, width=53)
        self.entry_subject.grid(row=2, column=1, padx=10, pady=5, sticky='w')

        ttk.Label(self.marks_frame, text="Exam Name:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.entry_exam = ttk.Entry(self.marks_frame, width=53)
        self.entry_exam.grid(row=3, column=1, padx=10, pady=5, sticky='w')

        ttk.Label(self.marks_frame, text="Marks Obtained:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        self.entry_marks = ttk.Entry(self.marks_frame, width=53)
        self.entry_marks.grid(row=4, column=1, padx=10, pady=5, sticky='w')

        btn_save_marks = ttk.Button(self.marks_frame, text="Save Marks & Notify Parent", command=self.handle_marks)
        btn_save_marks.grid(row=5, column=0, columnspan=2, pady=30)

    def setup_registration_tab(self):
        lbl_title = ttk.Label(self.reg_frame, text="Student Master Management", style="Header.TLabel")
        lbl_title.grid(row=0, column=0, columnspan=2, pady=20)

        labels = ["Student ID", "Full Name", "Department", "Parent Name", "Parent Mobile (WhatsApp)"]
        self.reg_entries = {}

        for i, text in enumerate(labels):
            ttk.Label(self.reg_frame, text=f"{text}:").grid(row=i+1, column=0, padx=10, pady=5, sticky='e')
            entry = ttk.Entry(self.reg_frame, width=40)
            entry.grid(row=i+1, column=1, padx=10, pady=5, sticky='w')
            self.reg_entries[text] = entry

        btn_register = ttk.Button(self.reg_frame, text="Update/Add Student", command=self.handle_registration)
        btn_register.grid(row=len(labels)+1, column=0, columnspan=2, pady=20)

        lbl_hint = ttk.Label(self.reg_frame, text="Note: Use this to add students or update their contact info.", font=("Arial", 9, "italic"))
        lbl_hint.grid(row=len(labels)+2, column=0, columnspan=2)

    def setup_view_tab(self):
        self.view_notebook = ttk.Notebook(self.view_frame)
        self.view_notebook.pack(expand=True, fill='both', pady=10)

        # Student Master Tree
        self.master_tree = self.create_treeview(self.view_notebook, "Student Master", 
            ("ID", "Name", "Dept", "Parent", "Phone"),
            [100, 200, 100, 150, 150])

        # Attendance Tree
        self.attn_tree = self.create_treeview(self.view_notebook, "Daily Attendance", 
            ("Date", "ID", "Status", "Reason"),
            [100, 100, 100, 300])

        # Marks Tree
        self.marks_tree = self.create_treeview(self.view_notebook, "Marks Records", 
            ("ID", "Subject", "Exam", "Marks"),
            [100, 150, 150, 100])

        btn_refresh = ttk.Button(self.view_frame, text="Refresh All Records", command=self.load_all_records)
        btn_refresh.pack(pady=5)
        
        btn_archive = ttk.Button(self.view_frame, text="Archive Daily Attendance", command=self.handle_archive)
        btn_archive.pack(pady=5)

        self.load_all_records()

    def create_treeview(self, parent_notebook, tab_name, columns, widths):
        frame = ttk.Frame(parent_notebook)
        parent_notebook.add(frame, text=tab_name)
        
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width)
        
        tree.pack(expand=True, fill='both', padx=5, pady=5)
        return tree

    def handle_registration(self):
        data = {k: v.get() for k, v in self.reg_entries.items()}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required!")
            return

        success, msg = self.db.add_student(
            data["Student ID"], 
            data["Full Name"], 
            data["Department"], 
            data["Parent Name"], 
            data["Parent Mobile (WhatsApp)"]
        )
        
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh_student_lists()
            self.load_all_records()
        else:
            messagebox.showerror("Error", msg)

    def handle_attendance(self):
        selection = self.student_combo.get()
        if not selection:
            messagebox.showerror("Error", "Please select a student.")
            return

        student_id = selection.split(" - ")[0]
        status = self.status_var.get()
        reason = self.entry_reason.get() if status == "Absent" else ""

        success, msg = self.db.mark_attendance(student_id, status, reason)
        
        if success:
            if status == "Absent":
                student_info = self.db.get_student_parent_info(student_id)
                if student_info:
                    notif_success, notif_msg = self.notifier.send_absence_notification(
                        student_info['Parent Name'],
                        student_info['Name'],
                        str(student_info['Parent Phone Number']),
                        datetime.now().strftime('%Y-%m-%d'),
                        reason
                    )
                    msg += f"\n{notif_msg}"
            
            messagebox.showinfo("Success", msg)
            self.entry_reason.delete(0, tk.END)
            self.load_all_records()
        else:
            messagebox.showerror("Error", msg)

    def handle_marks(self):
        selection = self.marks_student_combo.get()
        if not selection:
            messagebox.showerror("Error", "Please select a student.")
            return

        student_id = selection.split(" - ")[0]
        subject = self.entry_subject.get()
        exam = self.entry_exam.get()
        marks = self.entry_marks.get()

        if not all([subject, exam, marks]):
            messagebox.showerror("Error", "All fields are required!")
            return

        success, msg = self.db.add_marks(student_id, subject, exam, marks)
        
        if success:
            student_info = self.db.get_student_parent_info(student_id)
            if student_info:
                notif_success, notif_msg = self.notifier.send_marks_notification(
                    student_info['Parent Name'],
                    student_info['Name'],
                    str(student_info['Parent Phone Number']),
                    subject,
                    exam,
                    marks
                )
                msg += f"\n{notif_msg}"
            
            messagebox.showinfo("Success", msg)
            # Clear entries
            self.entry_subject.delete(0, tk.END)
            self.entry_exam.delete(0, tk.END)
            self.entry_marks.delete(0, tk.END)
            self.load_all_records()
        else:
            messagebox.showerror("Error", msg)

    def handle_archive(self):
        if messagebox.askyesno("Confirm", "Archive today's attendance?"):
            self.db.archive_attendance()
            messagebox.showinfo("Success", "Records archived.")
            self.load_all_records()

    def load_all_records(self):
        # Refresh Student Master
        self.clear_tree(self.master_tree)
        df_master = self.db.get_all_students()
        for _, row in df_master.iterrows():
            self.master_tree.insert("", tk.END, values=(row['Student ID'], row['Name'], row['Department'], row['Parent Name'], row['Parent Phone Number']))

        # Refresh Attendance
        self.clear_tree(self.attn_tree)
        try:
            df_attn = pd.read_excel(self.db.file_path, sheet_name='Daily Attendance')
            for _, row in df_attn.iterrows():
                self.attn_tree.insert("", tk.END, values=(row['Date'], row['Student ID'], row['Attendance Status'], row['Reason for Leave']))
        except: pass

        # Refresh Marks
        self.clear_tree(self.marks_tree)
        try:
            df_marks = pd.read_excel(self.db.file_path, sheet_name='Marks Record')
            for _, row in df_marks.iterrows():
                self.marks_tree.insert("", tk.END, values=(row['Student ID'], row['Subject'], row['Exam Name'], row['Marks Obtained']))
        except: pass

    def clear_tree(self, tree):
        for i in tree.get_children():
            tree.delete(i)

    def refresh_student_lists(self):
        df = self.db.get_all_students()
        student_list = [f"{row['Student ID']} - {row['Name']}" for _, row in df.iterrows()]
        self.student_combo['values'] = student_list
        self.marks_student_combo['values'] = student_list

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
