from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOrganizerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.organizer == request.user

class IsInvitedOrPublic(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.is_public:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if obj.organizer == request.user:
            return True
        return obj.invited.filter(id=request.user.id).exists()
