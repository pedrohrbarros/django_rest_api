from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
  add_form = CustomUserCreationForm
  form = CustomUserChangeForm
  readonly_fields = ['start_date', 'last_login']
  list_display = ('email', 'name', 'is_active')
  fieldsets = (
    ('Authentication', {'fields': ('email', 'password')}),
    ('Personal Information', {'fields': ('name',)}),
    ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    ('Important dates', {'fields': ('last_login',)}),
  )
  add_fieldsets = (
    (None, {
      'classes': ('wide',),
      'fields': ('email', 'password', 'password_confirmation'),
    }),
  )
  list_filter = ('is_superuser', 'is_active')
  search_fields = ('email',)
  ordering = ('email',)

  def get_form(self, request, obj=None, **kwargs):
    form = super().get_form(request, obj, **kwargs)
    if obj is None:  # If adding a new user
      form.base_fields['password'].required = True
      form.base_fields['password_confirmation'].required = True
    return form

admin.site.register(CustomUser, CustomUserAdmin)