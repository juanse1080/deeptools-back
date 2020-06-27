from django.db import transaction
from rest_framework import generics
from rest_framework import authentication, permissions
from rest_framework import status
from rest_framework.response import Response
import docker as docker_env
from module.models import *
from module.serializers import *
import json
from django.utils.crypto import get_random_string


class checkBuild(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetrieveModuleSerializer

    def retrieve(self, request, *args, **kwargs):
        return Response(
            self.serializer_class(Docker.objects.get(
                image_name=self.kwargs['pk'])).data
        )


class listImages(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ImageSerializer

    def get_queryset(self):
        client = docker_env.from_env()
        # images = []
        # for image in client.images.list():
        #     for tag in image.tags:
        #         print(tag.split(':')[0])
        #         images.append(Image(image.id, tag))
        #         if Docker.objects.filter(image_name=tag.split(':')[0]).count() == 0:
        #             print("ENTRO", tag.split(':')[0])

        # return images

        return [Image(image.id, tag) for image in client.images.list() for tag in image.tags if Docker.objects.filter(image_name=tag.split(':')[0]).count() == 0]


class createModule(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateModuleSerializer

    def create(self, request, *args, **kwargs):

        # Cargando los datos
        data = dict(request.data)
        id = '__{}'.format(get_random_string(length=30))
        data['id'] = id
        data['image_name'] = ''.join(
            [i for i in id[2:].lower() if not i.isdigit()])
        data['proto'] = '{0}/protobuf.proto'.format(id)
        data['user'] = self.request.user.id

        # Serializando el objeto
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            docker = serializer.save()
            docker.create_docker()
            return Response(docker.image_name)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
