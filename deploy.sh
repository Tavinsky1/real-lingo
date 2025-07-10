#!/bin/bash
# Deployment script for LingoWorld to slanglingo.run.place

echo "🚀 Starting LingoWorld deployment..."

# Stop any existing Django process
echo "Stopping existing processes..."
sudo pkill -f "gunicorn"
sudo pkill -f "runserver"

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and required system packages
echo "Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx git

# Install/update application
echo "Setting up application..."
cd /var/www || exit
sudo rm -rf lingo_project
sudo git clone https://github.com/yourusername/lingo_project.git || {
    echo "Note: Git clone failed. Please upload files manually."
}

# Set up virtual environment
echo "Setting up Python virtual environment..."
cd lingo_project
sudo python3 -m venv lingo_env
sudo ./lingo_env/bin/pip install -r requirements.txt

# Set up environment variables
echo "Setting up environment variables..."
sudo tee .env > /dev/null << EOF
DJANGO_SECRET_KEY=your-super-secret-key-here-change-this
DJANGO_SETTINGS_MODULE=lingo_project.settings_production
DEBUG=False
EOF

# Collect static files
echo "Collecting static files..."
sudo ./lingo_env/bin/python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
sudo ./lingo_env/bin/python manage.py migrate

# Set permissions
sudo chown -R www-data:www-data /var/www/lingo_project
sudo chmod -R 755 /var/www/lingo_project

echo "✅ Deployment preparation complete!"
echo "Next steps:"
echo "1. Configure Nginx"
echo "2. Set up SSL certificate"
echo "3. Start Gunicorn service"
