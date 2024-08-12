from django.db import models
from django.utils import timezone
from custom_auth.models import CustomUser

class Equipment(models.Model):
  id = models.AutoField(primary_key = True)
  equipmentId = models.CharField(verbose_name = "Equipment ID", null = False, blank = False, max_length = 255)
  timestamp = models.DateTimeField(verbose_name = "Timestamp", default = timezone.now, blank = False, null = False)
  value = models.FloatField(verbose_name = "Value", blank = False, null = False)
  user = models.ForeignKey(CustomUser, verbose_name="User", blank = True, null = True, on_delete = models.SET_NULL)
  
  def __str__(self):
    return f'Equipment - {self.equipmentId}'