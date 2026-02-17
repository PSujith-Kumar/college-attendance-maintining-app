# College Attendance & Marks Management System (WhatsApp)

A comprehensive Python application designed for college staff to manage student records, track daily attendance, record marks, and automatically notify parents via **WhatsApp**.

## Project Interfaces
1.  **Premium Web Dashboard** (Recommended): Modern, high-performance web interface located in `/web`.
2.  **JARVIS Marks Sender**: specialized orbital-themed marks dispatcher (`jarvis_marks_sender.html`).
3.  **Desktop App**: Original Python Tkinter interface (`app.py`).

## Key Features
- **Premium Web Interface**: Next-gen dashboard with real-time WhatsApp message preview and "JARVIS Protocol" dispatch.
- **Student Master Data**: Centralized storage for 720+ students.
- **Daily Attendance**: Easy marking for staff with "Reason for Absence" tracking.
- **Excel Smart-Mapping**: Automatically detect headers like "Reg No" or "Score" from spreadsheets.
- **Auto WhatsApp Alerts**: 
  - Instant alerts for absent students.
  - Grade/Marks reports sent directly to parents.
- **Excel Database**: All data is stored in `attendance.xlsx` across four specialized sheets.

## Setup Instructions

### 1. Requirements
Ensure you have Python installed, then run:
```bash
python -m pip install pandas openpyxl twilio
```

### 2. WhatsApp API Configuration (Twilio)
This app uses the **Twilio WhatsApp Business API**. 
1. Sign up at [Twilio](https://www.twilio.com).
2. Go to the **Messaging > Try it Out > Send a WhatsApp message** section to enable the sandbox.
3. Update `app.py` in the `__init__` method:
   ```python
   self.notifier = NotificationHandler(
       account_sid='YOUR_ACCOUNT_SID',
       auth_token='YOUR_AUTH_TOKEN',
       from_number='whatsapp:+14155238886' # Your Twilio Sandbox Number
   )
   ```
*If left blank, the app will run in **Mock Mode**, printing messages to the terminal for testing.*

### 3. Running the Web Dashboard (Recommended)
The premium web interface provides the best experience:
```bash
# Terminal 1: Start the API Server
python server.py

# Terminal 2: Start the Web Dashboard
cd web
npm install
npm run dev
```

### 4. Desktop App & Legacy Tools
- **Main GUI**: `python app.py`
- **JARVIS Assistant**: `python jarvis.py`
- **Legacy Marks Sender**: Open `jarvis_marks_sender.html` in any browser.

## Usage Guide
1. **Student Data**: Use the "Student Data" tab to populate or update student and parent info.
2. **Mark Attendance**: Select a student, set status, and click "Mark & Notify".
3. **Marks Entry**: Choose a student, Enter Subject, Exam, and Marks.
4. **View Records**: Monitor all data across different sheets.

## Technical Architecture
- **GUI**: Python Tkinter (Professional & implementation-ready).
- **Backend**: Python Logic with `pandas` for Excel manipulation.
- **Storage**: `attendance.xlsx` (Multi-sheet database).
- **API**: Twilio REST API for WhatsApp.

## Excel Structure (`attendance.xlsx`)
1. **Student Master**: Permanent ID, Name, Dept, Parent Contact.
2. **Daily Attendance**: Date-wise presence/absence.
3. **Attendance History**: Archived records.
4. **Marks Record**: Subject-wise academic performance logs.
