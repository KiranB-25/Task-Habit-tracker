import os
import sys
from pathlib import Path

# Add project root to sys.path so Django can discover modules on Vercel
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application

# Vercel serverless WSGI entry point
app = get_wsgi_application()
