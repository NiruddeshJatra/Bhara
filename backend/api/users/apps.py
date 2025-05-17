from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        from authemail.models import SignupCode, PasswordResetCode
        from .tasks import send_verification_email, send_password_reset_email

        def async_send_signup_email(self):
            send_verification_email.delay(self.id)
        
        def async_send_password_reset_email(self):
            send_password_reset_email.delay(self.id)
        
        SignupCode.send_signup_email = async_send_signup_email
        PasswordResetCode.send_password_reset_email = async_send_password_reset_email
