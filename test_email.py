from django.core.mail import send_mail
from django.conf import settings

def test_email_sending():
    try:
        # Test email configuration with dummy email
        subject = 'Test Email from Road Complaint Portal'
        message = 'This is a test email to verify the email configuration.'
        from_email = 'dummy@example.com'
        recipient_list = ['test@example.com']  # Dummy recipient
        
        # Send the email
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        print("Test email would be sent in production. In development, it's printed to console.")
        return True
    except Exception as e:
        print(f"Error in email configuration: {str(e)}")
        return False

if __name__ == "__main__":
    test_email_sending() 