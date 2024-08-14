from .serializer import EquipmentSerializer
import os
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import jwt
from .models import Equipment
from custom_auth.models import CustomUser
from rest_framework import status
import logging
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
import pandas as pd
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class EquipmentView(GenericAPIView):
  permission_classes = [AllowAny]
  serializer_class = EquipmentSerializer

  @swagger_auto_schema(
    operation_description="Register equipment data with either a single JSON payload or a CSV/Excel file",
    tags=['Sensor'],
    request_body=openapi.Schema(
      type=openapi.TYPE_OBJECT,
      properties={
        'equipmentId': openapi.Schema(type=openapi.TYPE_STRING, description='Equipment ID (only use with application/json Content-Type)'),
        'timestamp': openapi.Schema(type=openapi.TYPE_STRING, description='Timestamp(only use with application/json Content-Type)'),
        'value': openapi.Schema(type=openapi.TYPE_NUMBER, description='Value (only use with application/json Content-Type)'),
        'file': openapi.Schema(type=openapi.TYPE_FILE, description='CSV/Excel file with equipment data(only use with multipart/form-data Content-Type)')
      },
      required=['equipmentId', 'timestamp', 'value'],
    ),
    responses={
      status.HTTP_401_UNAUTHORIZED: openapi.Response(
        description = "Wrong authorization token provided in the header",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "Wrong authorization token")
          }
        )
      ),
      status.HTTP_401_UNAUTHORIZED: openapi.Response(
        description = "User not authenticated",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "Unauthenticated")
          }
        )
      ),
      status.HTTP_410_GONE: openapi.Response(
        description = "JWT Token provided in login is expired",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "Unauthenticated")
          }
        )
      ),
      status.HTTP_404_NOT_FOUND: openapi.Response(
        description = "User wasn't found with this JWT token provided",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "User not found")
          }
        ),
      ),
      status.HTTP_201_CREATED: openapi.Response(
        description = "Equipements were registered successfully inside database",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "Registered successfully")
          }
        )
      ),
      status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: openapi.Response(
        description = "Unsupported file type provided inside multiform data",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "Unsupported file type")
          }
        )
      ),
      status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
        description = "Some error not mapped occurred",
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = "Unknow error while uploading file")
          }
        )
      ),
      status.HTTP_406_NOT_ACCEPTABLE: openapi.Response(
        description = 'The content type provided in the header is not allowed',
        schema = openapi.Schema(
          type = openapi.TYPE_OBJECT,
          properties = {
            'Message': openapi.Schema(type = openapi.TYPE_STRING, description = 'Content type not allowed')
          }
        )
      )
    }
  )
  def post(self, request):
    if request.headers.get('Authorization') != os.getenv('AUTHORIZATION_TOKEN'):
      return Response({ 'Message': 'Wrong authorization token' }, status = status.HTTP_401_UNAUTHORIZED)
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
    user = CustomUser.objects.filter(id=payload['id'],is_active=True).first()
    if user is None:
      return Response({
        'Message': 'User not found'
      }, status = status.HTTP_404_NOT_FOUND)
    if request.headers.get('Content-Type') == 'application/json':
      data = {
        'equipmentId': request.data['equipmentId'],
        'timestamp': request.data['timestamp'],
        'value': request.data['value'],
        'user_id': user.id
      }
      serializer = self.serializer_class(data = data)
      serializer.is_valid(raise_exception = True)
      serializer.save()
      return Response({ 'Message': "Registered successfully" }, status = status.HTTP_201_CREATED)
    elif 'multipart/form-data' in request.headers.get('Content-Type'):
      file_obj = request.data['file']
      try:
        if file_obj.name.endswith('.csv'):
          df = pd.read_csv(file_obj)
          for index, row in df.iterrows():
            data = {
              'equipmentId': row['equipmentId'],
              'timestamp': row['timestamp'],
              'value': row['value'],
              'user_id': user.id
            }
            serializer = self.serializer_class(data = data)
            serializer.is_valid(raise_exception = True)
            serializer.save()
            logging.info(f"{row['equipmentId']} registered successfully")
          return Response({ 'Message': 'Registered successfully' },
                          status = status.HTTP_201_CREATED)
        elif file_obj.name.endswith(('.xls', '.xlsx')):
          df = pd.read_excel(file_obj)
          for index, row in df.iterrows():
            data = {
              'equipmentId': row['equipmentId'],
              'timestamp': row['timestamp'],
              'value': row['value'],
              'user_id': user.id
            }
            serializer = self.serializer_class(data = data)
            serializer.is_valid(raise_exception = True)
            serializer.save()
            logging.info(f"{row['equipmentId']} registered successfully")
          return Response({ 'Message': 'Registered successfully' },
                          status = status.HTTP_201_CREATED)
        else:
          return Response({ 'Message': 'Unsupported file type' },
                          status = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
      except Exception as error:
        logging.error(error, exc_info = True)
        return Response({ "Message": "Unknown error while uploading file"},
                        status = status.HTTP_500_INTERNAL_SERVER_ERROR )
    else:
      return Response({ 'Message': 'Content type not allowed' },
                      status = status.HTTP_406_NOT_ACCEPTABLE)
      