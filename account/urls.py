from django.urls import(
    path,
    include
)

from account.views import (
    SignUpAPIView,
    CheckNicknameDuplicateView,
    CheckEmailDuplicateView,
)

app_name = "account"

urlpatterns = [
    path("signup/", SignUpAPIView.as_view(), name="signup"),
    path('check-email/<str:email>/', CheckEmailDuplicateView.as_view(), name='check-email-duplicate'),
    path('check-nickname/<str:nickname>/', CheckNicknameDuplicateView.as_view(), name='check-nickname-duplicate'),

]