# jarvis.py — RMKCET Marks Sender (Excel -> WhatsApp)
# Opens installed WhatsApp Desktop first; if not found, falls back to browser.
# Supports GUI and optional voice activation.

import os
import threading
import queue
import webbrowser
import re
import time
import subprocess
import sys
from datetime import datetime
import urllib.parse
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox

# Optional speech + TTS
try:
    import speech_recognition as sr
except Exception:
    sr = None

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

# Excel handling
try:
    import pandas as pd
except Exception:
    pd = None

# ---------------- CONFIG ----------------
SPEAK_RATE = 165
WAKE_WORD = "hey jarvis"
SEND_DELAY_BETWEEN = 1.0
DEFAULT_EXCEL_PATH = r"C:\Users\tirup\Documents\marks.xlsx"

# ---------------- UTILITIES ----------------
def tts_speak(text: str):
    if not pyttsx3:
        return
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", SPEAK_RATE)
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass


def sanitize_number_for_wame(raw):
    """Return numeric digits only (wa.me and whatsapp:// both need plain digits)."""
    if raw is None:
        return ""
    return re.sub(r"[^\d]", "", str(raw))


def open_whatsapp_chat(number: str, message: str):
    """
    Try opening WhatsApp Desktop using URI scheme first.
    If that fails, fallback to browser (https://wa.me/).
    """
    num = sanitize_number_for_wame(number)
    if not num:
        return False

    encoded = urllib.parse.quote_plus(message)

    # Try WhatsApp Desktop (URI scheme)
    desktop_uri = f"whatsapp://send?phone={num}&text={encoded}"
    web_fallback = f"https://wa.me/{num}?text={encoded}"

    try:
        if sys.platform.startswith("win"):
            os.startfile(desktop_uri)  # opens via Windows URI handler
        else:
            subprocess.Popen(["xdg-open", desktop_uri])
        return True
    except Exception:
        try:
            webbrowser.open(web_fallback)
            return True
        except Exception:
            return False


def find_excel_file(default_path=None):
    """Return path to Excel file: try default_path first, then ask user via file dialog."""
    if default_path and os.path.isfile(default_path):
        return os.path.abspath(default_path)

    guesses = ["marks.xlsx", "students.xlsx", "student_marks.xlsx"]
    for g in guesses:
        if os.path.isfile(g):
            return os.path.abspath(g)

    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Select Excel file with student marks",
        filetypes=[("Excel files", "*.xlsx;*.xls")],
    )
    try:
        root.destroy()
    except Exception:
        pass
    return path or None


# ---------------- MESSAGE BUILDER ----------------
def build_message_whatsapp_format(whatsapp_no, reg_no, name, marks_dict):
    """Generate WhatsApp message in RMKCET format."""
    lines = [
        f"WHATSAPP NUMBER : {whatsapp_no if whatsapp_no else ''}",
        "Dear Student/Parent :",
        f"REG_NO : {reg_no if reg_no else ''}",
        f"NAME : {name if name else ''}",
    ]
    for subj, val in marks_dict.items():
        lines.append(f"{subj} : {val if val else ''}")
    lines.append("")
    lines.append("Regards,")
    lines.append("PRINCIPAL")
    lines.append("")
    lines.append("RMKCET")
    return "\n".join(lines)


# ---------------- EXCEL HANDLING ----------------
def detect_required_columns(df):
    headers = [str(c).strip() for c in df.columns]
    lower = [h.lower() for h in headers]

    def find_by_tokens(tokens):
        for i, h in enumerate(lower):
            for t in tokens:
                if t in h:
                    return headers[i]
        return None

    reg_col = find_by_tokens(["reg_no", "regno", "reg no", "reg"])
    name_col = find_by_tokens(["name", "student"])
    phone_col = find_by_tokens(["whatsapp", "parent", "phone", "mobile", "contact"])

    if not name_col:
        name_col = headers[0]
    if not phone_col:
        phone_col = headers[-1]

    # Dynamically pick up other columns as "subjects" (heuristic: columns not already used)
    used_cols = [reg_col, name_col, phone_col]
    subjects_found = {}
    for col in headers:
        if col not in used_cols and col.lower() not in ["email", "address", "gender"]:
            subjects_found[col] = col

    return {
        "reg_col": reg_col,
        "name_col": name_col,
        "phone_col": phone_col,
        "subjects": subjects_found,
    }


