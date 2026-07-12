from rest_framework import serializers
from .models import CustomUser, Profile


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "password",
            "telegram_id",
            "is_staff",
            "is_active",
        ]
        read_only_fields = ["id", "is_staff", "is_active"]

    def create(self, validated_data):
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
