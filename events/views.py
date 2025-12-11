from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from .models import Event, RSVP, Review
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizerOrReadOnly, IsInvitedOrPublic


class EventViewSet(viewsets.ModelViewSet):
    """
    Event endpoints:
      - POST /events/        create (authenticated)
      - GET  /events/        list (public + invited + own)
      - GET  /events/{id}/   retrieve (respect private/invite)
      - PUT/PATCH/DELETE     update / delete (organizer only)
      - POST /events/{id}/rsvp/       create/update your RSVP
      - GET/POST /events/{id}/reviews/ list/add reviews
    """
    queryset = Event.objects.select_related('organizer').prefetch_related('invited').all()
    serializer_class = EventSerializer

    # enable filtering/search/ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_public', 'location', 'organizer']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_time', 'created_at']
    ordering = ['start_time']

    def get_queryset(self):
        user = self.request.user
        qs = Event.objects.select_related('organizer').prefetch_related('invited').all()
        # show public events to everyone; show private events only to invited users/organizer
        if user.is_authenticated:
            return qs.filter(Q(is_public=True) | Q(invited=user) | Q(organizer=user)).distinct()
        return qs.filter(is_public=True)

    def get_permissions(self):
        # create requires authentication
        if self.action in ['create']:
            return [IsAuthenticated()]
        # edits / delete require organizer
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOrganizerOrReadOnly()]
        # retrieving a single event should respect private/invited permission
        if self.action in ['retrieve']:
            return [IsInvitedOrPublic()]
        # rsvp requires auth (defined on the action)
        # reviews: GET is open, POST will check auth inside view
        return [AllowAny()]

    def perform_create(self, serializer):
        # NOTE: serializer is responsible for assigning organizer from request context.
        # We intentionally do NOT pass organizer here to avoid "multiple values" errors.
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rsvp(self, request, pk=None):
        """
        POST /events/{id}/rsvp/
        Body: {"status": "Going" | "Maybe" | "Not Going"}
        Creates or updates the authenticated user's RSVP for the event.
        """
        event = self.get_object()
        status_val = request.data.get('status')
        if status_val not in dict(RSVP.STATUS_CHOICES):
            return Response({'detail': 'invalid status (choose Going / Maybe / Not Going)'},
                            status=status.HTTP_400_BAD_REQUEST)

        rsvp, created = RSVP.objects.update_or_create(
            event=event,
            user=request.user,
            defaults={'status': status_val}
        )
        return Response(RSVPSerializer(rsvp, context={'request': request}).data)

    @action(detail=True, methods=['get', 'post'], url_path='reviews', permission_classes=[AllowAny])
    def reviews(self, request, pk=None):
        """
        GET  /events/{id}/reviews/  -> list reviews (paginated)
        POST /events/{id}/reviews/  -> add a review (authenticated users only, one per user)
        """
        event = self.get_object()

        if request.method == 'GET':
            qs = event.reviews.all().order_by('-created_at')
            page = self.paginate_queryset(qs)
            serializer = ReviewSerializer(page or qs, many=True, context={'request': request})
            if page is not None:
                return self.get_paginated_response(serializer.data)
            return Response(serializer.data)

        # POST: create review
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        if Review.objects.filter(event=event, user=request.user).exists():
            return Response({'detail': 'You already reviewed this event'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'event': event.id,
            'rating': request.data.get('rating'),
            'comment': request.data.get('comment', '')
        }
        serializer = ReviewSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, event=event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RSVPUpdateView(viewsets.ViewSet):
    """
    PATCH /events/{event_pk}/rsvp/{user_pk}/ - update RSVP for a specific user (organizer or that user)
    """
    def partial_update(self, request, event_pk=None, user_pk=None):
        event = get_object_or_404(Event, pk=event_pk)
        rsvp = get_object_or_404(RSVP, event=event, user__pk=user_pk)

        # only the RSVP owner or the event organizer may update
        if request.user != rsvp.user and request.user != event.organizer:
            return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)

        serializer = RSVPSerializer(rsvp, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
