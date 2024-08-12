from django.urls import path
from .views import CustomUserView, LoginUserView

urlpatterns = [
  path('user/', CustomUserView.as_view(), name = 'user'),
  path('user/login/', LoginUserView.as_view(), name = 'login_user'),
]