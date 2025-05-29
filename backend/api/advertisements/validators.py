from rest_framework.serializers import ValidationError
from django.utils.translation import gettext as _
from django.utils import timezone


def validate_product_images(images):
    """
    Validates product images.
    - Requires at least one image
    - Maximum 10 images
    - Each image must be < 5MB
    - Only allows jpeg, png, gif formats
    """
    if len(images) < 1:
        raise ValidationError(_("At least one image is required."))
    if len(images) > 10:
        raise ValidationError(_("Maximum of 10 images allowed."))
    for image in images:
        if image.size > 1024 * 1024 * 5:
            raise ValidationError(_("Image size must be less than 5MB."))
        if image.content_type not in ["image/jpeg", "image/png", "image/gif"]:
            raise ValidationError(_("Invalid image format."))
    return images


def validate_pricing_tier(data):
    """
    Validates a single pricing tier.
    - Requires valid duration unit (day/week/month)
    - Requires positive base price
    - Optional max_period (if provided, must be positive)
    """
    valid_units = ["day", "week", "month"]
    if data.get("duration_unit") not in valid_units:
        raise ValidationError(
            _("Duration unit must be one of: %(units)s")
            % {"units": ", ".join(valid_units)}
        )

    if not data.get("base_price") or data["base_price"] <= 0:
        raise ValidationError(_("Base price must be greater than 0."))

    # max_period is optional, but if provided must be positive
    if "max_period" in data and data["max_period"] <= 0:
        raise ValidationError(_("Maximum period must be greater than 0."))

    return data


def validate_unavailable_period(data):
    """
    Validates a single unavailable period.
    - For ranges: requires start and end dates, start must be before end
    - For single dates: requires single_date
    - Cannot mix range and single date
    - Dates cannot be in the past
    """
    today = timezone.now().date()

    if data.get("is_range"):
        if not data.get("range_start") or not data.get("range_end"):
            raise ValidationError(
                _("Range start and end dates are required for date ranges.")
            )
        if data.get("single_date"):
            raise ValidationError(
                _("Single date cannot be provided if is_range is true.")
            )
        if data["range_start"] > data["range_end"]:
            raise ValidationError(_("Start date must be before end date."))
        if data["range_start"] < today:
            raise ValidationError(_("Range start date cannot be in the past."))
    else:
        if not data.get("single_date"):
            raise ValidationError(_("Single date is required if is_range is false."))
        if data.get("range_start") or data.get("range_end"):
            raise ValidationError(
                _("Range dates cannot be provided if is_range is false.")
            )
        if data["single_date"] < today:
            raise ValidationError(_("Single date cannot be in the past."))

    return data


def validate_product_details(data):
    """
    Validates product details.
    - Purchase year cannot be in the future
    """
    if data.get("purchase_year") and data["purchase_year"] > timezone.now().date():
        raise ValidationError(_("Purchase year cannot be in the future."))
    return data
