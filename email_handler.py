import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import base64

class EmailHandler:
    def __init__(self, email_address, email_password, smtp_server, smtp_port, imap_server, imap_port):
        self.email_address = email_address
        self.email_password = email_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_server = imap_server
        self.imap_port = imap_port

    def send_email(self, to_email, subject, encrypted_body, signature=None, public_key=None):
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = to_email
        msg['Subject'] = subject

        payload = {
            'encrypted_body': base64.b64encode(encrypted_body).decode(),
            'signature': base64.b64encode(signature).decode() if signature else None,
            'public_key': public_key.decode() if public_key else None
        }
        msg.attach(MIMEText(json.dumps(payload), 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            print(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"An error occurred while sending email: {e}")
            return False

    def receive_emails(self):
        try:
            with imaplib.IMAP4_SSL(self.imap_server, self.imap_port) as server:
                server.login(self.email_address, self.email_password)
                server.select('inbox')
                
                _, message_numbers = server.search(None, 'ALL')
                message_numbers = message_numbers[0].split()
                
                for num in reversed(message_numbers[-10:]):  # Process the 10 most recent emails
                    try:
                        print(f"Fetching email with ID: {num.decode()}")
                        _, msg = server.fetch(num, '(RFC822)')
                        email_body = msg[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        subject = email_message['subject']
                        sender = email_message['from']
                        print(f"Processing email - Subject: {subject}, From: {sender}")
                        
                        payload = None
                        if email_message.is_multipart():
                            for part in email_message.walk():
                                if part.get_content_type() == "text/plain":
                                    try:
                                        payload = json.loads(part.get_payload())
                                        print("Multipart email payload found")
                                        break
                                    except json.JSONDecodeError as e:
                                        print(f"JSONDecodeError for multipart email {num}: {e}")
                                        print(f"Raw payload: {part.get_payload()}")
                        else:
                            try:
                                payload = json.loads(email_message.get_payload())
                                print("Single part email payload found")
                            except json.JSONDecodeError as e:
                                print(f"JSONDecodeError for single part email {num}: {e}")
                                print(f"Raw payload: {email_message.get_payload()}")
                        
                        if payload is None:
                            print(f"No valid payload found for email {num}")
                            continue
                        
                        if 'encrypted_body' not in payload:
                            print(f"Email {num} is not a secure email (no encrypted body)")
                            continue
                        
                        yield {
                            'subject': subject,
                            'sender': sender,
                            'encrypted_body': base64.b64decode(payload['encrypted_body']),
                            'signature': base64.b64decode(payload['signature']) if payload.get('signature') else None,
                            'public_key': payload.get('public_key')
                        }
                    except Exception as e:
                        print(f"Error processing email {num}: {e}")
        except Exception as e:
            print(f"An error occurred while receiving emails: {e}")
            return []
