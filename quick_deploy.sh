#!/bin/bash
# Quick deployment script for LingoWorld
# Run this on your server (162.120.187.193)

set -e  # Exit on any error

echo "🚀 LingoWorld Quick Deployment Script"
echo "======================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
echo "🔧 Installing dependencies..."
apt install -y python3 python3-pip python3-venv nginx git curl ufw

# Create directories
echo "📁 Creating directories..."
mkdir -p /var/www
mkdir -p /var/log/gunicorn
mkdir -p /var/run/gunicorn

# Stop existing services
echo "🛑 Stopping existing services..."
systemctl stop nginx || true
systemctl stop slanglingo || true
pkill -f gunicorn || true

# Set up application
echo "📂 Setting up application..."
cd /var/www
rm -rf lingo_project
# You'll need to extract the uploaded tar.gz file here
# tar -xzf /tmp/lingo_deployment.tar.gz

echo "🐍 Setting up Python environment..."
cd lingo_project
python3 -m venv lingo_env
./lingo_env/bin/pip install --upgrade pip
./lingo_env/bin/pip install -r requirements.txt

# Generate secret key
echo "🔐 Generating secret key..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Create environment file
echo "⚙️ Creating environment file..."
cat > .env << EOF
DJANGO_SECRET_KEY=$SECRET_KEY
DJANGO_SETTINGS_MODULE=lingo_project.settings_production
DEBUG=False
EOF

# Set up database
echo "🗃️ Setting up database..."
./lingo_env/bin/python manage.py collectstatic --noinput
./lingo_env/bin/python manage.py migrate

# Configure Nginx
echo "🌐 Configuring Nginx..."
cp nginx_slanglingo.conf /etc/nginx/sites-available/slanglingo
ln -sf /etc/nginx/sites-available/slanglingo /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Set up Gunicorn service
echo "🔄 Setting up Gunicorn service..."
cp slanglingo.service /etc/systemd/system/
systemctl daemon-reload

# Set permissions
echo "🔒 Setting permissions..."
chown -R www-data:www-data /var/www/lingo_project
chmod -R 755 /var/www/lingo_project
chown -R www-data:www-data /var/log/gunicorn
chown -R www-data:www-data /var/run/gunicorn

# Configure firewall
echo "🔥 Configuring firewall..."
ufw allow 'Nginx Full'
ufw allow ssh
ufw --force enable

# Start services
echo "▶️ Starting services..."
systemctl start slanglingo
systemctl enable slanglingo
systemctl start nginx
systemctl enable nginx

# Test configuration
echo "🧪 Testing configuration..."
nginx -t

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Your LingoWorld application should now be available at:"
echo "  http://slanglingo.run.place"
echo "  http://162.120.187.193"
echo ""
echo "To check status:"
echo "  systemctl status slanglingo"
echo "  systemctl status nginx"
echo ""
echo "To view logs:"
echo "  tail -f /var/log/gunicorn/slanglingo_error.log"
echo "  tail -f /var/log/nginx/slanglingo.error.log"
