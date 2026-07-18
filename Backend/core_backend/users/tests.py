from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from faker import Faker
# Create your tests here.

User = get_user_model()
fake = Faker()


class UserRegistrationTestsAPI(APITestCase):
    def setUp(self):
        self.register_url = reverse("user-register")

    @patch("users.services.send_verification_email.delay")
    def test_user_registration_success(self, mock_send_email):
        """Test successful user registration."""
        password = fake.password(
            length=12, special_chars=True, digits=True, upper_case=True, lower_case=True
        )
        email = fake.email()
        data = {
            "email": email,
            "password": password,
            "confirm_password": password,
        }
        response = self.client.post(self.register_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data["message"],
            "User registered successfully. Please check your email for verification.",
        )

        user = User.objects.get(email=email)
        self.assertFalse(user.is_verified)

        mock_send_email.assert_called_once_with(user.id)

    @patch("users.services.send_verification_email.delay")
    def test_user_registration_password_mismatch(self, mock_send_email):
        """Test user registration with password mismatch."""
        data = {
            "email": fake.email(),
            "password": fake.password(length=10),
            "confirm_password": fake.password(length=10),
        }
        response = self.client.post(self.register_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(
            response.data["password"][0], "Password and Confirm Password do not match."
        )
        self.assertEqual(User.objects.count(), 0)
        
        mock_send_email.assert_not_called()
