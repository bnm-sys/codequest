#!/bin/bash
set -e

echo "🚀 Starting CodeQuest Setup..."

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source env/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check PostgreSQL connection
echo "🔍 Checking PostgreSQL connection..."
if ! python3 check_db_status.py 2>/dev/null; then
    echo "❌ PostgreSQL not accessible. Ensure Docker container is running on port 15432."
    exit 1
fi

# Run migrations
echo "🗄️  Applying database migrations..."
python manage.py migrate --noinput

# Create superuser if not exists
echo "👤 Setting up admin user..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123');
    print('✓ Admin user created');
else:
    print('✓ Admin user already exists');
" 2>/dev/null || true

# Run tests
echo "🧪 Running tests..."
pytest -q

echo "✅ Setup complete!"
echo ""
echo "📋 Quick Start:"
echo "   - Run server: ./env/bin/python manage.py runserver 0.0.0.0:8001"
echo "   - Admin panel: http://localhost:8001/admin"
echo "   - Mailhog UI: http://localhost:8025"
echo "   - Admin credentials: admin / admin123"
echo ""
