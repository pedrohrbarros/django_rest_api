from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.contrib.auth.password_validation import (
  MinimumLengthValidator,
  CommonPasswordValidator,
  NumericPasswordValidator,
  UserAttributeSimilarityValidator,
)

class CustomUserCreationForm(UserCreationForm):
  class Meta(UserCreationForm.Meta):
    model = CustomUser
    fields = '__all__'
      
  def clean_password(self):
    password = self.cleaned_data.get('password')
    validators = [
      MinimumLengthValidator(),
      CommonPasswordValidator(),
      NumericPasswordValidator(),
      UserAttributeSimilarityValidator(),
    ]
    for validator in validators:
      validator.validate(password)
    return password

class CustomUserChangeForm(UserChangeForm):
  class Meta(UserChangeForm.Meta):
    model = CustomUser
    fields = '__all__'

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Exclude the password field if it's not changed
    if not self.instance.pk:
      self.fields.pop('password')

  def clean_password(self):
    password = self.cleaned_data.get('password')
    validators = [
      MinimumLengthValidator(),
      CommonPasswordValidator(),
      NumericPasswordValidator(),
      UserAttributeSimilarityValidator(),
    ]
    for validator in validators:
      validator.validate(password)
    return password