from .serializers import MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class LoginAPI(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer