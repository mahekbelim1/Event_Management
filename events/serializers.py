from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Event, RSVP, Review

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = UserProfile
        fields = ['id','full_name','bio','location','profile_picture','user']

class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    invited = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)

    class Meta:
        model = Event
        fields = ['id','title','description','organizer','location','start_time','end_time','is_public','invited','created_at','updated_at']
        read_only_fields = ['id','organizer','created_at','updated_at']

    def create(self, validated_data):
        invited = validated_data.pop('invited', [])
        event = Event.objects.create(organizer=self.context['request'].user, **validated_data)
        if invited:
            event.invited.set(invited)
        return event

    def validate(self, data):
        start = data.get('start_time', getattr(self.instance, 'start_time', None))
        end = data.get('end_time', getattr(self.instance, 'end_time', None))
        if start and end and start >= end:
            raise serializers.ValidationError('start_time must be before end_time')
        return data

class RSVPSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = RSVP
        fields = ['id','event','user','status','updated_at']
        read_only_fields = ['id','user','updated_at','event']

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Review
        fields = ['id','event','user','rating','comment','created_at']
        read_only_fields = ['id','user','created_at','event']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('rating must be 1-5')
        return value
