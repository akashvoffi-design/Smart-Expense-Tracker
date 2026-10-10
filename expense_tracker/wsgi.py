"""
WSGI config for expense_tracker project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')

application = get_wsgi_application()
app = application

# Auto-migrate SQLite on Vercel if external database is not configured
if os.environ.get('VERCEL') and not os.environ.get('DATABASE_URL'):
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
    except Exception as e:
        print(f"Vercel auto-migration status: {e}")
