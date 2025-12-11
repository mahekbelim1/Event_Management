A Django REST Framework project that provides APIs for event creation, RSVPs, and reviews with JWT authentication and custom permissions.

1. Overview
-The Event Management API enables users to:
-Create, update, and delete events
-RSVP to events
-Submit reviews
-Access public events or private events if invited
-Authenticate using JWT tokens
-Use filtering, searching, and pagination features
-Run automated unit tests
This project demonstrates practical use of Django REST Framework, authentication, permissions, model relationships, and API design.

2. Features
-JWT authentication (SimpleJWT)
-Event CRUD operations
-RSVP system
-Review system with duplicate-review protection
-Custom permissions
-Only organizer can edit/delete event
-Private events visible only to invited users
-Search, filtering, and ordering
-Pagination
-Automated unit tests
-Django admin support

3. Project Structure
event_api/
    event_api/
        settings.py
        urls.py
        wsgi.py
    events/
        models.py
        serializers.py
        permissions.py
        views.py
        urls.py
        tests/
            test_api.py
    manage.py
requirements.txt
README.md

4. How to Run the Project
4.1 Clone the Repository
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

4.2 Create and Activate Virtual Environment
Windows (PowerShell):
python -m venv venv
venv\Scripts\activate


Mac / Linux:
python3 -m venv venv
source venv/bin/activate

4.3 Install Dependencies
pip install -r requirements.txt

4.4 Apply Database Migrations
python manage.py makemigrations
python manage.py migrate

4.5 Create Superuser
python manage.py createsuperuser

4.6 Run the Development Server
python manage.py runserver


API will be available at:
http://127.0.0.1:8000/api/events/
http://127.0.0.1:8000/api/token/
http://127.0.0.1:8000/admin/

5. Authentication (JWT)
5.1 Obtain Token
POST /api/token/
Body:
{
  "username": "your_username",
  "password": "your_password"
}

5.2 Use Access Token
Add header:
Authorization: Bearer <access_token>

6. API Endpoints
Event Endpoints
GET /api/events/ → List public events
POST /api/events/ → Create event (auth required)
GET /api/events/<id>/ → Retrieve event
PUT /api/events/<id>/ → Update event (organizer only)
DELETE /api/events/<id>/ → Delete event (organizer only)
RSVP Endpoints
POST /api/events/<id>/rsvp/
PATCH /api/events/<id>/rsvp/<user_id>/
Review Endpoints
POST /api/events/<id>/reviews/
GET /api/events/<id>/reviews/

7. Filtering, Searching, Pagination
Filtering

Examples:
/api/events/?location=Ahmedabad
/api/events/?organizer=1

Searching
/api/events/?search=Music

Ordering
/api/events/?ordering=start_time

Pagination
Enabled by default (page size = 10):
/api/events/?page=2

8. Running Unit Tests
python manage.py test -v 2

-Includes tests for:
-Event creation
-RSVPs
-Reviews
-Permissions
-Anonymous and authenticated access

9. Requirements
Generated automatically in requirements.txt using:
pip freeze > requirements.txt

Key packages:
-Django
-Django REST Framework
-SimpleJWT
-django-filter

10. Notes for Evaluators
-No database setup required (SQLite used)
-All core features implemented
-Unit tests included
-Project follows REST API best practices
-Fully documented and ready to extend

11. License
This project is created for internship assignment purposes.




