from django.urls import path

from .views import UserRegistrationView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


userurlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
