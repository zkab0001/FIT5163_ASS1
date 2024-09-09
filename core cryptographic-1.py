import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureEmailCrypto:
    def __init__(self, password):
        self.symmetric_key = self.generate_key(password)
        self.fernet = Fernet(self.symmetric_key)
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

    def generate_key(self, password):
        salt = b'salt_'  # In a real application, use a random salt and store it
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt_message(self, message):
        return self.fernet.encrypt(message.encode())

    def decrypt_message(self, encrypted_message):
        return self.fernet.decrypt(encrypted_message).decode()

    def sign_message(self, message):
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def verify_signature(self, message, signature, public_key):
        try:
            public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False

# Usage example
if __name__ == "__main__":
    crypto = SecureEmailCrypto("user_password")
    message = "Hello, this is a secure email!"
    encrypted_message = crypto.encrypt_message(message)
    signature = crypto.sign_message(message.encode())
    
    # Simulating sending and receiving
    received_encrypted_message = encrypted_message
    received_signature = signature
    
    decrypted_message = crypto.decrypt_message(received_encrypted_message)
    is_authentic = crypto.verify_signature(decrypted_message.encode(), received_signature, crypto.public_key)
    
    print(f"Decrypted message: {decrypted_message}")
    print(f"Signature verified: {is_authentic}")