from rest_framework.generics import CreateAPIView
from .models import CustomUser, Profile
from .serializers import CustomUserSerializer, ProfileSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

# Create your views here.


class UserRegistrationView(CreateAPIView):
    """Endpoint for user registration.
    Allows access to create a new user with email and password.
    """

    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        """Override the create method to handle user registration."""
        serializer_data = self.get_serializer(data=request.data)
        serializer_data.is_valid(raise_exception=True)
        serializer_data.save()
        return Response(
            {
                "message": "User registered successfully. Please check your email for verification.",
            },
            status=status.HTTP_201_CREATED,
        )
