from django.urls import path

from .views import (
    UserRegistrationView,
    UserVerificationEmailView,
    ResendVerificationEmailView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


userurlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("verify-email/", UserVerificationEmailView.as_view(), name="verify-email"),
    path(
        "resend-verification-code/",
        ResendVerificationEmailView.as_view(),
        name="resend-verification-code",
    ),
]
