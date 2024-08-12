from health_check.backends import BaseHealthCheckBackend
from health_check.backends import HealthCheckException
from django.urls import reverse
from django.test import RequestFactory
import os
import logging
from .views import EquipmentView
from custom_auth.views import LoginUserView
from http.cookies import SimpleCookie

class EquipmentHealthCheckBackend(BaseHealthCheckBackend):
  critical_service = False
  
  def __init__(self):
    super().__init__()
    self.factory = RequestFactory()
    self.parsed_url = reverse('equipment')
    self.auth_token = os.getenv('AUTHORIZATION_TOKEN')
    self.view = EquipmentView.as_view()
  
  def check_status(self):
    payload = {
      "equipmentId":"EQ-12495",
      "timestamp": "2023-02-15T01:30:00.000-05:00",
      "value":78.42
    }
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
    
    request = self.factory.post(
      self.parsed_url,
      data={
        "equipmentId":"EQ-12495",
        "timestamp": "2023-02-15T01:30:00.000-05:00",
        "value":78.42
      },
      content_type = 'application/json',
      HTTP_AUTHORIZATION=self.auth_token,
    )
    request.COOKIES['jwt'] = jwt
    response = self.view(request)
    if response.status_code != 201:
      raise HealthCheckException(response.data['Message'])
    return True
  def identifier(self):
    return "Equipment's Endpoint" 