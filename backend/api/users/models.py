from django.db import models
from authemail.models import EmailUserManager, EmailAbstractUser
from uuid import uuid4
from .validators import *


class User(EmailAbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(unique=True, validators=[validate_email])
    username = models.CharField(
        max_length=30, unique=True, validators=[validate_username]
    )
    password = models.CharField(max_length=128, validators=[validate_password])
    is_trusted = models.BooleanField(default=False)
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_phone_number],
    )
    date_of_birth = models.DateField(
        null=True, blank=True, validators=[validate_date_of_birth]
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        null=True,
        blank=True,
        validators=[validate_image_file],
    )
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    email_verification_token = models.CharField(max_length=255, null=True, blank=True)
    national_id = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_national_id],
    )
    national_id_front = models.ImageField(
        upload_to="national_id_front_images/",
        null=True,
        blank=True,
        validators=[validate_image_file],
    )
    national_id_back = models.ImageField(
        upload_to="national_id_back_images/",
        null=True,
        blank=True,
        validators=[validate_image_file],
    )
    marketing_consent = models.BooleanField(default=False)
    profile_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True
    )

    objects = EmailUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.username
