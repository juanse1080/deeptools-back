from rest_framework import serializers

class ImageSerializer(serializers.Serializer):
  id = serializers.CharField(max_length=500)
  label = serializers.CharField(max_length=200)
  name = serializers.CharField(max_length=200)
