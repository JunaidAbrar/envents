# Envents Production Deployment Guide

## Prerequisites
- AWS Lightsail instance running Ubuntu
- Domain pointed to Lightsail IP (enventsbd.com → 13.233.196.42)
- SSH access to Lightsail instance

## Step 1: Upload Files to Lightsail

First, copy your project files to the Lightsail instance:

```bash
# From your local machine
scp -i ~/Desktop/Envents/keys/LightsailDefaultKey-ap-south-1.pem -r ~/Desktop/Envents ubuntu@13.233.196.42:/tmp/
```

## Step 2: SSH into Lightsail and Setup

```bash
# SSH into your Lightsail instance
ssh -i ~/Desktop/Envents/keys/LightsailDefaultKey-ap-south-1.pem ubuntu@13.233.196.42

# Move files to proper location
sudo mkdir -p /var/www/envents
sudo mv /tmp/Envents/* /var/www/envents/
sudo chown -R ubuntu:ubuntu /var/www/envents
cd /var/www/envents

# Make deployment script executable
chmod +x deploy.sh
```

## Step 3: Run Deployment Script

```bash
# Run the automated deployment script
./deploy.sh
```

## Step 4: Manual Steps (if needed)

If you prefer manual deployment:

```bash
# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker ubuntu
sudo systemctl start docker
sudo systemctl enable docker

# Build and start services
docker-compose up -d --build

# Wait for services to start
sleep 30

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Check status
docker-compose ps
```

## Step 5: SSL Certificate Setup

```bash
# Install certbot
sudo apt install -y certbot

# Stop nginx temporarily
docker-compose stop nginx

# Generate SSL certificates
sudo certbot certonly --standalone \
  -d enventsbd.com \
  -d www.enventsbd.com \
  --email envents.operation@gmail.com \
  --agree-tos

# Restart nginx with SSL
docker-compose start nginx
```

## Step 6: Verify Deployment

1. Check services are running:
   ```bash
   docker-compose ps
   ```

2. Check logs:
   ```bash
   docker-compose logs -f web
   ```

3. Test URLs:
   - http://13.233.196.42 (IP access)
   - https://enventsbd.com (domain with SSL)

## Troubleshooting

### Common Issues:

1. **Static files not loading**: Check S3 credentials and run:
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

2. **Database connection errors**: Check if PostgreSQL is running:
   ```bash
   docker-compose logs db
   ```

3. **SSL certificate issues**: Ensure domain DNS is properly configured and try:
   ```bash
   sudo certbot certificates
   ```

4. **Permission issues**: Fix ownership:
   ```bash
   sudo chown -R ubuntu:ubuntu /var/www/envents
   ```

## Maintenance Commands

```bash
# View logs
docker-compose logs -f [service_name]

# Restart services
docker-compose restart

# Update deployment
git pull && docker-compose up -d --build

# Backup database
docker-compose exec db pg_dump -U postgres envents > backup_$(date +%Y%m%d).sql

# Django management commands
docker-compose exec web python manage.py [command]
```

## Environment Variables

Make sure your `.env.production` file has all required variables:

- SECRET_KEY
- DEBUG=False
- ALLOWED_HOSTS
- Database settings (DB_HOST=db)
- AWS S3 credentials
- Email settings
- Redis URL (redis://redis:6379/1)

## Security Notes

1. SSL certificates auto-renew via cron job
2. Security headers are configured in nginx
3. Database and Redis are isolated in Docker network
4. Static/media files served via S3 (more secure and faster)
