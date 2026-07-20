from rest_framework.generics import CreateAPIView, GenericAPIView
from .models import CustomUser, Profile
from .serializers import CustomUserSerializer, ProfileSerializer, VerifyEmailSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache

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


class UserVerificationEmailView(GenericAPIView):
    """Endpoint for verifying a user's email using a verification code sent to their email."""

    permission_classes = [AllowAny]
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer_data = self.get_serializer(data=request.data)
        serializer_data.is_valid()
        email = serializer_data.validated_data["email"]
        code = serializer_data.validated_data["code"]
        cache_key: str = f"email_verification_code_{email}"
        saved_code = cache.get(cache_key)

        if saved_code is None or str(saved_code) != str(code):
            return Response(
                {"error": "Invalid or expired verification code."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user: CustomUser = CustomUser.objects.get(email=email)
            if user.is_verified:
                return Response(
                    {"message": "Email is already verified."}, status=status.HTTP_200_OK
                )
            user.is_verified = True
            user.save(update_fields=["is_verified"])
            cache.delete(cache_key)

            return Response(
                {"message": "Email verified successfully! You can now log in."},
                status=status.HTTP_200_OK,
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
