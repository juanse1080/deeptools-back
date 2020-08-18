from django.core.exceptions import ObjectDoesNotExist

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

import docker as docker_env

from module.models import *
from module.serializers import *

import string
import random
import json


@api_view(['POST'])  # NOTE Check permissions
@permission_classes([permissions.IsAuthenticated])
def checkPermissionsAPI(request):
    if request.user.has_perms(request.data["permissions"]):
        return Response(True)
    else:
        return Response("Permission denied", status=status.HTTP_401_UNAUTHORIZED)


class createModule(generics.CreateAPIView):  # NOTE Create module
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateModuleSerializer

    def create(self, request, *args, **kwargs):
        # verificando permisos
        if not self.request.user.has_perm('module.add_docker'):
            return Response("Permission denied", status=status.HTTP_401_UNAUTHORIZED)

        data = {}
        for key, value in request.data.items():
            data[key] = value

        data["elements"] = json.loads(data["elements"])

        client = docker_env.from_env()
        try:
            exist_workdir = client.containers.run(
                remove=True, image=data["image"], command="test -d {0}".format(data["workdir"]))
        except docker_env.errors.ContainerError as error:
            return Response({
                "workdir": ["Path to workdir not found in image {}".format(data["image"])]}, status=status.HTTP_409_CONFLICT)
        except docker_env.errors.ImageNotFound as error:
            return Response({"image": ["Image not found"]}, status=status.HTTP_409_CONFLICT)

        try:
            exist_file = client.containers.run(
                remove=True, image=data["image"], command="ls -d {0}/{1}".format(data["workdir"], data["file"]))
        except docker_env.errors.ContainerError as error:
            return Response({
                "file": ["This file not exist in your {0}".format(data["workdir"])]}, status=status.HTTP_409_CONFLICT)
        except docker_env.errors.ImageNotFound as error:
            return Response({"image": ["Image not found"]}, status=status.HTTP_409_CONFLICT)

        try:
            exist_classname = client.containers.run(
                remove=True, image=data["image"], command="grep 'class {0}' {1}/{2}".format(data["classname"], data["workdir"], data["file"]))
        except docker_env.errors.ContainerError as error:
            return Response({"classname": ["Class not exist in {0}/{1}".format(data["workdir"], data["file"])]}, status=status.HTTP_409_CONFLICT)
        except docker_env.errors.ImageNotFound as error:
            return Response({"image": ["Image not found"]}, status=status.HTTP_409_CONFLICT)

        try:
            exist_classname = client.containers.run(
                remove=True, image=data["image"], working_dir=data["workdir"], command="python {0}".format(data["file"]))
        except docker_env.errors.ContainerError as error:
            return Response({"classname": ["{0} class has trouble running, verify document can run".format(data["classname"])]}, status=status.HTTP_409_CONFLICT)
        except docker_env.errors.ImageNotFound as error:
            return Response({"image": ["Image not found"]}, status=status.HTTP_409_CONFLICT)

        id = ''.join([random.choice(string.ascii_letters) for i in range(32)])
        data['id'] = id
        data['image_name'] = id.lower()
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


class listModule(generics.ListAPIView):  # NOTE List module
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListModuleSerializer

    def list(self, request, *args, **kwargs):
        if self.request.user.role == 'admin':
            others = Docker.objects.filter(
                state__in=['building', 'stopped', 'builded'])

            actives = Docker.objects.filter(state='active')

            for active in actives:
                if not active.check_active_state():
                    active.state = 'stopped'
                    active.save()

            dockers = actives.union(others).order_by('created_at')

        elif self.request.user.role == 'developer':
            others = Docker.objects.filter(
                state__in=['building', 'stopped', 'builded'],
                user=self.request.user)

            actives = Docker.objects.filter(state='active',
                                            user=self.request.user)

            for active in actives:
                if not active.check_active_state():
                    active.state = 'stopped'
                    active.save()

            dockers = actives.union(others).order_by('created_at')

        elif self.request.user.role == 'user':
            dockers = Docker.objects.filter(
                state='active').order_by('created_at')

        else:
            return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

        return Response(self.serializer_class(dockers, many=True).data)


