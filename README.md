📌 Event Management System – Django REST API

A fully functional Event Management API built using Django and Django REST Framework (DRF).
Users can create events, RSVP to events, leave reviews, and view public or invited-only events.
Includes JWT authentication, custom permissions, pagination, filtering, and unit tests.

🚀 Features
✅ User Profiles

Extends Django's built-in User model.

Includes fields: full_name, bio, location, profile_picture.

✅ Event Management

Create, update, delete events (organizer only).

Public and private events.

Invite users to private events.

Auto-store organizer during event creation.

✅ RSVP System

Users can mark: Going, Maybe, Not Going.

Users can update RSVP status anytime.

✅ Reviews

Users can post reviews.

Duplicate reviews from the same user are prevented.

✅ Authentication

JWT-based login using:

/api/token/
/api/token/refresh/

✅ Permissions

Only organizers may edit or delete events.

Private events visible only to invited users.

Public events open to all.

✅ Pagination, Filtering, Search

Pagination enabled on all list endpoints.

Filter events by:

title

location

organizer

Search events by title or description.

✅ Unit Tests Included

Covers:

Event creation

RSVP creation & update

Review posting and prevention of duplicates

Public events listing

📁 Project Structure
event_management/
│── event_api/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│── events/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   ├── tests/
│       ├── test_api.py
│── manage.py

⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone <your-repo-url>
cd event_management/event_api

2️⃣ Create Virtual Environment
python -m venv venv

3️⃣ Activate Environment

Windows:

venv\Scripts\activate

4️⃣ Install Dependencies
pip install -r requirements.txt

5️⃣ Apply Migrations
python manage.py makemigrations
python manage.py migrate

6️⃣ Create Superuser
python manage.py createsuperuser

7️⃣ Run Development Server
python manage.py runserver

🔑 Authentication
Obtain JWT Token
POST /api/token/
{
  "username": "your_username",
  "password": "your_password"
}


The response will contain:

{
  "refresh": "xxxxx",
  "access": "xxxxx"
}


Use access token in headers:
Authorization: Bearer <access_token>

🔗 API Endpoints

🎫 Events
Method	Endpoint	Description
POST	/api/events/	Create event
GET	/api/events/	List all public events
GET	/api/events/{id}/	Event details
PUT	/api/events/{id}/	Update event (organizer only)
DELETE	/api/events/{id}/	Delete event (organizer only)

📌 RSVP
Method	Endpoint
POST	/api/events/{id}/rsvp/
PATCH	/api/events/{id}/rsvp/{user_id}/

⭐ Reviews
Method	Endpoint
POST	/api/events/{id}/reviews/
GET	/api/events/{id}/reviews/

🧪 Running Unit Tests
python manage.py test events -v 2

📝 Technologies Used

Django 6+
Django REST Framework
SimpleJWT
SQLite (default)
Python 3.13

🎯 Bonus Features Implemented

✔ JWT authentication
✔ Custom permissions
✔ Pagination
✔ Search and filtering
✔ Unit tests


📚 Future Enhancements

Email notifications on event creation
Asynchronous tasks via Celery
Full Docker container setup
Frontend dashboard (React or Vue)


📄 License

This project is created for internship assignment purposes.



