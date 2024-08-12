from django.test import TestCase
from django.urls import reverse
import os
import logging
from http.cookies import SimpleCookie
from django.http import HttpResponse
from rest_framework.test import APIRequestFactory
from custom_auth.views import CustomUserView
import json

class EquipmentTest(TestCase):
  def setUp(self):
    self.factory = APIRequestFactory()
    self.url = reverse('equipment')
    self.auth_token = os.getenv('AUTHORIZATION_TOKEN')
    self.jwt_token = ''
  
  def test_equipment(self):
    request = self.factory.post(
      reverse('user'),
      data=json.dumps({
        'email': 'test@outlook.com.br',
        'name': 'Test User',
        'password': 'test_password',
      }),
      content_type='application/json',
      HTTP_AUTHORIZATION=self.auth_token
    )
    user_view = CustomUserView.as_view()
    response = user_view(request)
    self.assertIn(response.status_code, [201], response.data['Message'])
    
    response = self.client.post(
      reverse('login_user'),
      data = {
        'email': 'test@outlook.com.br',
        'password': 'test_password'
      },
      content_type = 'application/json',
      HTTP_AUTHORIZATION=self.auth_token
    )
    self.assertIn(response.status_code, [202], response.data['Message'])
    
    cookies = SimpleCookie(response.cookies)
    self.jwt_token = cookies.get('jwt').value
    
    response = self.client.post(
      self.url,
      data={
        "equipmentId":"EQ-12495",
        "timestamp": "2023-02-15T01:30:00.000-05:00",
        "value":78.42
      },
      content_type = 'application/json',
      HTTP_AUTHORIZATION=self.auth_token,
      COOKIES = {
        'jwt': self.jwt_token
      }
    )
    self.assertIn(response.status_code, [201], response.data)