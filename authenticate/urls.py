from django.urls import path
# Import other modules
from rest_framework_simplejwt.views import TokenRefreshView
# Import local 
from .api import LoginAPI

urlpatterns = [
    path('login/', LoginAPI.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]