from twilio.rest import Client

class NotificationHandler:
    def __init__(self, account_sid=None, auth_token=None, from_number=None):
        """
        initializes the notification handler.
        For WhatsApp, from_number should be 'whatsapp:+1234567890' (Twilio sandbox number)
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.client = None
        
        if account_sid and auth_token:
            try:
                self.client = Client(account_sid, auth_token)
            except Exception as e:
                print(f"Error initializing Twilio client: {e}")

    def send_absence_notification(self, parent_name, student_name, parent_phone, date, reason):
        message_body = f"Dear Parent {parent_name}, your child {student_name} is absent today ({date}). Reason: {reason}. Please contact the college if needed."
        return self._send_whatsapp(parent_phone, message_body)

    def send_marks_notification(self, parent_name, student_name, parent_phone, subject, exam, marks):
        message_body = f"Dear Parent {parent_name}, your child {student_name} has scored {marks} in {subject} - {exam}."
        return self._send_whatsapp(parent_phone, message_body)

    def _send_whatsapp(self, to_number, body):
        # Format number for WhatsApp if not already formatted
        if not to_number.startswith('whatsapp:'):
            to_whatsapp = f"whatsapp:{to_number}"
        else:
            to_whatsapp = to_number

        if self.client and self.from_number:
            try:
                # Ensure from_number also starts with whatsapp:
                from_whatsapp = self.from_number if self.from_number.startswith('whatsapp:') else f"whatsapp:{self.from_number}"
                
                message = self.client.messages.create(
                    body=body,
                    from_=from_whatsapp,
                    to=to_whatsapp
                )
                return True, f"WhatsApp sent (SID: {message.sid})"
            except Exception as e:
                return False, f"Twilio Error: {str(e)}"
        else:
            # Mock mode for demonstration
            print(f"--- MOCK WHATSAPP SENT ---")
            print(f"To: {to_whatsapp}")
            print(f"Body: {body}")
            print(f"--------------------------")
            return True, "WhatsApp sent (Mock Mode)"
