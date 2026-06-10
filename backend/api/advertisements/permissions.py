from rest_framework.permissions import BasePermission, SAFE_METHODS


class ProductPermission(BasePermission):
    def has_permission(self, request, view):
        # List and retrieve: everyone
        if request.method in SAFE_METHODS:
            return True
        
        # Create: authenticated users
        if view.action == "create":
            return request.user and request.user.is_authenticated and request.user.profile_completed
        
        # Update and delete: handled in has_object_permission
        return True
    
    def has_object_permission(self, request, view, obj):
        # Read permissions: everyone
        if request.method in SAFE_METHODS:
            return True
        
        # Update and delete: only owner, and only if not rented
        if view.action in ["update", "partial_update", "destroy"]:
            return obj.owner == request.user and not obj.status == "rented"
        
        return False
