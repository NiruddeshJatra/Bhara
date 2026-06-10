from rest_framework import serializers
from .models import Product, PricingTier, ProductImage, UnavailablePeriod
from .validators import *
from django.utils.translation import gettext as _
from django.db import transaction
import re
import logging

logger = logging.getLogger(__name__)


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]
        read_only_fields = ["id"]

    def validate_image(self, image):
        # Single file validation
        if image.size > 1024 * 1024 * 5:
            raise serializers.ValidationError(_("Image size must be less than 5MB."))
        if image.content_type not in ["image/jpeg", "image/jpg", "image/png", "image/gif"]:
            raise serializers.ValidationError(_("Invalid image format."))
        return image


class PricingTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingTier
        fields = ["id", "duration_unit", "base_price", "max_period"]
        read_only_fields = ["id"]

    def validate(self, data):
        return validate_pricing_tier(data)


class UnavailablePeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnavailablePeriod
        fields = ["id", "is_range", "single_date", "range_start", "range_end"]
        read_only_fields = ["id"]

    def validate(self, data):
        return validate_unavailable_period(data)


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    pricing_tiers = PricingTierSerializer(many=True)
    unavailable_periods = UnavailablePeriodSerializer(
        many=True, required=False)
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Product
        fields = [
            "id", "title", "category", "product_type", "description", "location",
            "security_deposit", "purchase_year", "purchase_price", "ownership_history",
            "status", "status_message", "status_updated_at", "views_count",
            "rental_count", "average_rating", "created_at", "updated_at",
            "images", "pricing_tiers", "unavailable_periods", "owner",
        ]
        read_only_fields = [
            "id", "status", "status_message", "status_updated_at",
            "views_count", "rental_count", "average_rating",
            "created_at", "updated_at", "owner",
        ]

    def to_internal_value(self, data):
        """
        Convert form-data with nested fields and files to internal format
        """
        # Start with a copy of the data
        internal_data = {}

        # Handle regular fields first
        for field_name in self.fields:
            if field_name in ['images', 'pricing_tiers', 'unavailable_periods']:
                continue
            if field_name in data:
                internal_data[field_name] = data[field_name]

        # Handle images
        images_data = self._parse_images(data)
        logger.info("Parsed images: %s", images_data)
        if images_data:
            internal_data['images'] = images_data

        # Handle pricing tiers
        pricing_tiers = self._parse_pricing_tiers(data)
        logger.info("Parsed pricing_tiers: %s", pricing_tiers)
        if pricing_tiers:
            internal_data['pricing_tiers'] = pricing_tiers

        # Handle unavailable periods
        unavailable_periods = self._parse_unavailable_periods(data)
        logger.info("Parsed unavailable_periods: %s", unavailable_periods)
        if unavailable_periods:
            internal_data['unavailable_periods'] = unavailable_periods

        return super().to_internal_value(internal_data)

    def _parse_images(self, data):
        """Parse image files from form data"""
        images_data = []

        # Look for image files with pattern: images[n][image] or images[n]
        for key, value in data.items():
            logger.debug("Key: %s, Value: %s", key, type(value))
            if key.startswith('images[') and ('[image]' in key or key.endswith(']')):
                if hasattr(value, 'read') and hasattr(value, 'size'):  # It's a file
                    images_data.append({'image': value})

        return images_data

    def _parse_pricing_tiers(self, data):
        """Parse pricing tiers from form data"""
        pricing_tiers = {}
        pattern = re.compile(r'pricing_tiers\[(\d+)\]\[(\w+)\]')
        for key, value in data.items():
            match = pattern.match(key)
            if match:
                index, field = match.groups()
                index = int(index)
                if index not in pricing_tiers:
                    pricing_tiers[index] = {}
                if field in ['base_price', 'max_period']:
                    value = int(value) if value else None
                pricing_tiers[index][field] = value
        return [pricing_tiers[i] for i in sorted(pricing_tiers.keys())]

    def _parse_unavailable_periods(self, data):
        """Parse unavailable periods from form data"""
        periods = {}
        pattern = re.compile(r'unavailable_periods\[(\d+)\]\[(\w+)\]')
        for key, value in data.items():
            match = pattern.match(key)
            if match:
                index, field = match.groups()
                index = int(index)
                if index not in periods:
                    periods[index] = {}
                # Convert boolean field
                if field == 'is_range':
                    value = value.lower() in ('true', '1', 'yes', 'on')
                periods[index][field] = value
        return [periods[i] for i in sorted(periods.keys())]

    def validate(self, data):
        validate_product_details(data)

        # Validate images count (list-level)
        images = data.get("images", [])
        if len(images) < 1:
            raise serializers.ValidationError({"images": _( "At least one image is required.")})
        if len(images) > 10:
            raise serializers.ValidationError({"images": _( "Maximum of 10 images allowed.")})

        # Validate pricing tiers
        if not data.get("pricing_tiers"):
            raise serializers.ValidationError(
                _( "At least one pricing tier is required.")
            )

        # Check for duplicate duration units
        duration_units = [pt["duration_unit"] for pt in data["pricing_tiers"]]
        if len(duration_units) != len(set(duration_units)):
            raise serializers.ValidationError(
                _( "Duplicate duration units are not allowed.")
            )

        return data

    @transaction.atomic
    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        pricing_tiers_data = validated_data.pop("pricing_tiers")
        unavailable_periods_data = validated_data.pop(
            "unavailable_periods", [])

        product = Product.objects.create(**validated_data)

        # Create images
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)

        # Create pricing tiers
        for pricing_tier_data in pricing_tiers_data:
            PricingTier.objects.create(product=product, **pricing_tier_data)

        # Create unavailable periods
        for unavailable_period_data in unavailable_periods_data:
            UnavailablePeriod.objects.create(
                product=product, **unavailable_period_data)

        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", None)
        pricing_tiers_data = validated_data.pop("pricing_tiers", None)
        unavailable_periods_data = validated_data.pop(
            "unavailable_periods", None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update images if provided
        if images_data is not None:
            instance.images.all().delete()
            for image_data in images_data:
                ProductImage.objects.create(product=instance, **image_data)

        # Update pricing tiers if provided
        if pricing_tiers_data is not None:
            instance.pricing_tiers.all().delete()
            for pricing_tier_data in pricing_tiers_data:
                PricingTier.objects.create(
                    product=instance, **pricing_tier_data)

        # Update unavailable periods if provided
        if unavailable_periods_data is not None:
            instance.unavailable_periods.all().delete()
            for period_data in unavailable_periods_data:
                UnavailablePeriod.objects.create(
                    product=instance, **period_data)

        return instance
