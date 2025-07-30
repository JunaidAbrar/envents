# C**Key points:**
- Django 5.0 web application using Python
- NeonDB (fully managed PostgreSQL database)
- AWS S3 storage, Tailwind CSS
- Authentication system with custom User model
- Multiple Django apps: accounts, venues, services, bookings, business
- REST Framework for API endpoints
- Email functionality via SMTP
- File uploads handled via S3 storage
- Redis for caching and sessionsot Instructions - Django Deployment to AWS Lightsail

## Project Context
- Django 5.0+ events management app (`envents_project`)
- PostgreSQL database, AWS S3 storage, Tailwind CSS
- Domain: enventsbd.com (Hostinger DNS)
- Lightsail SSH: `ssh -i ~/Desktop/Envents/keys/LightsailDefaultKey-ap-south-1.pem ubuntu@13.233.196.42`

## Key Files & Structure
```
envents_project/
├── envents_project/settings/
│   ├── base.py (core settings)
│   ├── development.py (current working config)
│   └── production.py (commented out - needs completion)
├── envents_project/s3_storage.py (unified S3 config)
├── theme/ (Tailwind CSS app)
└── requirements.txt
```

## Critical Implementation Points

### 1. Production Settings (`production.py`)
When user asks to create/fix production.py, uncomment and use this structure:
- Import from base.py and s3_storage
- Set DEBUG=False, proper ALLOWED_HOSTS
- Use `apply_s3_settings(locals())` for S3
- Add security headers (SSL redirect, HSTS, etc.)
- Environment variables for all secrets
- Database config pointing to 'db' service

### 2. Docker Configuration
**Dockerfile essentials:**
- Python 3.11-slim base
- Install Node.js for Tailwind build
- Copy requirements, install pip packages
- Run `npm install && npm run build:prod` in theme/static_src/
- Collect static files
- Gunicorn WSGI server

**docker-compose.yml structure:**
- web service (Django app)
- redis service (caching)
- nginx service (reverse proxy with SSL)
- Uses NeonDB (external managed database)
- Use .env.production for environment variables

### 3. Environment Variables (.env.production)
Required variables:
```
SECRET_KEY, DEBUG=False, ALLOWED_HOSTS
DB_NAME, DB_USER, DB_PASSWORD, DB_HOST (NeonDB connection details)
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME
EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
```

### 4. Deployment Commands
SSH into Lightsail, then:
```bash
# Install Docker
sudo apt update && sudo apt install docker.io docker-compose -y

# Clone repo, setup environment
git clone [repo] && cd [project]
cp .env.example .env.production  # edit with real values

# Deploy
docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Troubleshooting Checklist

### S3 Issues
- Check AWS credentials in .env.production
- Verify bucket policy allows public read for static/*
- Confirm CORS settings for domain

### Tailwind CSS Issues
- Ensure npm build runs in Dockerfile
- Check theme/static/css/dist/styles.css exists after build
- Verify collectstatic uploads to S3

### Domain/SSL Issues
- DNS A records: @ and www → Lightsail IP
- Use Let's Encrypt: `certbot --standalone -d enventsbd.com -d www.enventsbd.com`
- Update nginx.conf with SSL certificate paths

## Quick Commands Reference
```bash
# Logs
docker-compose logs -f web

# Update deployment
git pull && docker-compose up -d --build

# Debug shell
docker-compose exec web python manage.py shell
```

## Important Notes for Copilot
1. **Never set DEBUG=True in production**
2. **Always use environment variables for secrets**
3. **The s3_storage.py module handles S3 config - use `apply_s3_settings(locals())`**
4. **Tailwind build must happen in Docker build process**
5. **Database host must be 'db' (Docker service name)**
6. **User has working development setup - replicate that config for production**

## When User Needs Help
- Ask for specific error messages or logs
- Check if it's S3, database, or CSS-related issue
- Verify environment variables are set correctly
- Test with `docker-compose exec web python manage.py check --deploy`