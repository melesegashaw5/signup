# Agent Instructions for Seven Tour Operator Project

This document provides guidance for AI agents working on the Seven Tour Operator platform codebase.

## Project Overview

-   **Backend:** Django (Python) with Django REST Framework.
-   **Frontend:** React (TypeScript) with Create React App (manually structured).
-   **Database:** PostgreSQL.
-   **Containerization:** Docker and Docker Compose for local development.
-   **Authentication:** `dj-rest-auth` and `django-allauth` for email/password and Google OAuth (JWT-based).

Refer to the main `README.md` for detailed setup, stack, and local running instructions.

## Current Status & Key Points (as of initial Phase 1 completion)

1.  **Local Development Environment:**
    *   The primary way to run and interact with the application locally is via `docker-compose up --build`.
    *   The backend service is named `backend`, frontend is `frontend`, database is `db`.
    *   To run Django `manage.py` commands:
        ```bash
        docker-compose exec backend python manage.py <your_command>
        ```
        Example: `docker-compose exec backend python manage.py createsuperuser`
    *   To run backend tests:
        ```bash
        docker-compose exec backend python manage.py test
        # Or for specific apps:
        docker-compose exec backend python manage.py test users
        docker-compose exec backend python manage.py test tours
        ```
    *   The backend `entrypoint.sh` script automatically applies migrations on startup.

2.  **Database Migrations:**
    *   When new models are added or existing ones changed in Django apps:
        1.  Run `docker-compose exec backend python manage.py makemigrations <app_name>`
        2.  The new migration files will be created in the respective app's `migrations` directory.
        3.  These migrations will be applied automatically the next time `docker-compose up` starts the backend service, or can be applied manually with `docker-compose exec backend python manage.py migrate`.

3.  **Authentication System:**
    *   Backend uses `dj-rest-auth` with JWTs and `django-allauth` for Google OAuth.
    *   **Google OAuth Setup (Manual User Steps Required):**
        *   Frontend `REACT_APP_GOOGLE_CLIENT_ID` (in `frontend/.env`) needs a valid Google Client ID.
        *   Backend Django Admin (`/admin/socialaccount/socialapp/`) needs a "Social Application" configured for Google with Client ID and Secret.
        *   Without these, Google Sign-In will not function. The code is in place to use them once configured.
    *   Custom serializers (`UserDetailsSerializer`, `CustomRegisterSerializer`) and an `AccountAdapter` are in `users/serializers.py` and `users/adapter.py`.

4.  **PWA Features:**
    *   Basic PWA setup (manifest, service worker) is in place in the frontend.
    *   For full PWA functionality (installability, offline caching as configured), the React frontend needs to be built in **production mode** (`npm run build` or `yarn build` within the frontend container or CI/CD pipeline). The development server (`npm start`) does not typically enable all PWA features.
    *   The service worker (`service-worker.ts`) uses Workbox and will be compiled to `service-worker.js` during the React build process.

5.  **Frontend Development:**
    *   The frontend is structured with `pages`, `components`, `services`, and `contexts`.
    *   API calls are centralized in `services/apiService.ts`.
    *   Global authentication state is managed by `contexts/AuthContext.tsx`.
    *   No automated frontend tests (Jest/React Testing Library) have been implemented in this phase.

6.  **Styling:**
    *   Styling is currently very basic (inline styles or minimal CSS in `App.css` / `index.css`). A dedicated styling strategy (e.g., CSS Modules, Styled Components, Tailwind CSS) would be a future enhancement.

7.  **Environment Variables:**
    *   **Backend:** Uses Django's settings for configuration. Sensitive keys like `DJANGO_SECRET_KEY` and production database credentials should be managed via environment variables in deployment (not hardcoded or committed). `docker-compose.yml` sets some for local dev.
    *   **Frontend:** Uses `REACT_APP_` prefixed environment variables (e.g., `REACT_APP_API_BASE_URL`, `REACT_APP_GOOGLE_CLIENT_ID`). These are typically set in a `.env` file for local development and injected at build time or runtime in deployed environments.

8.  **Deployment:**
    *   Example CI/CD workflow in `.github/workflows/ci-cd.yml`.
    *   Example `Procfile`s for Heroku-style deployments are provided for backend and frontend.
    *   Actual deployment is highly platform-dependent and requires manual setup of services, environment variables, and secrets.

## Agent Workflow Suggestions

*   **Adding new Django features (models, views, etc.):**
    1.  Modify/create models in the relevant app.
    2.  Run `makemigrations`.
    3.  Update/create Django admin configurations.
    4.  Update/create DRF serializers and ViewSets.
    5.  Update/create URLs.
    6.  Write backend tests (API tests, model tests, signal tests as appropriate).
    7.  If frontend interaction is needed, update/create React components, services, and contexts.
*   **Running commands:** Use `docker-compose exec backend ...` for Django commands and tests.
*   **Committing changes:** Ensure migration files are committed.
*   **Testing:** Always aim to write tests for new backend logic. Simulate running them if direct execution isn't possible in the agent environment, but note this.

This document should help maintain consistency and understanding when working on this project.Tool output for `create_file_with_block`:
