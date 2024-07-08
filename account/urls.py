from django.urls import(
    path,
    include
)

from account.views import (
    SignUpAPIView,
    CheckNicknameDuplicateView,
    LoginView,
    LogoutView,
    UserProfileRetrieveView,
    UserProfileUpdateView,
    PasswordResetView,
    PasswordResetConfirmView,
    VerifyUserEmailView
)

app_name = "account"

urlpatterns = [
    path("signup/", SignUpAPIView.as_view(), name="signup"),
    path('check-nickname/<str:nickname>/', CheckNicknameDuplicateView.as_view(), name='check-nickname-duplicate'),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('profile/', UserProfileRetrieveView.as_view(), name='profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('verify-email/<uidb64>/<token>/', VerifyUserEmailView.as_view(), name='verify_email'),
]