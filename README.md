# Envents - Event Management Platform

Django-based event management platform for venues, services, and bookings.

---

## 🚀 Railway Deployment Guide

### Prerequisites
- Railway account ([railway.app](https://railway.app))
- Neon Postgres database (automatically provisioned on Railway or use existing)
- AWS S3 bucket for static/media files

### Environment Variables

Set these environment variables in Railway:

#### **Required**
```bash
SECRET_KEY=<generate-secure-random-key>
DEBUG=False
DJANGO_SETTINGS_MODULE=envents_project.settings.production
DATABASE_URL=<neon-postgres-connection-string>
REDIS_URL=<redis-connection-string>
ALLOWED_HOSTS=enventsbd.com,envents-production.up.railway.app
CSRF_TRUSTED_ORIGINS=https://enventsbd.com,https://envents-production.up.railway.app
```

#### **AWS S3 Storage**
```bash
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>
AWS_STORAGE_BUCKET_NAME=<your-bucket-name>
AWS_S3_REGION_NAME=ap-south-1
```

#### **Email Configuration**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<your-app-password>
DEFAULT_FROM_EMAIL=noreply@enventsbd.com
```

#### **Security (Optional - defaults provided)**
```bash
SECURE_HSTS_SECONDS=31536000  # 1 year for production, use 0 for staging
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Railway Configuration

#### **Services Required**
1. **PostgreSQL (Neon)** - Primary database
2. **Redis** - Caching layer (critical for performance)
   - Add Redis plugin in Railway dashboard
   - Railway will auto-populate `REDIS_URL` variable

#### **Build Command**
```bash
python manage.py collectstatic --noinput
```

#### **Start Command**
```bash
python manage.py migrate && gunicorn envents_project.wsgi:application --bind 0.0.0.0:$PORT
```

Or use the included `Procfile` (Railway auto-detects it):
```
web: gunicorn envents_project.wsgi:application --bind 0.0.0.0:$PORT
```

### Deployment Steps

1. **Connect Repository to Railway**
   ```bash
   # Install Railway CLI (optional)
   npm install -g @railway/cli
   railway login
   railway link
   ```

2. **Add Neon Postgres**
   - In Railway dashboard, click "New" → "Database" → "Add PostgreSQL"
   - Or use existing Neon instance by setting `DATABASE_URL` manually

3. **Set Environment Variables**
   - Copy from `.env.example`
   - Set all required variables in Railway dashboard under "Variables" tab

4. **Deploy**
   - Push to GitHub (Railway auto-deploys)
   - Or use Railway CLI: `railway up`

5. **Create Superuser**
   ```bash
   railway run python manage.py createsuperuser
   ```

6. **Custom Domain (Optional)**
   - Add custom domain in Railway dashboard
   - Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` with your domain

---

## 🛠️ Local Development

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Envents
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Local Development with S3
For local development, you can use the same S3 bucket or local file storage by adjusting settings in `envents_project/settings/development.py`.

---

## ✅ Production Checklist

Run Django's deployment checklist:
```bash
python manage.py check --deploy --settings=envents_project.settings.production
```

Ensure all environment variables are set before running this check.

---

## ⚡ **Performance Optimizations**

The following optimizations are implemented for production performance:

### **Database Optimizations**
- ✅ **Connection Pooling**: `CONN_MAX_AGE=600` keeps connections alive for 10 minutes
- ✅ **Strategic Indexes**: Optimized indexes on frequently queried fields
- ✅ **Query Optimization**: `select_related()` and `prefetch_related()` prevent N+1 queries
- ✅ **Efficient Random Selection**: Database-level random ordering instead of Python memory loading

### **Caching Strategy**
- ✅ **Redis Caching**: Full-page and fragment caching for frequently accessed data
- ✅ **Cache Middleware**: Automatic response caching for anonymous users
- ✅ **Static Data Caching**: Cities, categories cached for 1 hour
- ✅ **Featured Venues**: Smart caching with automatic invalidation

### **Response Optimization**
- ✅ **GZip Compression**: Automatic response compression
- ✅ **Static Files**: Served from AWS S3 with CloudFront-ready configuration
- ✅ **Media Files**: Videos and images served from S3 (not application server)

### **Expected Performance**
- **Homepage Load**: <1-2 seconds (vs 14+ seconds before optimization)
- **Database Queries**: 1-3 per page (vs 15-20 before)
- **Cache Hit Rate**: 80-95% for repeat visitors
- **Connection Overhead**: Near-zero with connection pooling

### **Monitoring Performance**

Check Django cache statistics:
```bash
railway run python manage.py shell
>>> from django.core.cache import cache
>>> cache.get('venue_cities_list')  # Test cache
```

Clear cache if needed:
```bash
railway run python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

---

## 📦 Technology Stack

- **Backend**: Django 5.x
- **Database**: PostgreSQL (Neon)
- **Cache**: Redis (Railway addon)
- **Storage**: AWS S3
- **Web Server**: Gunicorn
- **Hosting**: Railway
- **Frontend**: TailwindCSS

---

## 📝 Notes

- **Fresh Database**: This configuration assumes a fresh database. Old data from docker-compose setups is not migrated.
- **SSL/TLS**: Enforced in production via `SECURE_SSL_REDIRECT` and HSTS headers.
- **Static Files**: Served from S3 (no WhiteNoise in production).
- **Sessions**: Database-backed for reliability.

---

## 🔒 Security

- Never commit `.env` file or secrets to git
- Rotate `SECRET_KEY` regularly
- Use strong passwords for database and admin accounts
- Enable 2FA on AWS and Railway accounts
- Review Railway logs regularly

---

## 🐛 Troubleshooting

### "Please supply the ENGINE value"
- Ensure `DATABASE_URL` is set in Railway environment variables
- Verify the connection string format: `postgresql://user:pass@host:5432/db?sslmode=require`

### "SECURE_HSTS_SECONDS" crash
- Fixed in production.py - now accepts `False`, `0`, `off`, `no` as valid values

### Static files not loading
- Verify S3 credentials are correct
- Check S3 bucket permissions (Block Public Access with proper CORS)
- Run `python manage.py collectstatic` in Railway build step

### Database connection refused
- Verify Neon database is active
- Check `DATABASE_URL` includes `?sslmode=require`
- Ensure Railway has network access to Neon

---

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

**License**: [Add your license]
