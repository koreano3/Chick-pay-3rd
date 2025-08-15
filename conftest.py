import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')  # 실제 경로로

import django
django.setup()

import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()
