from django.urls import path

from .views import UserRegistrationView


userurlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-register")
]
