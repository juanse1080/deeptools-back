from django.utils.crypto import get_random_string
from django.db import transaction
from rest_framework import generics
from rest_framework import authentication, permissions
from rest_framework.response import Response
import docker as docker_env
from module.models import *
from module.serializers import *

class listImages(generics.ListAPIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = ImageSerializer

  def get_queryset(self):
    client = docker_env.from_env()
    return [Image(image.id, tag) for image in client.images.list() for tag in image.tags]

class createModule(generics.CreateAPIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = ModuleSerializer

  def create(self, request, *args, **kwargs):
    
    # Cargando los datos
    pk = get_random_string(length=32)
    data = request.data
    data['language'] = 'python'
    data['base_path'] = '{0}{1}'.format(settings.MEDIA_URL, pk)
    data['id'] = pk
    data['user'] = self.request.user.id
    print(data['base_path'])

    # Serializando el objeto
    serializer = self.serializer_class(data=data)
    if serializer.is_valid():
      docker = serializer.save()
      with transaction.atomic():
        docker.create_docker(data['proto'])
        docker.save()
        elements = ['examples', 'graph', 'input', 'output', 'response']

        for key in data:
          if key in elements:
            ElementType.objects.create(
              kind=key,
              docker=docker,
              element=Element.objects.get(name=key),
            )
      return Response(True)
    print(serializer.errors)
    return serializer.errors




