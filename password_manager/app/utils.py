import hashlib
import random
from flask_mail import Message
from app import mail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os


# AES Encryption and Decryption
def generate_aes_key():
    return os.urandom(32).hex()


def aes_encrypt(key, plaintext):
    key_bytes = bytes.fromhex(key)
    iv = os.urandom(16)  # Initialization vector
    cipher = Cipher(algorithms.AES(key_bytes), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return iv.hex() + ciphertext.hex()


def aes_decrypt(key, ciphertext):
    key_bytes = bytes.fromhex(key)
    iv = bytes.fromhex(ciphertext[:32])  # Extract IV
    encrypted_message = bytes.fromhex(ciphertext[32:])  # Extract encrypted content
    cipher = Cipher(algorithms.AES(key_bytes), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_message) + decryptor.finalize()


# SHA-256 Hashing
def sha256_hash(data):
    sha256 = hashlib.sha256()
    sha256.update(data.encode())
    return sha256.hexdigest()


# Binary Search Tree (BST) Implementation
class BSTNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None

    def insert(self, key, value):
        def _insert(node, key, value):
            if not node:
                return BSTNode(key, value)
            if key < node.key:
                node.left = _insert(node.left, key, value)
            elif key > node.key:
                node.right = _insert(node.right, key, value)
            return node

        self.root = _insert(self.root, key, value)

    def search(self, key):
        def _search(node, key):
            if not node:
                return None
            if key == node.key:
                return node.value
            elif key < node.key:
                return _search(node.left, key)
            else:
                return _search(node.right, key)

        return _search(self.root, key)

    def in_order(self):
        result = []

        def _in_order(node):
            if not node:
                return
            _in_order(node.left)
            result.append((node.key, node.value))
            _in_order(node.right)

        _in_order(self.root)
        return result



# Function to generate a 4-digit OTP
def generate_otp():
    return str(random.randint(1000, 9999))  # Generates a 4-digit OTP

# Function to send OTP email
def send_otp_email(user_email, otp):
    msg = MIMEMultipart()
    msg['From'] = "auth.vaultify@gmail.com"  # Use a professional sender address
    msg['To'] = user_email
    msg['Subject'] = "Your OTP Code for Vaultify"

    body = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f7fa;
                    color: #333;
                }}
                .email-container {{
                    background-color: #ffffff;
                    width: 70%;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
                    background-color: #ffffff;
                }}
                h2 {{
                    color: #007bff;
                    font-size: 30px;
                    margin-bottom: 20px;
                    font-weight: 600;
                }}
                p {{
                    font-size: 16px;
                    line-height: 1.6;
                    color: #555;
                    margin-bottom: 20px;
                }}
                .otp{{
                    align-items: center;
                    text-align: center;
                }}
                .otp-code {{
                    display: inline-block;
                    font-size: 22px;
                    font-weight: 700;
                    padding: 12px 20px;
                    background-color: #e1f5fe;
                    border-radius: 6px;
                    color: #007bff;
                    margin-bottom: 20px;

                }}
                .cta-button {{
                    display: inline-block;
                    background-color: #007bff;
                    color: #fff;
                    padding: 12px 25px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-size: 16px;
                    margin-top: 20px;
                    text-align: center;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }}
                .cta-button:hover {{
                    background-color: #0056b3;
                }}
                .footer {{
                    font-size: 12px;
                    color: #999;
                    text-align: center;
                    margin-top: 30px;
                }}
                .footer p {{
                    margin: 5px 0;
                }}
                @media (max-width: 600px) {{
                    .email-container {{
                        width: 100% !important;
                        padding: 20px !important;
                    }}
                    h2 {{
                        font-size: 26px !important;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <h2>Your OTP Code for Vaultify</h2>
                <p>Hi there,</p>
                <p>We’ve received a request to send you a one-time password (OTP) for your Vaultify account. To proceed, please use the following OTP:</p>
                <div class="otp">
                <div class="otp-code">{otp}</div>
                </div>
                <p>This code is valid for the next 5 minutes. If you did not request this code, please disregard this email.</p>

                <p>If you need assistance or have any questions, feel free to contact us at <a href="auth.vaultify@gmail.com">auth.vaultify@gmail.com</a>.</p>

                <p style="text-align:left;">Best regards,<br>The Vaultify Team</p>

                <div class="footer">
                    <p>This is an automated email. Please do not reply to this message.</p>
                    <p>Vaultify, Inc. | Ahmedabad, India</p>
                </div>
            </div>
        </body>
    </html>
    """

    msg.attach(MIMEText(body, 'html'))

    try:
        # Connect to the SMTP server
        with smtplib.SMTP('smtp-relay.brevo.com', 587) as server:
            server.starttls()  # Start TLS encryption
            server.login('845306001@smtp-brevo.com', 'Ov3QkFIK0BtXMDc5')  # Login to the server
            server.send_message(msg)  # Send the email
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

