from celery import shared_task
from authemail.models import SignupCode, PasswordResetCode
from django.core.mail import send_mail
from django.conf import settings
import logging
import traceback

# Get an instance of a logger
logger = logging.getLogger(__name__)

@shared_task
def send_verification_email(user_id, code):
    """
    Send verification email to user with the given code.
    
    Args:
        user_id: User ID 
        code: SignupCode primary key
    """
    logger.info(f"TASK RECEIVED: Attempting to send verification email for user_id={user_id}, code={code}")
    
    try:
        if not code or not user_id:
            logger.warning(f"Missing required parameters: user_id={user_id}, code={code}")
            return
        
        logger.info(f"Looking up SignupCode with code={code}")
        signup_code = SignupCode.objects.get(code=code)
        
        # Verify that the signup code belongs to the correct user
        if str(signup_code.user.id) != str(user_id):
            logger.warning(f"User ID mismatch for code: {code}. Expected {user_id}, got {signup_code.user.id}")
            return
        
        # Build verification URLs - these can be configured in settings
        backend_url = getattr(settings, 'BACKEND_URL', 'http://localhost:8000')
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        
        # For testing with Postman, use the backend verification URL
        backend_verification_url = f"{backend_url}/auth/signup/verify/?code={code}"
        
        # For production, this would be the frontend URL
        frontend_verification_url = f"{frontend_url}/verify-email?code={code}"
        
        # For testing purposes, use the backend URL that works with Postman
        verification_url = backend_verification_url
        
        logger.info(f"Sending email to {signup_code.user.email}")
        send_mail(
            subject='Verify Your Email Address - Bhara',
            message=f'Hello {signup_code.user.first_name},\n\n'
                    f'Thank you for signing up with Bhara! To complete your registration and verify your email address, please click on the link below:\n\n'
                    f'{verification_url}\n\n'
                    f'This link will expire in 24 hours.\n\n'
                    f'If you did not sign up for a Bhara account, please ignore this email.\n\n'
                    f'Best regards,\n'
                    f'The Bhara Team',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[signup_code.user.email],
            fail_silently=False,
        )
        logger.info(f"SUCCESS: Verification email sent to {signup_code.user.email}")
    except SignupCode.DoesNotExist:
        logger.error(f"Signup code not found for code: {code}")
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"ERROR: Failed to send verification email. Error: {str(e)}")

@shared_task
def send_password_reset_email(code):
    try:
        if not code:
            print("Warning: No code provided")
            return
        
        password_reset_code = PasswordResetCode.objects.get(code=code)
        send_mail(
            subject='Reset Your Password - Bhara',
            message=f'Hello {password_reset_code.user.first_name},\n\n'
                    f'You have requested to reset your password. To reset your password, please click on the link below:\n\n'
                    f'http://localhost:3000/reset-password?code={code}\n\n'
                    f'This link will expire in 24 hours.\n\n'
                    f'If you did not request a password reset, please ignore this email.\n\n'
                    f'Best regards,\n'
                    f'The Bhara Team',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[password_reset_code.user.email],
            fail_silently=False,
        )
        print(f"Successfully sent password reset email for code: {code}")
    except PasswordResetCode.DoesNotExist:
        print(f"Password reset code not found for code: {code}")
    except Exception as e:
        print(f"Failed to send password reset email for code: {code}. Error: {str(e)}")
        
{
    "token": "948db55716f83386e9e0f49e87c29d40fa811074",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0ODUxNjQ1OSwiaWF0IjoxNzQ4MjU3MjU5LCJqdGkiOiJmZTU4MGE2ZGEzMTA0ZjAyODAxYWQxYThiMmY0ZTg2NiIsInVzZXJfaWQiOiI1YTI2ZTA5MS1jZDQ0LTRkY2ItYmU1ZS0wNGUxYTNkODg1YmYifQ.t5ObmWMWrFTZyA4zZAhy-wtA_90XjyzYlWoIH4XRqBc",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ4MjYwODU5LCJpYXQiOjE3NDgyNTcyNTksImp0aSI6IjlkOTJjNTQzODRmMDRkOTY5YTMwZGM0ZmVkZTE0MTk2IiwidXNlcl9pZCI6IjVhMjZlMDkxLWNkNDQtNGRjYi1iZTVlLTA0ZTFhM2Q4ODViZiJ9.OCUj0G01aKDDTcbo6FXJ2N8kMq5LK1NhmEwdMFq2wA4"
}