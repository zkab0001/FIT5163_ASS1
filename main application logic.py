from secure_email_crypto import SecureEmailCrypto
from email_handler import EmailHandler

class SecureEmailApp:
    def __init__(self, email_address, email_password, smtp_server, smtp_port, imap_server, imap_port, crypto_password):
        self.email_handler = EmailHandler(email_address, email_password, smtp_server, smtp_port, imap_server, imap_port)
        self.crypto = SecureEmailCrypto(crypto_password)
        self.trust_list = set()

    def send_secure_email(self, to_email, subject, body):
        encrypted_body = self.crypto.encrypt_message(body)
        signature = self.crypto.sign_message(body.encode())
        full_body = f"{encrypted_body.decode()}|||{signature.hex()}"
        self.email_handler.send_email(to_email, subject, full_body)

    def receive_secure_emails(self):
        for email in self.email_handler.receive_emails():
            try:
                encrypted_body, signature = email['body'].split('|||')
                decrypted_body = self.crypto.decrypt_message(encrypted_body.encode())
                is_authentic = self.crypto.verify_signature(decrypted_body.encode(), bytes.fromhex(signature), self.crypto.public_key)
                
                if is_authentic:
                    if email['sender'] not in self.trust_list:
                        self.trust_list.add(email['sender'])
                    yield {'subject': email['subject'], 'sender': email['sender'], 'body': decrypted_body, 'verified': True}
                else:
                    yield {'subject': email['subject'], 'sender': email['sender'], 'body': decrypted_body, 'verified': False}
            except:
                yield {'subject': email['subject'], 'sender': email['sender'], 'body': "Unable to decrypt message", 'verified': False}

# Usage example
if __name__ == "__main__":
    app = SecureEmailApp('your_email@example.com', 'your_password', 'smtp.example.com', 587, 'imap.example.com', 993, 'crypto_password')
    
    # Sending a secure email
    app.send_secure_email('recipient@example.com', 'Secure Test', 'This is a secure test email')
    
    # Receiving and decrypting secure emails
    for email in app.receive_secure_emails():
        print(f"Subject: {email['subject']}")
        print(f"From: {email['sender']}")
        print(f"Body: {email['body']}")
        print(f"Verified: {email['verified']}\n")