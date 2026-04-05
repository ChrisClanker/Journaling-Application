import os
import sys
import pytest

# Add the journal_project directory to the Python path so Django can find its settings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'journal_project'))

# Ensure test environment variables are set before Django loads
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'journal_project.settings')
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-pytest')
os.environ.setdefault('USE_AI', 'False')
