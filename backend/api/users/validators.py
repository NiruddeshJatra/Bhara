from rest_framework.serializers import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import User
import string
import re
from datetime import datetime
from django.utils.translation import gettext as _


def validate_password_strength(password):
    validate_password(password)
    if len(password) < 8:
        raise ValidationError(_("Password must be at least 8 characters long."))
    if not any(char.isupper() for char in password):
        raise ValidationError(_("Password must contain at least one uppercase letter."))
    if not any(char.islower() for char in password):
        raise ValidationError(_("Password must contain at least one lowercase letter."))
    if not any(char.isdigit() for char in password):
        raise ValidationError(_("Password must contain at least one digit."))
    if not any(char in string.punctuation for char in password):
        raise ValidationError(
            _("Password must contain at least one special character.")
        )
    return password


def validate_phone_number(phone_number):
    pattern = r"^(\+?88)?01[3-9]\d{8}$"
    if not re.match(pattern, phone_number):
        raise ValidationError(
            _("Invalid phone number. Please enter a valid Bangladeshi phone number.")
        )
    return phone_number


def validate_national_id(national_id):
    pattern = r"^[0-9]{10}$"
    if not re.match(pattern, national_id):
        raise ValidationError(
            _("Invalid national ID. Please enter a valid Bangladeshi national ID.")
        )
    return national_id


def validate_email(email):
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        raise ValidationError(_("Invalid email address."))
    return email


def validate_username(username):
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        raise ValidationError(
            _("Username can only contain letters, numbers, and underscores.")
        )
    return username


def validate_date_of_birth(date_of_birth):
    if date_of_birth > datetime.now().date():
        raise ValidationError(_("Date of birth cannot be in the future."))
    if date_of_birth < datetime(1900, 1, 1).date():
        raise ValidationError(_("Date of birth cannot be before 1900-01-01."))
    if date_of_birth > datetime(2005, 1, 1).date():
        raise ValidationError(_("You must be at least 18 years old to register."))
    return date_of_birth


def validate_image_file(image_file):
    if image_file.type not in ["image/jpeg", "image/png", "image/jpg", "image/webp"]:
        raise ValidationError(
            _("Invalid image file. Please upload a valid image file.")
        )
    if image_file.size > 10 * 1024 * 1024:
        raise ValidationError(_("Image file cannot be larger than 10MB."))
    return image_file


def validate_signup_data(data):
    errors = {}

    # Check uniqueness
    if User.objects.filter(username=data.get("username")).exists():
        errors["username"] = _("Username is already taken.")

    if User.objects.filter(email=data.get("email")).exists():
        errors["email"] = _("Email is already registered.")

        # Validate field formats
        try:
            validate_email(data.get("email"))
        except ValidationError as e:
            errors["email"] = e.message

        try:
            validate_username(data.get("username"))
        except ValidationError as e:
            errors["username"] = e.message

        try:
            validate_password(data.get("password"))
        except ValidationError as e:
            errors["password"] = e.message

    if errors:
        raise ValidationError(errors)

    return data


def validate_profile_completion_data(data):
    errors = {}

    phone_number = data.get("phone_number")
    if phone_number:
        try:
            validate_phone_number(phone_number)
        except ValidationError as e:
            errors["phone_number"] = e.message

    date_of_birth = data.get("date_of_birth")
    if date_of_birth:
        try:
            validate_date_of_birth(date_of_birth)
        except ValidationError as e:
            errors["date_of_birth"] = e.message

    national_id = data.get("national_id")
    if national_id:
        try:
            validate_national_id(national_id)
        except ValidationError as e:
            errors["national_id"] = e.message

    national_id_front = data.get("national_id_front")
    if national_id_front:
        try:
            validate_image_file(national_id_front)
        except ValidationError as e:
            errors["national_id_front"] = e.message

    national_id_back = data.get("national_id_back")
    if national_id_back:
        try:
            validate_image_file(national_id_back)
        except ValidationError as e:
            errors["national_id_back"] = e.message

    required_fields = [
        "phone_number",
        "date_of_birth",
        "national_id",
        "national_id_front",
        "national_id_back",
    ]
    for field in required_fields:
        if not data.get(field):
            errors[field] = _("This field is required.")

    if errors:
        raise ValidationError(errors)

    return data
