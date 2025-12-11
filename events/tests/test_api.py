# events/tests/test_api.py
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from events.models import Event, RSVP, Review
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class EventAPITestCase(APITestCase):
    def setUp(self):
        # create users
        self.user1 = User.objects.create_user(username="user1", password="pass12345", email="u1@example.com")
        self.user2 = User.objects.create_user(username="user2", password="pass12345", email="u2@example.com")

        # client for user1
        self.client1 = APIClient()
        self.client1.force_authenticate(user=self.user1)

        # client for anonymous requests
        self.anon = APIClient()

        # sample event times
        self.start = timezone.now() + timedelta(days=1)
        self.end = self.start + timedelta(hours=3)

    def test_create_event_sets_organizer_and_invites(self):
        url = reverse("events-list")  # DRF router registered basename 'events'
        payload = {
            "title": "Test Event",
            "description": "testing",
            "location": "Test City",
            "start_time": self.start.isoformat(),
            "end_time": self.end.isoformat(),
            "is_public": False,
            "invited": [self.user2.id]
        }
        resp = self.client1.post(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.json()
        self.assertEqual(data["title"], "Test Event")
        # organizer must be user1
        self.assertEqual(data["organizer"]["username"], "user1")
        # check DB invited
        event = Event.objects.get(pk=data["id"])
        self.assertIn(self.user2, event.invited.all())

    def test_rsvp_create_and_update(self):
        # create event by user1
        event = Event.objects.create(
            title="E",
            description="d",
            organizer=self.user1,
            location="loc",
            start_time=self.start,
            end_time=self.end,
            is_public=True
        )
        url = reverse("events-rsvp", args=[event.id])  # action route for rsvp
        resp = self.client1.post(url, {"status": "Going"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # verify RSVP exists
        self.assertTrue(RSVP.objects.filter(event=event, user=self.user1, status="Going").exists())

        # update via patch using RSVP update endpoint
        patch_url = reverse("rsvp-update", kwargs={"event_pk": event.id, "user_pk": self.user1.id})
        resp2 = self.client1.patch(patch_url, {"status": "Maybe"}, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        obj = RSVP.objects.get(event=event, user=self.user1)
        self.assertEqual(obj.status, "Maybe")

    def test_review_post_and_prevent_duplicate(self):
        event = Event.objects.create(
            title="E2",
            description="d",
            organizer=self.user1,
            location="loc",
            start_time=self.start,
            end_time=self.end,
            is_public=True
        )
        review_url = reverse("events-reviews", args=[event.id])
        # post review
        resp = self.client1.post(review_url, {"rating": 5, "comment": "nice"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # posting again should fail
        resp2 = self.client1.post(review_url, {"rating": 4, "comment": "again"}, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You already reviewed", resp2.json().get("detail", "") or "")

    def test_list_public_events_anonymous(self):
        Event.objects.create(
            title="Public",
            description="d",
            organizer=self.user1,
            location="loc",
            start_time=self.start,
            end_time=self.end,
            is_public=True
        )
        Event.objects.create(
            title="Private",
            description="d",
            organizer=self.user1,
            location="loc",
            start_time=self.start,
            end_time=self.end,
            is_public=False
        )
        url = reverse("events-list")
        resp = self.anon.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()

        # Normalize results into a list of event dicts
        if isinstance(data, dict) and "results" in data:
            results_list = data["results"]
        elif isinstance(data, list):
            results_list = data
        else:
            # fallback: try to handle various shapes
            results_list = data.get("results", [])

        titles = [e.get("title") for e in results_list if isinstance(e, dict)]
        # ensure private event NOT visible to anonymous
        self.assertIn("Public", " ".join(titles))
        self.assertNotIn("Private", " ".join(titles))
