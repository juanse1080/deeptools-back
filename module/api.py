from rest_framework import generics
from rest_framework import authentication, permissions
from rest_framework.response import Response
import docker as docker_env
from module.models import *
from module.serializers import *


class listImages(generics.ListAPIView):
  authentication_classes = [authentication.TokenAuthentication]
  serializer_class = ImageSerializer

  def get_queryset(self):
    client = docker_env.from_env()
    return [Image(image.id, tag) for image in client.images.list() for tag in image.tags]