def send_marks_from_excel(path=None, gui_write=None):
    """Read Excel and open WhatsApp chats with pre-filled messages."""
    def gw(text):
        if gui_write:
            gui_write("Jarvis", text)
        else:
            print(text)

    if pd is None:
        gw("pandas not installed. Please install pandas and openpyxl.")
        return

    if not path:
        path = find_excel_file(DEFAULT_EXCEL_PATH)
    if not path or not os.path.isfile(path):
        gw("No Excel file selected or found.")
        return

    gw(f"Reading Excel file: {path}")
    try:
        df = pd.read_excel(path)
    except Exception as e:
        gw(f"Failed to read Excel file: {e}")
        return

    if df.empty:
        gw("Excel file is empty.")
        return

    cols = detect_required_columns(df)
    reg_col = cols["reg_col"]
    name_col = cols["name_col"]
    phone_col = cols["phone_col"]
    subj_map = cols["subjects"]

    gw(f"Using columns -> REG: '{reg_col}', NAME: '{name_col}', PHONE: '{phone_col}'.")
    gw(f"Subjects: {list(subj_map.keys())}")

    success, failed = 0, 0
    for idx, row in df.iterrows():
        try:
            reg_no = row.get(reg_col, "")
            name = row.get(name_col, "")
            phone = row.get(phone_col, "")

            marks = {}
            for subj, col in subj_map.items():
                val = row.get(col, "") if col and col in df.columns else ""
                marks[subj] = "" if pd.isna(val) else val

            if not phone or str(phone).strip().lower() == "nan":
                gw(f"Skipping row {idx} ({name}) — no phone number.")
                failed += 1
                continue

            message = build_message_whatsapp_format(phone, reg_no, name, marks)
            opened = open_whatsapp_chat(phone, message)
            if opened:
                gw(f"Opened WhatsApp chat for {name} ({phone}).")
                success += 1
            else:
                gw(f"Failed to open WhatsApp for {name} ({phone}).")
                failed += 1

            time.sleep(SEND_DELAY_BETWEEN)
        except Exception as e:
            gw(f"Error processing row {idx}: {e}")
            failed += 1

    gw(f"Done. Opened chats for {success} students; {failed} failed/skipped.")


# ---------------- COMMAND HANDLER ----------------
def handle_command(cmd: str, gui_write=None):
    if not cmd or not cmd.strip():
        return "No command."

    c = cmd.lower().strip()

    if "time" in c:
        return f"The time is {datetime.now().strftime('%H:%M:%S')}"
    if "date" in c:
        return f"Today's date is {datetime.now().strftime('%Y-%m-%d')}"

    if "send" in c and "marks" in c and "whatsapp" in c:
        threading.Thread(target=send_marks_from_excel, args=(None, gui_write), daemon=True).start()
        return "Preparing to open WhatsApp chats for student marks..."

    return "Sorry, I didn’t understand that."


# ---------------- GUI ----------------
class JarvisGUI:
    def __init__(self, root):
        self.root = root
        root.title("Jarvis - RMKCET Marks Sender")
        root.geometry("820x600")
        root.configure(bg="#0b0f13")

        self.chat = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, bg="#07111a", fg="#7fffd4",
            font=("Consolas", 12), state=tk.NORMAL
        )
        self.chat.pack(padx=12, pady=(12, 6), fill=tk.BOTH, expand=True)
        self.chat.insert(tk.END, "Jarvis: Ready. Say 'Hey Jarvis' or type a command.\n")

        controls = tk.Frame(root, bg="#0b0f13")
        controls.pack(fill=tk.X, padx=12, pady=(0, 12))

        self.entry = tk.Entry(controls, font=("Consolas", 12), width=64)
        self.entry.pack(side=tk.LEFT, padx=(0, 8), expand=True, fill=tk.X)
        self.entry.bind("<Return>", lambda e: self.on_send())

        send_btn = ttk.Button(controls, text="Send", command=self.on_send)
        send_btn.pack(side=tk.LEFT)

        file_btn = ttk.Button(
            controls,
            text="Send marks → WhatsApp (choose file if needed)",
            command=self.on_send_marks_button,
        )
        file_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.q = queue.Queue()
        self._poll_queue()

    def _write(self, who, text):
        self.chat.insert(tk.END, f"\n{who}: {text}\n")
        self.chat.see(tk.END)
        if who == "Jarvis":
            threading.Thread(target=tts_speak, args=(text,), daemon=True).start()

    def on_send(self):
        txt = self.entry.get().strip()
        if not txt:
            return
        self._write("You", txt)
        res = handle_command(txt, gui_write=self._write)
        self._write("Jarvis", res)
        self.entry.delete(0, tk.END)

    def on_send_marks_button(self):
        path = find_excel_file(DEFAULT_EXCEL_PATH)
        if not path:
            self._write("Jarvis", "No Excel file chosen.")
            return
        self._write("Jarvis", f"Starting to open WhatsApp chats from {path} ...")
        threading.Thread(target=lambda: send_marks_from_excel(path, gui_write=self._write), daemon=True).start()

    def _poll_queue(self):
        try:
            while True:
                text = self.q.get_nowait()
                self._write("You", text)
                res = handle_command(text, gui_write=self._write)
                self._write("Jarvis", res)
        except queue.Empty:
            pass
        self.root.after(200, self._poll_queue)


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisGUI(root)
    root.mainloop()
