#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Wait for the database to be ready
# This is a simple loop, more robust solutions like wait-for-it.sh can be used
echo "Waiting for PostgreSQL to start..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Apply database migrations
echo "Applying database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Collect static files (optional, usually for production, but good practice)
# echo "Collecting static files..."
# python manage.py collectstatic --noinput --clear

# Start server
echo "Starting server..."
exec "$@"
# This will execute the command passed to the Docker container (e.g., runserver or gunicorn)
