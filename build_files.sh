#!/bin/bash
echo "=== BUILD START ==="
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear

if [ -n "$DATABASE_URL" ]; then
    echo "Running migrations for DATABASE_URL..."
    python3 manage.py migrate --noinput
fi
echo "=== BUILD COMPLETE ==="
