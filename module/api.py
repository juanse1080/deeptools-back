from django.db import transaction
from rest_framework import generics
from rest_framework import authentication, permissions
from rest_framework import status
from rest_framework.response import Response
import docker as docker_env
from module.models import *
from module.serializers import *
import json


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
        data = dict(request.data)
        data['user'] = self.request.user.id

        # Serializando el objeto
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            docker = serializer.save()
            docker.create_docker()
            return Response(True)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
