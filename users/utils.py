import random
import string
from django.core.mail import send_mail

def generate_code():
    """Generates a 5-character alphanumeric code for verification."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

def send_verification_email(email, code, purpose='registration'):
    """Sends a verification email with the generated code."""
    subject = 'CanineRacks Verification Code'
    message = f'Your code is: {code}\n\nUse this code to complete your {purpose} process.'
    
    send_mail(
        subject=subject,
        message=message,
        from_email='canineracks@gmail.com',  # ✅ Replace with your new Gmail
        recipient_list=[email],
        fail_silently=False,
    )
