from django.shortcuts import render
from sensor.models import Equipment

def home(request):
  items = Equipment.objects.all()
  return render(request, 'home.html', {'labels': [item.equipmentId for item in items], 'data': [item.value for item in items], 'timestamps': [str(item.timestamp) for item in items]})