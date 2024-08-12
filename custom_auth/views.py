from django_rest_api import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from .serializer import CustomUserSerializer
from rest_framework.permissions import AllowAny
import jwt, datetime
from .models import CustomUser
from rest_framework.exceptions import AuthenticationFailed
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
import os
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.views.decorators.csrf import csrf_exempt

class LoginUserView(GenericAPIView):
  permission_classes = [AllowAny]
  serializer_class = CustomUserSerializer
  
  @swagger_auto_schema(
    operation_description="Login with the built-in authentication structure from the server.",
    tags = ["User"],
    request_body = openapi.Schema(
      type = openapi.TYPE_OBJECT,
      properties = {
        'email': openapi.Schema(type = openapi.TYPE_STRING, description = "User's email"),
        'password': openapi.Schema(type = openapi.TYPE_STRING, description = "User's password")
      }
    ),
    responses = {
      status.HTTP_429_TOO_MANY_REQUESTS: openapi.Response(
        description = "Too many login attempts were made in a short period of time",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "Too many login attempts. Try again later.")
          }
        )
      ),
      status.HTTP_404_NOT_FOUND: openapi.Response(
        description="User was not found registered in database",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "User not found")
          }
        )
      ),
      status.HTTP_400_BAD_REQUEST: openapi.Response(
        description="Password was incorrect related to the user that was tried to log-in",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "Incorrect password")
          }
        )
      ),
      status.HTTP_202_ACCEPTED: openapi.Response(
        description = "Login was made successfully and token was set in cookies headers",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "Token successfully created")
          }
        )
      ),
      status.HTTP_401_UNAUTHORIZED: openapi.Response(
        description="Wrong authorization token provided in header",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type=openapi.TYPE_STRING, description='Wrong authorization token'),
          },
        ),
      ),
    }
  )
  def post(self, request):
    if request.headers.get('Authorization') != os.getenv('AUTHORIZATION_TOKEN'):
      return Response({ 'Message': 'Wrong authorization token' }, status = status.HTTP_401_UNAUTHORIZED)
    email = request.data['email']
    password = request.data['password']
    user = CustomUser.objects.filter(email=email, is_active = True).first()
    if user is None:
      user_ip = request.META.get('REMOTE_ADDR')
      login_attempts = cache.get(f'login_attempts:{user_ip}', 0)
      cache.set(f'login_attempts:{user_ip}', login_attempts + 1, timeout=settings.LOGIN_ATTEMPT_TIMEOUT)

      if login_attempts + 1 >= settings.MAX_LOGIN_ATTEMPTS:
        return Response({
          "Message": "Too many login attempts. Try again later."
        }, status = status.HTTP_429_TOO_MANY_REQUESTS)
      return Response({
        "Message": "User not found"
      }, status = status.HTTP_404_NOT_FOUND)
    if not user.check_password(password):
      user_ip = request.META.get('REMOTE_ADDR')
      login_attempts = cache.get(f'login_attempts:{user_ip}', 0)
      cache.set(f'login_attempts:{user_ip}', login_attempts + 1, timeout=settings.LOGIN_ATTEMPT_TIMEOUT)

      if login_attempts + 1 >= settings.MAX_LOGIN_ATTEMPTS:
        return Response({
          "Message": "Too many login attempts. Try again later."
        }, status = status.HTTP_429_TOO_MANY_REQUESTS)
      return Response({
        "Message": "Incorrect password"
      }, status = status.HTTP_400_BAD_REQUEST)
    payload = {
      'id': user.id,
      'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
      'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, 'secret', algorithm='HS256')
    user_ip = request.META.get('REMOTE_ADDR')
    cache.delete(f'login_attempts:{user_ip}')
    response = Response()
    response.set_cookie(key='jwt', value = token, httponly=True)
    response.data = {
      'Message': "Token successfully created"
    }
    response.status_code = status.HTTP_202_ACCEPTED
    user.last_login = timezone.now()
    user.save()
    return response
  
class CustomUserView(GenericAPIView):
  permission_classes = [AllowAny]
  serializer_class = CustomUserSerializer
  queryset = CustomUser.objects.all()
  
  @swagger_auto_schema(
    operation_description="Get your own user data from the Django Rest API database based in your JWT token create by login endpoint",
    tags = ["User"],
    responses={
      status.HTTP_401_UNAUTHORIZED: openapi.Response(
        description = "User without JWT Token, so either it is expired or it wasn't created, either way it is needed to log-in again",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type=openapi.TYPE_STRING, description='Unauthenticated'),
          }
        )
      ),
      status.HTTP_410_GONE: openapi.Response(
        description = "JWT Token expired, log-in again to get a new one",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "Expired Token")
          }
        )
      ),
      status.HTTP_404_NOT_FOUND: openapi.Response(
        description = "User not found for this JWT Token, maybe user was unactive meanwhile auth process",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "User not found")
          }
        )
      ),
      status.HTTP_200_OK: openapi.Response(
        description = "User found successfully",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'name': openapi.Schema(type = openapi.TYPE_STRING, description = "User's name"),
            'email': openapi.Schema(type = openapi.TYPE_STRING, description = "User's email"),
          }
        )
      )
    }
  )
  def get(self, request, format='json'):
    token = request.COOKIES.get('jwt')
    if not token:
      return Response({
        'Message': 'Unauthenticated'
      }, status = status.HTTP_401_UNAUTHORIZED)
    try:
      payload = jwt.decode(token, 'secret', algorithms = ["HS256"])
    except jwt.ExpiredSignatureError:
      return Resppnse({
        'Message': 'Expired Token'
      }, status = status.HTTP_410_GONE)
    user = CustomUser.objects.filter(id=payload['id'],is_active=True).first()
    if user is not None:
      serializer = CustomUserSerializer(user)
    else:
      return Response({
        'Message': "User not found"
      }, status = status.HTTP_404_NOT_FOUND)
    return Response(serializer.data, status = status.HTTP_200_OK)

  @swagger_auto_schema(
    operation_description="Register a new user to Django Rest API database.",
    tags = ["User"],
    responses={
      status.HTTP_401_UNAUTHORIZED: openapi.Response(
        description = "Wrong authorization token provided in header",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type=openapi.TYPE_STRING, description='Wrong authorization token'),
          }
        )
      ),
      status.HTTP_400_BAD_REQUEST: openapi.Response(
        description = "Some field was not correctly typed or filled",
        schema = openapi.Schema(
          type= openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type=openapi.TYPE_STRING, description='Field {field_name} is required'),
          } 
        )  
      ),
      status.HTTP_409_CONFLICT: openapi.Response(
        description = "The user already exists in the database",
        schema = openapi.Schema(
          type=openapi.TYPE_OBJECT,
          properties={
            "Message": openapi.Schema(type=openapi.TYPE_STRING, description = "User already exists")
          }
        ) 
      ),
      status.HTTP_201_CREATED: openapi.Response(
        description="User created successfully inside database, and already can be used to log-in",
        schema=openapi.Schema(
          type=openapi.TYPE_OBJECT,
          properties={
            'Message': openapi.Schema(type=openapi.TYPE_STRING, description='User created successfully'),
          }
        )
      )
    }
  )
  def post(self, request):
    if request.headers.get('Authorization') != os.getenv('AUTHORIZATION_TOKEN'):
      return Response({ 'Message': 'Wrong authorization token' }, status = status.HTTP_401_UNAUTHORIZED)
    try:
      required_fields = ['name', 'email', 'password']
      for field in required_fields:
        if field not in request.data:
          return Response({
            "Message": f"Field: {field} is required"
          }, status = status.HTTP_400_BAD_REQUEST)
      email = request.data['email']
      password = request.data['password']
      user = CustomUser.objects.filter(email=email).first()
      if user is not None:
        return Response({
          "Message": "User already exists"
        }, status = status.HTTP_409_CONFLICT)
      serializer = CustomUserSerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      serializer.save()
      return Response({
        'Message': 'User created successfully'
      }, status = status.HTTP_201_CREATED)
    except Exception as error:
      logging.error(error, exc_info = True)
      return Response({
        'Message': 'Error while creating user'
      }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
  
  @swagger_auto_schema(
    operation_description="Patch users' information, only name or email allowed",
    tags = ["User"],
    request_body = openapi.Schema(
      type = openapi.TYPE_OBJECT,
      properties = {
        'email': openapi.Schema(type = openapi.TYPE_STRING, description = "New user's email"),
        'password': openapi.Schema(type = openapi.TYPE_STRING, description = "New user's password"),
        'name': openapi.Schema(type = openapi.TYPE_STRING, description = "New user's name")
      }
    ),
    responses={
      status.HTTP_401_UNAUTHORIZED: openapi.Response(
        description = "User without JWT Token, so either it is expired or it wasn't created, either way it is needed to log-in again",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type=openapi.TYPE_STRING, description='Unauthenticated'),
          }
        )
      ),
      status.HTTP_410_GONE: openapi.Response(
        description = "JWT Token expired, log-in again to get a new one",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "Expired Token")
          }
        )
      ),
      status.HTTP_404_NOT_FOUND: openapi.Response(
        description = "User not found for this JWT Token, maybe user was unactive meanwhile auth process",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "User not found")
          }
        )
      ),
      status.HTTP_202_ACCEPTED: openapi.Response(
        description = "User updated successfully",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'name': openapi.Schema(type = openapi.TYPE_STRING, description = "User's name"),
            'email': openapi.Schema(type = openapi.TYPE_STRING, description = "User's email"),
          }
        )
      )
    }
  )
  def patch(self, request):
    token = request.COOKIES.get('jwt')
    if not token:
      return Response({
        'Message': 'Unauthenticated'
      }, status = status.HTTP_401_UNAUTHORIZED)
    try:
      payload = jwt.decode(token, 'secret', algorithms = ["HS256"])
    except jwt.ExpiredSignatureError:
      return Response({
        'Message': 'Expired Token'
      }, status = status.HTTP_410_GONE)
    user = CustomUser.objects.filter(id=payload['id']).first()
    if user is None:
      return Response({
        'Message': 'User not found'
      }, status = status.HTTP_404_NOT_FOUND)
    serializer = CustomUserSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status = status.HTTP_202_ACCEPTED)
  
  @swagger_auto_schema(
    operation_description="Delete your JWT token to successfully log-out from the Django Rest API",
    tags = ["User"],
    responses={
      status.HTTP_401_UNAUTHORIZED: openapi.Response(
        description = "User without JWT Token, so either it is expired or it wasn't created, either way it is needed to log-in again",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type=openapi.TYPE_STRING, description='Unauthenticated'),
          }
        )
      ),
      status.HTTP_410_GONE: openapi.Response(
        description = "JWT Token expired, log-in again to get a new one",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "Expired Token")
          }
        )
      ),
      status.HTTP_202_ACCEPTED: openapi.Response(
        description = "Token was deleted successfully",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, descritpion = 'Token deleted successfully')
          }
        )
      )
    }
  )
  def delete(self, request):
    token = request.COOKIES.get('jwt')
    if not token:
      return Response({
        'Message': 'Unauthorized'
      }, status = status.HTTP_401_UNAUTHORIZED)
    try:
      jwt.decode(token, 'secret', algorithms = ["HS256"])
    except jwt.ExpiredSignatureError:
      return Response({
        'Message': 'Expired Token'
      }, status = status.HTTP_410_GONE)
    response = Response()
    response.delete_cookie('jwt')
    response.data = {
      'Message': 'Token deleted successfully'
    }
    response.status_code = status.HTTP_202_ACCEPTED
    return response