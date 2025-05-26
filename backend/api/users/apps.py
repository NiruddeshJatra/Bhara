from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        from authemail.models import SignupCode, PasswordResetCode
        from .tasks import send_verification_email, send_password_reset_email
        
        # Store original methods before monkey patching
        original_signup_email = SignupCode.send_signup_email
        original_password_reset_email = PasswordResetCode.send_password_reset_email

        def async_send_signup_email(self):
            print("Sending verification email for code: ", self.code)
            send_verification_email.delay(self.code)
        
        def async_send_password_reset_email(self):
            print("Sending password reset email for code: ", self.code)
            send_password_reset_email.delay(self.code)
            
        # Save original methods as attributes for reference in tasks
        SignupCode.send_signup_email.__wrapped__ = original_signup_email
        PasswordResetCode.send_password_reset_email.__wrapped__ = original_password_reset_email
        
        # Apply monkey patching
        SignupCode.send_signup_email = async_send_signup_email
        PasswordResetCode.send_password_reset_email = async_send_password_reset_email
