# pytest 통합테스트!

import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Cash, CashTransaction, CashTransfer
import factory
from factory.django import DjangoModelFactory

# Factories
class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    name = factory.Sequence(lambda n: f'User {n}')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

class CashFactory(DjangoModelFactory):
    class Meta:
        model = Cash

    user = factory.SubFactory(UserFactory)
    balance = Decimal('0.00')

# Fixtures
@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user1():
    return UserFactory()

@pytest.fixture
def user2():
    return UserFactory()

@pytest.fixture
def cash1(user1):
    return CashFactory(user=user1, balance=Decimal('1000.00'))

@pytest.fixture
def cash2(user2):
    return CashFactory(user=user2, balance=Decimal('500.00'))

# Tests
@pytest.mark.django_db
class TestUserRegistration:
    def test_user_registration(self, api_client):
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'name': 'New User',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'birthdate': '1990-01-01'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == 302  # Redirect to login
        assert get_user_model().objects.filter(email='newuser@example.com').exists()
        
        # Check if Cash account was created
        user = get_user_model().objects.get(email='newuser@example.com')
        assert Cash.objects.filter(user=user).exists()

@pytest.mark.django_db
class TestCashOperations:
    def test_deposit(self, api_client, user1, cash1):
        api_client.force_authenticate(user=user1)
        url = reverse('cash-deposit')
        data = {'amount': '500.00'}
        
        initial_balance = cash1.balance
        response = api_client.post(url, data)
        
        cash1.refresh_from_db()
        assert response.status_code == 302  # Redirect to success page
        assert cash1.balance == initial_balance + Decimal('500.00')
        assert CashTransaction.objects.filter(
            user=user1,
            transaction_type='deposit',
            amount=Decimal('500.00')
        ).exists()

    def test_withdraw(self, api_client, user1, cash1):
        api_client.force_authenticate(user=user1)
        url = reverse('cash-withdraw')
        data = {'amount': '300.00'}
        
        initial_balance = cash1.balance
        response = api_client.post(url, data)
        
        cash1.refresh_from_db()
        assert response.status_code == 302
        assert cash1.balance == initial_balance - Decimal('300.00')
        assert CashTransaction.objects.filter(
            user=user1,
            transaction_type='withdraw',
            amount=Decimal('300.00')
        ).exists()

    def test_insufficient_funds_withdraw(self, api_client, user1, cash1):
        api_client.force_authenticate(user=user1)
        url = reverse('cash-withdraw')
        data = {'amount': '2000.00'}  # More than balance
        
        initial_balance = cash1.balance
        response = api_client.post(url, data)
        
        cash1.refresh_from_db()
        assert cash1.balance == initial_balance  # Balance shouldn't change
        assert not CashTransaction.objects.filter(
            user=user1,
            transaction_type='withdraw',
            amount=Decimal('2000.00')
        ).exists()

@pytest.mark.django_db
class TestTransfer:
    def test_successful_transfer(self, api_client, user1, user2, cash1, cash2):
        api_client.force_authenticate(user=user1)
        url = reverse('cash-transfer')  # 'transfer' -> 'cash-transfer'로 수정
        data = {
            'receiver_email': user2.email,
            'amount': '500.00',
            'memo': 'Test transfer'
        }
        
        sender_initial = cash1.balance
        receiver_initial = cash2.balance
        
        response = api_client.post(url, data)
        
        cash1.refresh_from_db()
        cash2.refresh_from_db()
        
        assert response.status_code == 302
        assert cash1.balance == sender_initial - Decimal('500.00')
        assert cash2.balance == receiver_initial + Decimal('500.00')
        
        # Check transfer record
        transfer = CashTransfer.objects.filter(
            sender=user1,
            receiver=user2,
            amount=Decimal('500.00')
        ).first()
        assert transfer is not None
        
        # Check transaction records
        assert CashTransaction.objects.filter(
            user=user1,
            transaction_type='transfer',
            amount=Decimal('500.00'),
            related_transfer=transfer
        ).exists()
        
        assert CashTransaction.objects.filter(
            user=user2,
            transaction_type='deposit',
            amount=Decimal('500.00'),
            related_transfer=transfer
        ).exists()
@pytest.mark.django_db
class TestTransfer:
    def test_successful_transfer(self, api_client, user1, user2, cash1, cash2):
        api_client.force_authenticate(user=user1)
        url = reverse('cash-transfer')  # 'transfer' -> 'cash-transfer'로 수정
        data = {
            'receiver_email': user2.email,
            'amount': '500.00',
            'memo': 'Test transfer'
        }
        
        sender_initial = cash1.balance
        receiver_initial = cash2.balance
        
        response = api_client.post(url, data)
        
        cash1.refresh_from_db()
        cash2.refresh_from_db()
        
        assert response.status_code == 302
        assert cash1.balance == sender_initial - Decimal('500.00')
        assert cash2.balance == receiver_initial + Decimal('500.00')
        
        # Check transfer record
        transfer = CashTransfer.objects.filter(
            sender=user1,
            receiver=user2,
            amount=Decimal('500.00')
        ).first()
        assert transfer is not None
        
        # Check transaction records
        assert CashTransaction.objects.filter(
            user=user1,
            transaction_type='transfer',
            amount=Decimal('500.00'),
            related_transfer=transfer
        ).exists()
        
        assert CashTransaction.objects.filter(
            user=user2,
            transaction_type='deposit',
            amount=Decimal('500.00'),
            related_transfer=transfer
        ).exists()
