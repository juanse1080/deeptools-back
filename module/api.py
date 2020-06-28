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
import time


class checkBuild(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetrieveModuleSerializer

    def retrieve(self, request, *args, **kwargs):
        return Response(
            self.serializer_class(Docker.objects.get(
                image_name=self.kwargs['pk'])).data
        )


class stopContainer(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetrieveModuleSerializer

    def create(self, request, *args, **kwargs):
        time.sleep(5)
        return Response(
            self.serializer_class(Docker.objects.get(
                image_name=self.kwargs['pk'])).data
        )


class listImages(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ImageSerializer

    def get_queryset(self):
        client = docker_env.from_env()
        return [Image(image.id, tag) for image in client.images.list() for tag in image.tags if Docker.objects.filter(image_name=tag.split(':')[0]).count() == 0]


class listModule(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListModuleSerialize

    def get_queryset(self):
        dockers = Docker.objects.all()
        print(dockers)
        return dockers


class createModule(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateModuleSerializer

    def create(self, request, *args, **kwargs):

        # Cargando los datos
        data = dict(request.data)

        # verificando la existencia de los datos en el contanedor
        client = docker_env.from_env()
        # exist_workdir = client.containers.run(
        #     image=data["image"], command="test -d {0} && echo 'exist'".format(data["workdir"]), detach=True)
        # exist_file = client.containers.run(
        #     image=data["image"], command="test -d {0}/{1} && echo 'exist'".format(data["workdir"], data["file"]), detach=True)

        try:
            exist_workdir = client.containers.run(
                image=data["image"], command="test -d {0}".format(data["workdir"]))
        except docker_env.errors.ContainerError as error:
            return Response({"workdir": ["Path to workdir not found"]}, status=status.HTTP_409_CONFLICT)
        except docker_env.errors.ImageNotFound as error:
            return Response({"image": ["Image not found"]}, status=status.HTTP_409_CONFLICT)

        try:
            exist_file = client.containers.run(
                image=data["image"], command="ls -d {0}/{1}".format(data["workdir"], data["file"]))
        except docker_env.errors.ContainerError as error:
            return Response({"file": ["This file not exist in your workdir"]}, status=status.HTTP_409_CONFLICT)
        except docker_env.errors.ImageNotFound as error:
            return Response({"image": ["Image not found"]}, status=status.HTTP_409_CONFLICT)

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
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
