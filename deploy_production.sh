#!/bin/bash

# Production deployment script for Envents

echo "Starting Envents deployment..."

# Navigate to the project directory - update this path as needed
PROJECT_DIR=$(dirname $(realpath $0))
cd $PROJECT_DIR

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setting up environment..."
export DJANGO_SETTINGS_MODULE=envents_project.settings.production

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

echo "Compressing and optimizing..."
python manage.py compress --force

echo "Starting Gunicorn..."
gunicorn --workers 3 --bind 0.0.0.0:8000 envents_project.wsgi:application

echo "Deployment complete!"
