from django.apps import AppConfig
from health_check.plugins import plugin_dir

class SensorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sensor'
    
    def ready(self):
        from .health import EquipmentHealthCheckBackend
        plugin_dir.register(EquipmentHealthCheckBackend)
