from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.urls import reverse
import os
from .views import CustomUserView, LoginUserView
import json
import logging
from http.cookies import SimpleCookie
from django.http import HttpResponse

class UserTest(TestCase):
  def setUp(self):
    self.view = CustomUserView.as_view()
    self.factory = APIRequestFactory()
    self.url = reverse('user')
    self.auth_token = os.getenv("AUTHORIZATION_TOKEN")
    self.jwt_token = ''

  def test_user(self):
    request = self.factory.post(
      self.url,
      data=json.dumps({
        'email': 'test@outlook.com.br',
        'name': 'Test User',
        'password': 'test_password',
      }),
      content_type='application/json',
      HTTP_AUTHORIZATION=self.auth_token
    )
    response = self.view(request)
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
    
    response = self.client.patch(
      self.url,
      data = {
        'name': 'Test User Updated'
      },
      content_type = 'application/json',
      COOKIES = {
        'jwt': self.jwt_token
      }
    )
    self.assertIn(response.status_code, [202], response.data)
    
    response = self.client.get(self.url, COOKIES = { 'jwt': self.jwt_token })
    self.assertIn(response.status_code, [200], response.data)
    
    response = self.client.delete(self.url, COOKIES = { 'jwt': self.jwt_token })
    self.assertIn(response.status_code, [202], response.data)