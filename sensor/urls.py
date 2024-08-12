from django.urls import path
from .views import EquipmentView

urlpatterns = [
  path('equipment/', EquipmentView.as_view(), name = 'equipment')
]