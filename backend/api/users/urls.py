from django.urls import path
from .views import CustomSignup, CustomLogin, CustomLogout, UserProfileView, ProfileCompletionView
from authemail import views as authemail_views

urlpatterns = [
    path('signup/', CustomSignup.as_view(), name='signup'),
    path('login/', CustomLogin.as_view(), name='login'),
    path('logout/', CustomLogout.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/complete/', ProfileCompletionView.as_view(), name='profile_complete'),
    path('signup/verify/', authemail_views.SignupVerify.as_view(), name='signup_verify'),
    path('password/reset/', authemail_views.PasswordReset.as_view(), name='password_reset'),
    path('password/reset/verify/', authemail_views.PasswordResetVerify.as_view(), name='password_reset_verify'),
    path('password/reset/verified/', authemail_views.PasswordResetVerified.as_view(), name='password_reset_verified'),
    path('password/change/', authemail_views.PasswordChange.as_view(), name='password_change'),
]