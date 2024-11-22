import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_otp(length=6):
    """Generate a random OTP of specified length."""
    digits = string.digits
    otp = ''.join(random.choice(digits) for _ in range(length))
    return otp

def send_email(receiver_email, otp):
    """Send an email with the OTP to the specified receiver."""
    # Email configuration
    sender_email = "doej52762@gmail.com"
    sender_password = "rgek xubc jffw meku"  # Replace with the app password you generated

    # Create the email content
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "OTP for Government Stall Rental System Verification"

    body = (f'''Government Stall Rental System

Dear User,

We have received a request for a One-Time Password (OTP) for your account.

Your OTP code is: {otp}

Please enter this code to complete your verification process. 

If you did not request this OTP, please disregard this email and contact our support team immediately.

Thank you for using our service.

Best regards,
Government Stall Rental System Support Team''')
    message.attach(MIMEText(body, "plain"))

    # Connect to the Gmail server
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()

if __name__ == "__main__":
    # Generate OTP
    otp = generate_otp()
    print(f"Generated OTP: {otp}")

    # Send OTP via email
    recipient_email = "tanhongzheng616@gmail.com"
    send_email(recipient_email, otp)
