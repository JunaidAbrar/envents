#!/bin/bash

# Envents Project Deployment Script for AWS Lightsail
# Run this script on your Lightsail instance

set -e  # Exit on any error

echo "🚀 Starting Envents deployment..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
echo "🐳 Installing Docker..."
sudo apt install -y docker.io docker-compose-v2
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Create project directory
echo "📁 Setting up project directory..."
cd /home/ubuntu
sudo mkdir -p /var/www/envents
sudo chown ubuntu:ubuntu /var/www/envents
cd /var/www/envents

# Clone repository (you'll need to update this with your actual repo URL)
echo "📥 Cloning repository..."
if [ ! -d ".git" ]; then
    git clone https://github.com/JunaidAbrar/envents.git .
else
    git pull origin master
fi

# Copy production environment file
echo "⚙️  Setting up environment..."
if [ ! -f ".env.production" ]; then
    echo "❌ Please create .env.production file with your production settings!"
    echo "You can copy from .env.production.example and update the values."
    exit 1
fi

# Install Certbot for SSL certificates
echo "🔒 Installing Certbot..."
sudo apt install -y certbot

# Stop nginx if running (to free port 80 for certbot)
echo "🔄 Preparing for SSL certificate generation..."
docker-compose down nginx 2>/dev/null || true

# Generate SSL certificates
echo "🔐 Generating SSL certificates..."
sudo certbot certonly --standalone \
    -d enventsbd.com \
    -d www.enventsbd.com \
    --email envents.operation@gmail.com \
    --agree-tos \
    --non-interactive

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 20

# Run migrations
echo "🔄 Running database migrations..."
docker-compose exec -T web python manage.py migrate

# Collect static files (upload to S3)
echo "📦 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Create superuser (optional - comment out if not needed)
echo "👤 Creating superuser (optional)..."
echo "You can create a superuser manually later with:"
echo "docker-compose exec web python manage.py createsuperuser"

# Setup automatic SSL renewal
echo "🔄 Setting up SSL certificate auto-renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && docker-compose restart nginx") | crontab -

# Show status
echo "📊 Checking service status..."
docker-compose ps

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Your site should be available at:"
echo "   - http://13.233.196.42 (IP access)"
echo "   - https://enventsbd.com (with SSL)"
echo "   - https://www.enventsbd.com (with SSL)"
echo ""
echo "📝 Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Restart services: docker-compose restart"
echo "   - Update deployment: git pull && docker-compose up -d --build"
echo "   - Access Django shell: docker-compose exec web python manage.py shell"
echo "   - Create superuser: docker-compose exec web python manage.py createsuperuser"
