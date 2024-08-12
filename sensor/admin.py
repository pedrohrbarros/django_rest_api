from django.contrib import admin
from .models import Equipment

class EquipmentAdmin(admin.ModelAdmin):
  list_display = ('equipmentId', 'timestamp', 'value')
  readonly_fields = ['timestamp']

admin.site.register(Equipment, EquipmentAdmin)