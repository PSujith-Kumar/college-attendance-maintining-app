import pandas as pd
import os
from datetime import datetime

class DataManager:
    def __init__(self, file_path='attendance.xlsx'):
        self.file_path = file_path
        self._initialize_excel()

    def _initialize_excel(self):
        if not os.path.exists(self.file_path):
            with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
                # Sheet 1 – Student Master
                df_master = pd.DataFrame(columns=['Student ID', 'Name', 'Department', 'Parent Name', 'Parent Phone Number'])
                df_master.to_excel(writer, sheet_name='Student Master', index=False)
                
                # Sheet 2 – Daily Attendance
                df_daily = pd.DataFrame(columns=['Date', 'Student ID', 'Attendance Status', 'Reason for Leave'])
                df_daily.to_excel(writer, sheet_name='Daily Attendance', index=False)
                
                # Sheet 3 – Attendance History
                df_history = pd.DataFrame(columns=['Date', 'Student ID', 'Attendance Status', 'Reason for Leave'])
                df_history.to_excel(writer, sheet_name='Attendance History', index=False)

                # Sheet 4 – Marks Record
                df_marks = pd.DataFrame(columns=['Student ID', 'Subject', 'Exam Name', 'Marks Obtained'])
                df_marks.to_excel(writer, sheet_name='Marks Record', index=False)
            print(f"Initialized {self.file_path}")

    def add_student(self, student_id, name, dept, parent_name, parent_phone):
        df_master = pd.read_excel(self.file_path, sheet_name='Student Master')
        if student_id in df_master['Student ID'].values:
            # Update existing student if ID exists
            idx = df_master.index[df_master['Student ID'] == student_id].tolist()[0]
            df_master.loc[idx, 'Name'] = name
            df_master.loc[idx, 'Department'] = dept
            df_master.loc[idx, 'Parent Name'] = parent_name
            df_master.loc[idx, 'Parent Phone Number'] = parent_phone
            msg = "Student info updated."
        else:
            new_student = {
                'Student ID': student_id,
                'Name': name,
                'Department': dept,
                'Parent Name': parent_name,
                'Parent Phone Number': parent_phone
            }
            df_master = pd.concat([df_master, pd.DataFrame([new_student])], ignore_index=True)
            msg = "Student added successfully."
        
        with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_master.to_excel(writer, sheet_name='Student Master', index=False)
        return True, msg

    def get_all_students(self):
        return pd.read_excel(self.file_path, sheet_name='Student Master')

    def mark_attendance(self, student_id, status, reason=''):
        date_str = datetime.now().strftime('%Y-%m-%d')
        df_daily = pd.read_excel(self.file_path, sheet_name='Daily Attendance')
        
        # Check if already marked for today
        mask = (df_daily['Date'] == date_str) & (df_daily['Student ID'] == student_id)
        if not df_daily[mask].empty:
            return False, "Attendance already marked for this student today."

        # Add entry
        new_entry = {
            'Date': date_str,
            'Student ID': student_id,
            'Attendance Status': status,
            'Reason for Leave': reason if status == 'Absent' else ''
        }
        df_daily = pd.concat([df_daily, pd.DataFrame([new_entry])], ignore_index=True)

        with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_daily.to_excel(writer, sheet_name='Daily Attendance', index=False)
        
        return True, "Attendance marked."

    def add_marks(self, student_id, subject, exam, marks):
        df_marks = pd.read_excel(self.file_path, sheet_name='Marks Record')
        
        new_mark = {
            'Student ID': student_id,
            'Subject': subject,
            'Exam Name': exam,
            'Marks Obtained': marks
        }
        df_marks = pd.concat([df_marks, pd.DataFrame([new_mark])], ignore_index=True)
        
        with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_marks.to_excel(writer, sheet_name='Marks Record', index=False)
        return True, "Marks recorded."

    def get_student_parent_info(self, student_id):
        df_master = pd.read_excel(self.file_path, sheet_name='Student Master')
        # Ensure student_id is compared correctly (as string or int depending on storage)
        student = df_master[df_master['Student ID'].astype(str) == str(student_id)]
        if not student.empty:
            return student.iloc[0].to_dict()
        return None

    def archive_attendance(self):
        df_daily = pd.read_excel(self.file_path, sheet_name='Daily Attendance')
        df_history = pd.read_excel(self.file_path, sheet_name='Attendance History')
        
        df_history = pd.concat([df_history, df_daily], ignore_index=True)
        
        # Clear daily attendance
        df_daily_empty = pd.DataFrame(columns=['Date', 'Student ID', 'Attendance Status', 'Reason for Leave'])
        
        with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_history.to_excel(writer, sheet_name='Attendance History', index=False)
            df_daily_empty.to_excel(writer, sheet_name='Daily Attendance', index=False)
        return True

