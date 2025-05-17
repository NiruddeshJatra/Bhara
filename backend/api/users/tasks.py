from celery import shared_task
from authemail.models import SignupCode, PasswordResetCode

@shared_task
def send_verification_email(code_id):
    try:
        code = SignupCode.objects.get(id=code_id)
        code.send_signup_email()
    except SignupCode.DoesNotExist:
        pass

@shared_task
def send_password_reset_email(code_id):
    try:
        code = PasswordResetCode.objects.get(id=code_id)
        code.send_password_reset_email()
    except PasswordResetCode.DoesNotExist:
        pass
