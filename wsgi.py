import sys
import logging

venv_path = '/var/www/ptemeritve/pte_server/venv/lib/python3.14/site-packages'
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/ptemeritve/pte_server")

from app import app as application