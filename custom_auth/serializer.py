from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = CustomUser
    fields = ('name', 'email', 'password')
    extra_kwargs = {
      'password': {
        'write_only': True 
      }
    }
  def create(self, validated_data):
    password = validated_data.pop('password')
    user = CustomUser(**validated_data)
    user.set_password(password)
    user.save()
    return user