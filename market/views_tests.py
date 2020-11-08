import pytest
import json
from pprint import pprint
from market.models import User, Shop
from rest_framework.test import APIClient
from django.core.management import call_command
import yaml

CLIENT = APIClient()

@pytest.mark.django_db
def test_signup():
    response = CLIENT.post('/signup/', {'username': 'test@user.ru', 'password': 'StRoNg_PasSwOrd111;'})
    assert response.status_code == 200
    assert response.json()['Status'] == True

@pytest.mark.django_db
def test_invalid_signin():
    response = CLIENT.post('/signin/', {'username': 'non-existent@user.ru', 'password': 'qwerty'})
    response = response.json()
    assert 'Errors' in response
    assert response['Status'] == False

@pytest.mark.django_db
def test_valid_signin():
    user = User.objects.create_user('test@user.ru', 'StRoNg_PasSwOrd111;')
    response = CLIENT.post('/signin/', {'username': 'test@user.ru', 'password': 'StRoNg_PasSwOrd111;'})
    response = response.json()
    assert 'Errors' not in response
    assert response['Status'] == True
    assert response['Test'] == 'OK'

@pytest.mark.django_db
def test_create_contacts():
    user = User.objects.create_user('test@user.ru', 'StRoNg_PasSwOrd111;')
    CLIENT.login(username='test@user.ru', password='StRoNg_PasSwOrd111;')
    response = CLIENT.post('/contacts/', {'city': 'gorod', 'street': 'ulitsa', 'phone': '+12345678', 'house': 50})
    response = response.json()
    assert response['city'] == 'gorod'

@pytest.mark.django_db
def test_get_shop_list():
    shop = Shop.objects.create(name='Ситилинк')
    shop = Shop.objects.create(name='DNS')
    response = CLIENT.get('/shops/')
    response = response.json()
    assert len(response) == 2
    for shop in response:
        assert shop['name'] == 'Ситилинк' or shop['name'] == 'DNS'

@pytest.mark.django_db
def test_partner_update():
    user = User.objects.create_user('test@user.ru', 'StRoNg_PasSwOrd111;', type='shop')
    CLIENT.login(username='test@user.ru', password='StRoNg_PasSwOrd111;')
    with open('market/fixtures/shop1.yaml') as f:
        data = f
        response = CLIENT.post('/partner_update/', {'data': data})
        response = response.json()
        assert response['Status'] == True
