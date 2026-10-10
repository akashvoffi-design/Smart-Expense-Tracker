#!/bin/bash
set -e
echo "=== BUILD START ==="

# Ensure the output directory exists
mkdir -p staticfiles_build/static

# Create and activate an isolated virtual environment to comply with PEP 668
if python3 -m venv .build_venv 2>/dev/null; then
    echo "Virtual environment created successfully."
    source .build_venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    python manage.py collectstatic --noinput --clear
    if [ -n "$DATABASE_URL" ]; then
        echo "Running database migrations..."
        python manage.py migrate --noinput || echo "Migrations skipped or deferred."
    fi
else
    echo "Falling back to pip with --break-system-packages..."
    python3 -m pip install --break-system-packages -r requirements.txt || python3 -m pip install -r requirements.txt
    python3 manage.py collectstatic --noinput --clear
    if [ -n "$DATABASE_URL" ]; then
        echo "Running database migrations..."
        python manage.py migrate --noinput || echo "Migrations skipped or deferred."
    fi
fi

echo "=== BUILD COMPLETE ==="
