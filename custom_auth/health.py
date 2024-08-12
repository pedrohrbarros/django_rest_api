from health_check.backends import BaseHealthCheckBackend
from health_check.backends import HealthCheckException
from django.urls import reverse
from django.test import RequestFactory
import os
import logging
from .views import CustomUserView, LoginUserView
from http.cookies import SimpleCookie

class UserHealthCheckBackend(BaseHealthCheckBackend):
  critical_service = False

  def __init__(self):
    super().__init__()
    self.factory = RequestFactory()
    self.parsed_url = reverse('user')
    self.auth_token = os.getenv('AUTHORIZATION_TOKEN')
    self.view = CustomUserView.as_view()

  def check_status(self):
    payload = {
      'email': 'custom_hc@outlook.com.br',
      'name': 'Health Checker',
      'password': 'health_checker',
    }
    request = self.factory.post(
      self.parsed_url,
      data=payload,
      content_type='application/json',
      HTTP_AUTHORIZATION=self.auth_token
    )

    response = self.view(request)

    if response.status_code != 201 and response.status_code != 409:
      raise HealthCheckException(response.data['Message'])

    request = self.factory.post(
      reverse('login_user'),
      data = {
        'email': 'custom_hc@outlook.com.br',
        'password': 'health_checker'
      },
      content_type="application/json",
      HTTP_AUTHORIZATION=self.auth_token
    )
    login_view = LoginUserView().as_view()
    response = login_view(request)
    cookies = SimpleCookie(response.cookies)
    jwt = cookies.get('jwt').value
    
    if response.status_code != 202:
      raise HealthCheckException(response.data['Message'])
    
    request = self.factory.patch(
      self.parsed_url,
      data = {
        'name': 'Custom Health Checker'
      },
      content_type = 'application/json',
    )
    request.COOKIES['jwt'] = jwt 
    response = self.view(request)
    if response.status_code != 202:
      raise HealthCheckException(response.data['Message'])
    
    request = self.factory.get(self.parsed_url)
    request.COOKIES['jwt'] = jwt
    response = self.view(request)
    if response.status_code != 200:
      raise HealthCheckException(response.data['Message'])
    
    request = self.factory.delete(self.parsed_url)
    request.COOKIES['jwt'] = jwt
    response = self.view(request)
    if response.status_code != 202:
      raise HealthCheckException(response.data['Message'])
    return True

  def identifier(self):
    return "User's Endpoint" 