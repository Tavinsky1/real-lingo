# LingoWorld Deployment Guide
## Deploy to slanglingo.run.place (162.120.187.193)

This guide walks you through deploying the LingoWorld application to your server.

## Prerequisites

1. **Server Access**: SSH access to your server at 162.120.187.193
2. **Domain**: Domain `slanglingo.run.place` pointed to your server IP
3. **Root/Sudo Access**: Administrative privileges on the server

## Step 1: DNS Configuration

Make sure your domain `slanglingo.run.place` points to `162.120.187.193`:

```bash
# Check DNS resolution
nslookup slanglingo.run.place
dig slanglingo.run.place
```

**DNS Records needed:**
- A record: `slanglingo.run.place` → `162.120.187.193`
- Optional CNAME: `www.slanglingo.run.place` → `slanglingo.run.place`

## Step 2: Server Preparation

SSH into your server:
```bash
ssh root@162.120.187.193
# or
ssh username@162.120.187.193
```

### Update system and install dependencies:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx git curl
```

### Create directories:
```bash
sudo mkdir -p /var/www
sudo mkdir -p /var/log/gunicorn
sudo mkdir -p /var/run/gunicorn
```

## Step 3: Upload Application Files

### Option A: Upload files directly (recommended for first deployment)
```bash
# On your local machine, create a deployment package
cd /Users/tavinsky/lingo_project
tar -czf lingo_project.tar.gz \
  --exclude='lingo_env' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  .

# Upload to server
scp lingo_project.tar.gz root@162.120.187.193:/tmp/

# On server, extract files
ssh root@162.120.187.193
cd /var/www
sudo tar -xzf /tmp/lingo_project.tar.gz
sudo mv lingo_project slanglingo  # Optional: rename for clarity
cd slanglingo  # or lingo_project
```

### Option B: Git clone (if you have a repository)
```bash
cd /var/www
sudo git clone https://github.com/yourusername/lingo_project.git
cd lingo_project
```

## Step 4: Set Up Python Environment

```bash
cd /var/www/lingo_project  # or your chosen directory name
sudo python3 -m venv lingo_env
sudo ./lingo_env/bin/pip install --upgrade pip
sudo ./lingo_env/bin/pip install -r requirements.txt
```

## Step 5: Configure Environment Variables

```bash
sudo cp .env.template .env
sudo nano .env  # Edit with your values
```

**Required .env content:**
```bash
DJANGO_SECRET_KEY=your-super-secret-random-key-here
DJANGO_SETTINGS_MODULE=lingo_project.settings_production
DEBUG=False
```

**Generate a secret key:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 6: Database Setup

```bash
# Collect static files
sudo ./lingo_env/bin/python manage.py collectstatic --noinput

# Run migrations
sudo ./lingo_env/bin/python manage.py migrate

# Create superuser (optional)
sudo ./lingo_env/bin/python manage.py createsuperuser
```

## Step 7: Configure Nginx

```bash
# Copy nginx configuration
sudo cp nginx_slanglingo.conf /etc/nginx/sites-available/slanglingo
sudo ln -s /etc/nginx/sites-available/slanglingo /etc/nginx/sites-enabled/

# Remove default site if needed
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## Step 8: Set Up Gunicorn Service

```bash
# Copy systemd service file
sudo cp slanglingo.service /etc/systemd/system/

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl start slanglingo
sudo systemctl enable slanglingo

# Check service status
sudo systemctl status slanglingo
```

## Step 9: Set Permissions

```bash
sudo chown -R www-data:www-data /var/www/lingo_project
sudo chmod -R 755 /var/www/lingo_project
sudo chown -R www-data:www-data /var/log/gunicorn
sudo chown -R www-data:www-data /var/run/gunicorn
```

## Step 10: Firewall Configuration

```bash
# Allow HTTP and HTTPS traffic
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw --force enable
```

## Step 11: Test Deployment

1. **Test HTTP access:**
   - Visit: http://slanglingo.run.place
   - Visit: http://162.120.187.193

2. **Check logs if issues occur:**
```bash
# Nginx logs
sudo tail -f /var/log/nginx/slanglingo.error.log
sudo tail -f /var/log/nginx/slanglingo.access.log

# Gunicorn logs
sudo tail -f /var/log/gunicorn/slanglingo_error.log
sudo tail -f /var/log/gunicorn/slanglingo_access.log

# Django logs
sudo tail -f /var/www/lingo_project/django.log

# Service status
sudo systemctl status slanglingo
sudo systemctl status nginx
```

## Step 12: SSL Certificate (Optional but Recommended)

### Using Let's Encrypt (free SSL):
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d slanglingo.run.place

# Test automatic renewal
sudo certbot renew --dry-run
```

## Troubleshooting

### Common Issues:

1. **Service won't start:**
   ```bash
   sudo systemctl status slanglingo
   sudo journalctl -u slanglingo -f
   ```

2. **Permission errors:**
   ```bash
   sudo chown -R www-data:www-data /var/www/lingo_project
   ```

3. **Static files not loading:**
   ```bash
   sudo ./lingo_env/bin/python manage.py collectstatic --noinput
   ```

4. **Database errors:**
   ```bash
   sudo ./lingo_env/bin/python manage.py migrate
   ```

## Updating the Application

```bash
# Stop service
sudo systemctl stop slanglingo

# Update code (git pull or upload new files)
# Reinstall dependencies if needed
sudo ./lingo_env/bin/pip install -r requirements.txt

# Collect static files
sudo ./lingo_env/bin/python manage.py collectstatic --noinput

# Run migrations
sudo ./lingo_env/bin/python manage.py migrate

# Restart service
sudo systemctl start slanglingo
```

## Success Indicators

If everything is working correctly:
- ✅ `http://slanglingo.run.place` loads the LingoWorld homepage
- ✅ All three countries (Argentina, Germany, Australia) are accessible
- ✅ Search functionality works
- ✅ Static files (CSS, JS) load properly
- ✅ Admin panel accessible at `/admin/`

## Contact

For issues with deployment, check the logs and ensure all steps were followed correctly. The application should now be live at `slanglingo.run.place`!
