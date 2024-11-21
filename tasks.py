# user_service/user/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import User

# Task to check if the user is already registered
@shared_task
def check_user_registered(username, email):
    try:
        user = User.objects.get(username=username)
        return False  # User already exists
    except User.DoesNotExist:
        return True  # User does not exist

# Task to send a confirmation email to the user
@shared_task
def send_confirmation_email(user_id):
    user = User.objects.get(id=user_id)
    subject = 'Registration Confirmation'
    message = f'Hello {user.username}, your account has been successfully created!'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
