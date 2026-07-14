from django.core.mail import send_mail
from .models import CustomUser
from celery import shared_task


@shared_task
def send_welcome_email(user: CustomUser):
    """Send a welcome email to the newly registered user."""
    pass
