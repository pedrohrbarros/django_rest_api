from django.apps import AppConfig
from health_check.plugins import plugin_dir

class CustomAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_auth'

    def ready(self):
        from .health import UserHealthCheckBackend
        plugin_dir.register(UserHealthCheckBackend)