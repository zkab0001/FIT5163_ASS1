from secure_email_app import SecureEmailApp

def main():
    print("Welcome to the Secure Email Application!")
    email = input("Enter your email address: ")
    password = input("Enter your email password: ")
    crypto_password = input("Enter a password for encryption: ")
    
    app = SecureEmailApp(email, password, 'smtp.example.com', 587, 'imap.example.com', 993, crypto_password)
    
    while True:
        print("\n1. Send secure email")
        print("2. Check secure emails")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            to_email = input("Enter recipient's email: ")
            subject = input("Enter email subject: ")
            body = input("Enter email body: ")
            app.send_secure_email(to_email, subject, body)
            print("Secure email sent!")
        
        elif choice == '2':
            print("\nChecking secure emails...")
            for email in app.receive_secure_emails():
                print(f"\nSubject: {email['subject']}")
                print(f"From: {email['sender']}")
                print(f"Body: {email['body']}")
                print(f"Verified: {email['verified']}")
        
        elif choice == '3':
            print("Thank you for using the Secure Email Application!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()