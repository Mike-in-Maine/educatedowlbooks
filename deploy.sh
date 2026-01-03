#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "------------------------------------------"
echo "🚀 Starting Deployment: Educated Owl Books"
echo "------------------------------------------"

# 1. Enter the project directory
cd /var/www/educatedowlbooks.com

# 2. Get the latest code from GitHub
echo "📥 Pulling latest code..."
git fetch origin
git checkout main
git pull --ff-only origin main
# git reset --hard origin/main

# 3. Activate Virtual Environment
echo "🐍 Activating environment..."
source venv/bin/activate

# 4. Update Python Packages
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# 5. Apply Database Changes
echo "🗄️ Running migrations..."
python manage.py migrate --settings=config.settings_prod

# 6. Prepare Static Files (CSS/JS)
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings_prod

# 7. Fix Permissions (Crucial for Gunicorn/Nginx access)
echo "🔒 Adjusting permissions..."
chown -R root:www-data /var/www/educatedowlbooks.com
chmod -R 775 /var/www/educatedowlbooks.com

# 8. Restart the Web Server
echo "🔄 Restarting Gunicorn..."
systemctl restart gunicorn-educatedowlbooks.service

echo "------------------------------------------"
echo "✅ Deployment Successful! Site is live."
echo "------------------------------------------"