class retrieveModule(generics.RetrieveAPIView):  # NOTE Show module
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetrieveModuleSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            if self.request.user.role == 'developer':
                docker = Docker.objects.get(image_name=self.kwargs['pk'])
                if not docker.user.id == self.request.user.id:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

            elif self.request.user.role == 'user':
                docker = Docker.objects.get(image_name=self.kwargs['pk'])

            elif self.request.user.role == 'admin':
                docker = Docker.objects.get(image_name=self.kwargs['pk'])

            else:
                return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

            docker.background = f"{docker.get_public_path()}/{docker.background}"
            data = self.serializer_class(docker).data
            exps = []
            for exp in docker.experiments.filter(elements__example=True, user=docker.user, state='executed').distinct():
                exp.state = exp.elements.filter(
                    kind='input')[0].get_public_path()
                exps.append(exp)
            data["experiments"] = RetriveExperiment(exps, many=True).data
            if self.request.user.id == docker.user.id:
                data["users"] = UserSerializer(
                    docker.subscribers.all(), many=True).data
            return Response(data)
        except ObjectDoesNotExist:
            return Response("Module not found", status=status.HTTP_404_NOT_FOUND)


class deleteContainer(generics.DestroyAPIView):  # NOTE Delete module
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        try:
            if self.request.user.role == 'developer':
                docker = Docker.objects.get(image_name=self.kwargs['pk'],
                                            state__in=['active', 'stopped', 'building', 'builded'])
                if not docker.user.id == self.request.user.id:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

            elif self.request.user.role == 'user':
                return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

            elif self.request.user.role == 'admin':
                docker = Docker.objects.get(image_name=self.kwargs['pk'],
                                            state__in=['active', 'stopped', 'building', 'builded'])

            else:
                return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

            docker.delete_module()
            return Response(True)
        except ObjectDoesNotExist:
            return Response("Module not found", status=status.HTTP_404_NOT_FOUND)


class subscribeContainer(generics.UpdateAPIView):  # NOTE subscribe container
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        try:
            if self.request.user.role == 'user':
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'])

            elif self.request.user.role == 'developer':
                return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

            elif self.request.user.role == 'admin':
                return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

            else:
                return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

            if not docker.check_if_exist(self.request.user):
                docker.subscribers.add(self.request.user)
                docker.save()
                return Response('add')
            else:
                docker.subscribers.remove(self.request.user)
                docker.save()
                return Response('remove')

        except ObjectDoesNotExist:
            return Response("Module not found",
                            status=status.HTTP_404_NOT_FOUND)


class stopContainer(generics.UpdateAPIView):  # NOTE Stop container
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        try:
            if self.request.user.role == 'developer':
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'], state='active')
                if not docker.user.id == self.request.user.id:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

            elif self.request.user.role == 'user':
                return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

            elif self.request.user.role == 'admin':
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'], state='active')

            else:
                return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

            docker.stop_container()
            return Response(True)
        except ObjectDoesNotExist:
            return Response("Module not found",
                            status=status.HTTP_404_NOT_FOUND)


class startContainer(generics.UpdateAPIView):  # NOTE Start container
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        try:
            if self.request.user.role == 'developer':
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'], state='stopped')
                if not docker.user.id == self.request.user.id:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

            elif self.request.user.role == 'user':
                return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

            elif self.request.user.role == 'admin':
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'], state='stopped')

            else:
                return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

            docker.run_container()
            return Response(True)
        except ObjectDoesNotExist:
            return Response("Module not found",
                            status=status.HTTP_404_NOT_FOUND)


class listImages(generics.ListAPIView):  # NOTE List images
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ImageSerializer

    def get_queryset(self):
        if not self.request.user.role in ['developer', 'admin']:
            return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

        client = docker_env.from_env()
        return [
            Image(image.id, tag) for image in client.images.list()
            for tag in image.tags
            if Docker.objects.filter(image_name=tag.split(':')[0]).count() == 0
        ]
