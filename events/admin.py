from django.contrib import admin
from .models import UserProfile, Event, RSVP, Review

admin.site.register(UserProfile)
admin.site.register(Event)
admin.site.register(RSVP)
admin.site.register(Review)
