from rest_framework import serializers
from .models import CustomUser, Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=False, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "password",
            "confirm_password",
            "telegram_id",
            "is_staff",
            "is_superuser",
            "is_active",
        ]
        read_only_fields = ["id", "is_staff", "is_superuser", "is_active"]

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError(
                {"password": "Password and Confirm Password do not match."}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password", None)
        password = validated_data.pop("password", None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "first_name",
            "last_name",
            "gender",
            "goal",
            "birth_date",
            "height_cm",
            "weight_kg",
            "current_fat_percentage",
            "activity_level",
            "preferred_environment",
            "target_workouts_per_week",
            "measurement_system",
            "timezone",
            "experience_level",
            "is_premium",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at", "is_premium"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["is_staff"] = user.is_staff
        if hasattr(user, "profile"):
            token["first_name"] = user.profile.first_name
            token["is_superuser"] = user.is_superuser
        return token
