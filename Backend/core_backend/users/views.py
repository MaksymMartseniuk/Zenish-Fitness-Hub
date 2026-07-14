from rest_framework.generics import CreateAPIView
from .models import CustomUser, Profile
from .serializers import CustomUserSerializer, ProfileSerializer
from rest_framework.permissions import AllowAny

# Create your views here.


class UserRegistrationView(CreateAPIView):
    """Endpoint for user registration.
    Allows access to create a new user with email and password.
    """

    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

