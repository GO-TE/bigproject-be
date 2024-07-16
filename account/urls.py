import account.views
from django.urls import(
    path,
    include
)

from rest_framework_simplejwt.views import TokenRefreshView

from account.views import (
    SignUpAPIView,
    CheckNicknameDuplicateView,
    CheckEmailDuplicateView,
    LoginView,
    LogoutView,
    UserProfileRetrieveView,
    UserProfileUpdateView,
    PasswordResetView,
    PasswordResetConfirmView,
    VerifyUserEmailView,
    ActivateUserAccountView,
    GoogleLogin
)

app_name = "account"

urlpatterns = [
    path("signup/", SignUpAPIView.as_view(), name="signup"),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('profile/', UserProfileRetrieveView.as_view(), name='profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('verify-email/', VerifyUserEmailView.as_view(), name='verify_email'),
    path('activate/<uidb64>/<token>/', ActivateUserAccountView.as_view(), name='account_activate'),
    path('check-email/', CheckEmailDuplicateView.as_view(), name='check-email-duplicate'),
    path('check-nickname/', CheckNicknameDuplicateView.as_view(), name='check_nickname_duplicate'),
    path('google/login/', GoogleLogin.as_view(), name='google-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]