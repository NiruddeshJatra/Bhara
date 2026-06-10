from rest_framework import viewsets, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.core.cache import cache
import logging

from .models import Product, ProductImage
from .serializers import ProductSerializer
from .filters import ProductFilter
from .permissions import ProductPermission

logger = logging.getLogger(__name__)


class ProductPagination(PageNumberPagination):
    """Custom pagination for products with 40 items per page"""
    page_size = 40
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [ProductPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'views_count', 'rental_count', 'average_rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Base queryset with performance optimizations
        queryset = Product.objects.select_related('owner').prefetch_related(
            "images",
            "pricing_tiers"
        )
        
        # Different visibility rules based on action
        if self.action in ['list', 'retrieve']:
            if self.request.user.is_authenticated and self.request.user == queryset_owner:
                queryset = queryset.filter(status__in=['active', 'draft', 'maintenance', 'suspended'])
            else:
                queryset = queryset.filter(status='active')

            # Apply smart ordering for public listings
            if self.action == 'list':
                queryset = self._apply_smart_ordering(queryset)

        elif self.action in ["my_products"]:
            # Owner's view: show all their products regardless of status
            queryset = queryset.filter(owner=self.request.user)

        else:
            # Admin/owner actions: show all products
            pass
        
        return queryset

    def _apply_smart_ordering(self, queryset):
        """
        Apply intelligent ranking for product listings.
        Prioritizes: recently active > highly rated > most viewed > newest
        """
        ordering = self.request.query_params.get('ordering', '')
        
        if not ordering:
            # Default smart ordering: mix of engagement and recency
            from django.db.models import F, ExpressionWrapper, FloatField
            from django.utils import timezone
            from django.db.models.functions import Extract

            days_since_creation = ExpressionWrapper(
                Extract(timezone.now() - F('created_at'), 'epoch') / 86400.0,
                output_field=FloatField()
            )
            popularity_score = ExpressionWrapper(
                (F('views_count') * 0.3 + F('rental_count') * 2.0 + F('average_rating') * 1.5) / (days_since_creation + 1),
                output_field=FloatField()
            )
            return queryset.annotate(popularity_score=popularity_score).order_by('-popularity_score', '-created_at')
        
        return queryset.order_by(ordering)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single product and increment view count.
        """
        instance = self.get_object()
        
        # Increment view count (only for non-owners)
        if not (request.user.is_authenticated and request.user == instance.owner):
            instance.increment_views()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Create a new product with owner set to current user.
        """
        # Owner is already set in serializer via HiddenField
        product = serializer.save()
        
        # Clear relevant caches
        self._clear_product_caches()
        
    def perform_update(self, serializer):
        """
        Update product with validation for rental status.
        """
        instance = serializer.instance
        
        # Prevent editing while product is rented
        if instance.status == 'rented':
            raise serializers.ValidationError(
                "Cannot edit product details while it's currently rented."
            )
        
        serializer.save()
        self._clear_product_caches()
        
        logger.info(f"Product updated: {instance.id} by user {self.request.user.id}")

    def perform_destroy(self, instance):
        """
        Delete product with validation.
        """
        if instance.status == 'rented':
            raise serializers.ValidationError(
                "Cannot delete product while it's currently rented."
            )
        
        product_id = instance.id
        instance.delete()
        self._clear_product_caches()
        
        logger.info(f"Product deleted: {product_id} by user {self.request.user.id}")

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_products(self, request):
        """
        Get current user's products with all statuses.
        """
        queryset = self.filter_queryset(
            Product.objects.filter(owner=request.user)
            .select_related('owner')
            .prefetch_related('images', 'pricing_tiers', 'unavailable_periods')
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
          
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
      
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated, ProductPermission])
    def update_status(self, request, pk=None):
        """
        Update product status (for admin/owner use).
        """
        instance = serializer.instance
        new_status = request.data.get('status')
        message = request.data.get('message', '')
        instance.update_status(new_status, message)
        self._clear_product_caches()
        
        return Response({
            'status': instance.status,
            'message': instance.status_message,
            'updated_at': instance.status_updated_at
        })
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured products (highly rated and frequently rented).
        """
        cache_key = 'featured_products'
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            queryset = self.get_queryset().filter(
                average_rating__gte=4.0,
                rental_count__gte=5
            ).order_by('-average_rating', '-rental_count')[:12]
            
            serializer = self.get_serializer(queryset, many=True)
            cached_data = serializer.data
            cache.set(cache_key, cached_data, 60 * 30)  # Cache for 30 minutes
        
        return Response(cached_data)

    def _clear_product_caches(self):
        # Use the raw Redis connection for Django's built-in RedisCache
        try:
            # _cache is the raw redis-py client
            client = cache._cache
            keys = client.keys('product_list_*')
            if keys:
                client.delete(*keys)
        except Exception as e:
            # Optionally log the error
            print("Error clearing product caches:", e)


class ProductImageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Separate viewset for product images with different sizes.
    """
    queryset = ProductImage.objects.all()
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['get'])
    def sizes(self, request, pk=None):
        """
        Get different sizes of the same image.
        This would integrate with django-imagekit for on-the-fly resizing.
        """
        image = self.get_object()
        
        # This would use django-imagekit processors
        # For now, returning the concept structure
        sizes = {
            'thumbnail': f"{image.image.url}?size=thumb",    # 150x150
            'card': f"{image.image.url}?size=card",          # 300x200
            'modal': f"{image.image.url}?size=modal",        # 600x400
            'full': image.image.url                          # Original
        }
        
        return Response(sizes)