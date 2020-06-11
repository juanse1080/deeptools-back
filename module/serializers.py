from rest_framework import serializers
from .models import *

class ImageSerializer(serializers.Serializer):
  id = serializers.CharField(max_length=500)
  label = serializers.CharField(max_length=200)
  name = serializers.CharField(max_length=200)

class ModuleSerializer(serializers.ModelSerializer):
  proto = serializers.FileField(use_url=True)
  class Meta:
    model = Docker
    fields = '__all__'