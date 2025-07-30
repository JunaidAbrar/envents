# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Install Node.js for Tailwind CSS build
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Build Tailwind CSS
WORKDIR /app/theme/static_src
RUN npm install && npm run build:prod

# Return to app directory
WORKDIR /app

# Collect static files (will upload to S3)
RUN python manage.py collectstatic --noinput --settings=envents_project.settings.production

# Create directory for media files (though we use S3)
RUN mkdir -p /app/media

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "envents_project.wsgi:application"]
