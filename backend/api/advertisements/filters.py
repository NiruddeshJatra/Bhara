from django_filters import FilterSet, ChoiceFilter, CharFilter, NumberFilter, DateFilter
from django.db.models import Q
from .models import Product
from .constants import *


class ProductFilter(FilterSet):
    category = ChoiceFilter(choices=CATEGORY_CHOICES)
    product_type = ChoiceFilter(choices=PRODUCT_TYPE_CHOICES)
    location = CharFilter(lookup_expr='icontains')
    
    # Price range filtering (based on minimum pricing tier)
    min_price = NumberFilter(method="filter_min_price")
    max_price = NumberFilter(method='filter_max_price')
    
    # Rating filter
    min_rating = NumberFilter(field_name='average_rating', lookup_expr='gte')
    
    # Availability filter
    available_date = DateFilter(method='filter_available_date')
    
    class Meta:
        model = Product
        fields = ['category', 'product_type', 'location']

    def filter_min_price(self, queryset, name, value):
        """Filter products with minimum price in any pricing tier"""
        return queryset.filter(pricing_tiers__base_price__gte=value).distinct()

    def filter_max_price(self, queryset, name, value):
        """Filter products with maximum price in any pricing tier"""
        return queryset.filter(pricing_tiers__base_price__lte=value).distinct()

    def filter_available_date(self, queryset, name, value):
        """Filter products available on a specific date"""
        return queryset.exclude(
            Q(unavailable_periods__single_date=value) |
            Q(
                unavailable_periods__is_range=True,
                unavailable_periods__range_start__lte=value,
                unavailable_periods__range_end__gte=value
            )
        ).distinct()