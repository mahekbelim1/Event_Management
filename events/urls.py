# events/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RSVPUpdateView

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='events')

urlpatterns = [
    path('', include(router.urls)),
    # RSVP update (organizer or user can update a specific user's RSVP)
    path('events/<int:event_pk>/rsvp/<int:user_pk>/', RSVPUpdateView.as_view({'patch': 'partial_update'}), name='rsvp-update'),
]

