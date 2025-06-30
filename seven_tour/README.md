# Seven Tour Operator Platform

This project is the backend and frontend for the Seven Tour Operator platform, designed to provide comprehensive travel and visa services.

## Project Structure

-   `/backend`: Contains the Django backend application.
    -   `users`: Django app for user management, authentication, profiles, golden coins.
    -   `tours`: Django app for tour packages, countries, destinations, reviews.
    -   `core`: Core Django project settings, URLs.
-   `/frontend`: Contains the React (TypeScript) frontend application.
    -   `src/pages`: Main page components.
    -   `src/components`: Reusable UI components.
    -   `src/services`: API service integration.
    -   `src/contexts`: React contexts (e.g., AuthContext).
-   `docker-compose.yml`: For setting up the local development environment using Docker.
-   `.github/workflows/ci-cd.yml`: Basic GitHub Actions workflow for CI/CD (builds images).

## Technology Stack

-   **Backend**: Python, Django, Django REST Framework, PostgreSQL
    -   Authentication: `dj-rest-auth`, `django-allauth` (for email/password & Google OAuth), JWT.
-   **Frontend**: TypeScript, React, React Router, Axios, `@react-oauth/google`.
-   **Containerization**: Docker, Docker Compose.
-   **CI/CD Example**: GitHub Actions.

## Getting Started (Local Development)

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

-   Docker Desktop (or Docker Engine + Docker Compose) installed.
-   A Google Cloud Platform project with OAuth 2.0 Client ID set up if you want to test Google Sign-In.

### Setup & Running

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd seven_tour
    # Or cd into the directory where docker-compose.yml is located
    ```

2.  **Environment Variables:**
    *   **Backend:** The backend uses default credentials for the database in `docker-compose.yml` for local development (`seven_tour_db`, `seven_tour_user`, `password`). `DJANGO_SECRET_KEY` also uses a placeholder. For production, these must be changed and secured.
    *   **Frontend (Google OAuth):**
        *   Create a `.env` file in the `seven_tour/frontend/` directory: `seven_tour/frontend/.env`
        *   Add your Google OAuth Client ID to this file:
            ```env
            REACT_APP_GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com
            ```
            Replace `YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com` with your actual Client ID from Google Cloud Console.

3.  **Build and Run with Docker Compose:**
    From the directory containing `docker-compose.yml` (e.g., `seven_tour/`), run:
    ```bash
    docker-compose up --build -d
    ```
    -   `--build`: Forces Docker to rebuild the images if Dockerfiles have changed.
    -   `-d`: Runs containers in detached mode.
    This command will:
    -   Pull/build images for backend, frontend, and PostgreSQL.
    -   Start the services.
    -   The backend's `entrypoint.sh` script will wait for PostgreSQL, then apply database migrations.

4.  **Accessing the Application:**
    *   **Frontend:** Open your browser and go to `http://localhost:3000`
    *   **Backend API:** Accessible at `http://localhost:8000/api/v1/`
    *   **Django Admin:** `http://localhost:8000/admin/`
        *   To create a superuser for the Django admin, once the backend container is running:
            ```bash
            docker-compose exec backend python manage.py createsuperuser
            ```
            Follow the prompts to create your admin account.

5.  **Setting up Google OAuth in Django Admin (for Google Sign-In):**
    *   Navigate to `http://localhost:8000/admin/`.
    *   Log in with your superuser credentials.
    *   Go to "Social applications" (under `DJANGO-ALLAUTH` or `SOCIALACCOUNT`).
    *   Click "Add social application".
    *   Provider: `Google`
    *   Name: `Google Auth` (or similar)
    *   Client id: Your Google OAuth Client ID (the same one used in `REACT_APP_GOOGLE_CLIENT_ID`).
    *   Secret key: Your Google OAuth Client Secret from Google Cloud Console.
    *   Sites: Choose the default site (usually `example.com` or `localhost:8000` for local dev, ensure this site's domain in Django Admin > Sites matches what `allauth` expects or configure it). Often, you'll select the available site from the list.
    *   Save the social application.

6.  **Stopping the Application:**
    ```bash
    docker-compose down
    ```

### Running Backend Tests

Once the application is running via `docker-compose up -d`:
```bash
docker-compose exec backend python manage.py test
```
To run tests for a specific app:
```bash
docker-compose exec backend python manage.py test users
docker-compose exec backend python manage.py test tours
```

## Key Features Implemented (Phase 1 Basic)

*   **User Management:** Email/password registration & login, Google Sign-In. Basic profile view.
*   **Referral System:** Unique referral codes, welcome Golden Coins.
*   **Tour Packages:** Admin can create/manage countries, destinations, tour packages.
*   **Tour Display:** Users can browse, filter, search, and view tour package details.
*   **Reviews (Stub):** Backend model and API for submitting reviews (UI for submission/display is basic or pending).
*   **PWA Ready:** Basic manifest and service worker setup.
*   **API Documentation:** API endpoints are browsable via DRF's default interface (e.g. `http://localhost:8000/api/v1/tours/packages/`). For more formal documentation, tools like Swagger/OpenAPI via `drf-spectacular` could be added.

## Further Development & Deployment

*   See `.github/workflows/ci-cd.yml` for a basic CI pipeline example.
*   See `backend/Procfile` and `frontend/Procfile` for example Heroku deployment configurations.
*   For production deployment, ensure all environment variables (secrets, API keys, database URLs, allowed hosts, CORS origins) are securely configured on your hosting platform.
*   The current `DEBUG` mode is `True` for Django; set to `False` for production.

This README provides a starting point. More detailed documentation for specific components or advanced setup can be added as the project evolves.
