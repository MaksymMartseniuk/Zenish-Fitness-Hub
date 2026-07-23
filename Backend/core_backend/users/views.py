from rest_framework.generics import CreateAPIView, GenericAPIView
from .models import CustomUser, Profile
from .serializers import (
    CustomUserSerializer,
    ProfileSerializer,
    VerifyEmailSerializer,
    ResendVerificationEmailSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from .services import send_verification_email, send_password_reset_email
import secrets

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
        verification_code = serializer_data.validated_data["verification_code"]
        cache_key: str = f"email_verification_code_{email}"
        saved_code = cache.get(cache_key)

        if saved_code is None or str(saved_code) != str(verification_code):
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


class ResendVerificationEmailView(GenericAPIView):
    """Endpoint for resending verification code for email"""

    permission_classes = [AllowAny]
    serializer_class = ResendVerificationEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        try:
            user: CustomUser = CustomUser.objects.get(email=email)
            if user.is_verified:
                return Response(
                    {"message": "Email is already verified. You can log in."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            send_verification_email.delay(user_id=user.id)
            return Response(
                {
                    "message": "Verification code resent successfully. Please check your email."
                },
                status=status.HTTP_200_OK,
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User with this email not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class PasswordResetRequestView(GenericAPIView):
    """Endpoint to request a password reset link."""

    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            reset_token = secrets.token_urlsafe(32)
            cache_key = f"reset_token:{reset_token}"
            cache.set(cache_key, email, timeout=900)
            send_password_reset_email(email, reset_token)
        except CustomUser.DoesNotExist:
            pass

        return Response(
            {
                "message": "If an account with this email exists, a password reset link has been sent."
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(GenericAPIView):
    """Endpoint to set a new password using a token."""

    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["password"]
        cache_key = f"reset_token:{token}"
        email = cache.get(cache_key)
        if not email:
            return Response(
                {"error": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user: CustomUser = CustomUser.objects.get(email=email)
            user.set_password(new_password)
            user.save(update_fields=["password"])
            cache.delete(cache_key)
            return Response(
                {
                    "message": "Password has been reset successfully. You can now log in."
                },
                status=status.HTTP_200_OK,
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User associated with this token no longer exists."},
                status=status.HTTP_404_NOT_FOUND,
            )
