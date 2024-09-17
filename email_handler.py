import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailHandler:
    def __init__(self, email_address, email_password, smtp_server, smtp_port, imap_server, imap_port):
        self.email_address = email_address
        self.email_password = email_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_server = imap_server
        self.imap_port = imap_port

    def send_email(self, to_email, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)

    def receive_emails(self):
        with imaplib.IMAP4_SSL(self.imap_server, self.imap_port) as server:
            server.login(self.email_address, self.email_password)
            server.select('inbox')
            _, message_numbers = server.search(None, 'ALL')
            
            for num in message_numbers[0].split():
                _, msg = server.fetch(num, '(RFC822)')
                email_body = msg[0][1]
                email_message = email.message_from_bytes(email_body)
                
                subject = email_message['subject']
                sender = email_message['from']
                
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                else:
                    body = email_message.get_payload(decode=True).decode()
                
                yield {'subject': subject, 'sender': sender, 'body': body}

# Usage example
if __name__ == "__main__":
    handler = EmailHandler('your_email@example.com', 'your_password', 'smtp.example.com', 587, 'imap.example.com', 993)
    
    # Sending an email
    handler.send_email('recipient@example.com', 'Test Subject', 'This is a test email body')
    
    # Receiving emails
    for email in handler.receive_emails():
        print(f"Subject: {email['subject']}")
        print(f"From: {email['sender']}")
        print(f"Body: {email['body']}\n")
