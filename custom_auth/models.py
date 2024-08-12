from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import (
  CommonPasswordValidator,
  MinimumLengthValidator,
  NumericPasswordValidator,
  UserAttributeSimilarityValidator,
)

class CustomAccountManager(BaseUserManager):
  def create_superuser(self, email, name, password, **other_fields):
    other_fields.setdefault('is_superuser', True)
    other_fields.setdefault('is_active', True)
    other_fields.setdefault('is_staff', True)
      
    if other_fields.get('is_superuser') is not True:
      raise ValueError(
        'Superuser must be assigned to is_superuser=True.'
      )
    password_validators = [
      MinimumLengthValidator(),
      CommonPasswordValidator(),
      NumericPasswordValidator(),
      UserAttributeSimilarityValidator()
    ]
    password_validation_errors = []
    for validator in password_validators:
      try :
        validator.validate(password)
      except Exception as e:
        password_validation_errors.extend(e.messages)
    
    if password_validation_errors:
      raise ValueError('\n'.join(password_validation_errors))

    return self.create_user(email, name, password, **other_fields)

  def create_user(self, email, name, password, **other_fields):
    password_validators = [
      MinimumLengthValidator(),
      CommonPasswordValidator(),
      NumericPasswordValidator(),
      UserAttributeSimilarityValidator()
    ]
    password_validation_errors = []
    for validator in password_validators:
      try :
        validator.validate(password)
      except Exception as e:
        password_validation_errors.extend(e.messages)
    
    if password_validation_errors:
      raise ValueError('\n'.join(password_validation_errors))
    email = self.normalize_email(email)
    user = self.model(email=email, name=name, **other_fields)
    user.set_password(password)
    user.save()
    return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
  id = models.AutoField(primary_key = True)
  email = models.EmailField(verbose_name='E-mail Address', unique=True, null = False, blank = False)
  password = models.CharField(verbose_name = 'Password', max_length = 255, blank = False, null = False)
  name = models.CharField(verbose_name = 'Complete Name', max_length=150, blank = False, null = False)
  start_date = models.DateTimeField(verbose_name = "Start Date", default=timezone.now)
  is_active = models.BooleanField(verbose_name="Is Active?", default=True)
  is_staff = models.BooleanField(verbose_name = "Is Staff?",default = False)
  
  objects = CustomAccountManager()
  
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['name', 'password']

  def __str__(self):
    return self.name