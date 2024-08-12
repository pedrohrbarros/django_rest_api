from rest_framework import serializers
from .models import Equipment

class EquipmentSerializer(serializers.ModelSerializer):
  class Meta:
    model = Equipment
    fields = ('equipmentId', 'timestamp', 'value', 'user_id')