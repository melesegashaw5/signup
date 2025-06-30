# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        # psycopg2 dependencies
        libpq-dev \
        gcc \
    # Pillow dependencies (if you use ImageField)
    # libjpeg-dev zlib1g-dev libtiff-dev libfreetype6-dev liblcms2-dev libwebp-dev \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Expose port (if your app runs on a specific port, though Django dev server is started by command)
# EXPOSE 8000

# Add a script to wait for DB if needed, or handle in docker-compose with depends_on healthcheck
# COPY ./entrypoint.sh /app/entrypoint.sh
# RUN chmod +x /app/entrypoint.sh
# ENTRYPOINT ["/app/entrypoint.sh"]

# Default command to run when container starts (can be overridden in docker-compose.yml)
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
