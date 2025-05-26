from celery import shared_task
from authemail.models import SignupCode, PasswordResetCode
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
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
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        verification_url = f"{frontend_url}/verify-email?code={code}"
        
        # Prepare context for templates
        context = {
            'user': signup_code.user,
            'verification_url': verification_url,
            'frontend_url': frontend_url,
            'code': code
        }
        
        # Render email content from templates
        subject = render_to_string('authemail/signup_email_subject.txt', context).strip()
        text_content = render_to_string('authemail/signup_email.txt', context)
        html_content = render_to_string('authemail/signup_email.html', context)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[signup_code.user.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send(fail_silently=False)
        logger.info(f"SUCCESS: Verification email sent to {signup_code.user.email}")
        
    except SignupCode.DoesNotExist:
        logger.error(f"Signup code not found for code: {code}")
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"ERROR: Failed to send verification email. Error: {str(e)}")

@shared_task
def send_password_reset_email(code):
    """
    Send password reset email to user with the given code.
    
    Args:
        code: PasswordResetCode primary key
    """
    logger.info(f"TASK RECEIVED: Attempting to send password reset email for code={code}")
    
    try:
        if not code:
            logger.warning("Missing required parameter: code")
            return
        
        logger.info(f"Looking up PasswordResetCode with code={code}")
        password_reset_code = PasswordResetCode.objects.get(code=code)
        
        # Build reset URL - this can be configured in settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        reset_url = f"{frontend_url}/reset-password?code={code}"
        
        # Prepare context for templates
        context = {
            'user': password_reset_code.user,
            'reset_url': reset_url,
            'frontend_url': frontend_url,
            'code': code
        }
        
        # Render email content from templates
        subject = render_to_string('authemail/password_reset_email_subject.txt', context).strip()
        text_content = render_to_string('authemail/password_reset_email.txt', context)
        html_content = render_to_string('authemail/password_reset_email.html', context)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[password_reset_code.user.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send(fail_silently=False)
        logger.info(f"SUCCESS: Password reset email sent to {password_reset_code.user.email}")
        
    except PasswordResetCode.DoesNotExist:
        logger.error(f"Password reset code not found for code: {code}")
    except Exception as e:
        logger.error(f"Error sending password reset email: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"ERROR: Failed to send password reset email. Error: {str(e)}")
        