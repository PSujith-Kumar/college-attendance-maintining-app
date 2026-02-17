from flask import Flask, jsonify, request
from flask_cors import CORS
from data_manager import DataManager
from notification_handler import NotificationHandler
from datetime import datetime
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for the web frontend

db = DataManager()
notifier = NotificationHandler()

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        df_students = db.get_all_students()
        total_students = len(df_students)
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        df_daily = pd.read_excel(db.file_path, sheet_name='Daily Attendance')
        
        present_today = len(df_daily[(df_daily['Date'] == date_str) & (df_daily['Attendance Status'] == 'Present')])
        absent_today = len(df_daily[(df_daily['Date'] == date_str) & (df_daily['Attendance Status'] == 'Absent')])
        
        # Calculate Avg Performance (Mocking actual calculation logic from Marks Record)
        df_marks = pd.read_excel(db.file_path, sheet_name='Marks Record')
        if not df_marks.empty:
            avg_marks = f"{round(pd.to_numeric(df_marks['Marks Obtained'], errors='coerce').mean(), 1)}%"
        else:
            avg_marks = "0%"

        return jsonify({
            "total_students": total_students,
            "present_today": present_today,
            "absent_today": absent_today,
            "avg_marks": avg_marks
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/attendance/today', methods=['GET'])
def get_today_attendance():
    try:
        date_str = datetime.now().strftime('%Y-%m-%d')
        df_students = db.get_all_students()
        df_daily = pd.read_excel(db.file_path, sheet_name='Daily Attendance')
        
        # Merge students with their today's attendance
        df_today = df_daily[df_daily['Date'] == date_str]
        
        # Combine
        records = []
        for _, s in df_students.iterrows():
            att = df_today[df_today['Student ID'].astype(str) == str(s['Student ID'])]
            records.append({
                "Student ID": s['Student ID'],
                "Name": s['Name'],
                "Status": att.iloc[0]['Attendance Status'] if not att.empty else "Pending"
            })
            
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/students', methods=['GET'])
def get_students():
    try:
        df = db.get_all_students()
        students = df.to_dict(orient='records')
        return jsonify(students)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    student_id = data.get('student_id')
    status = data.get('status')
    reason = data.get('reason', '')
    
    success, msg = db.mark_attendance(student_id, status, reason)
    
    if success and status == 'Absent':
        student_info = db.get_student_parent_info(student_id)
        if student_info:
            notifier.send_absence_notification(
                student_info['Parent Name'],
                student_info['Name'],
                str(student_info['Parent Phone Number']),
                datetime.now().strftime('%Y-%m-%d'),
                reason
            )
            
    return jsonify({"success": success, "message": msg})

@app.route('/api/marks', methods=['POST'])
def add_marks():
    data = request.json
    student_id = data.get('student_id')
    subject = data.get('subject')
    exam = data.get('exam')
    marks = data.get('marks')
    
    success, msg = db.add_marks(student_id, subject, exam, marks)
    
    if success:
        student_info = db.get_student_parent_info(student_id)
        if student_info:
            notifier.send_marks_notification(
                student_info['Parent Name'],
                student_info['Name'],
                str(student_info['Parent Phone Number']),
                subject,
                exam,
                marks
            )
            
    return jsonify({"success": success, "message": msg})

if __name__ == '__main__':
    # Run on all interfaces so the APK can connect via IP
    app.run(host='0.0.0.0', port=5000, debug=True)
