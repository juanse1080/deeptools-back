from django.db import transaction
from django.utils.crypto import get_random_string
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import generics, mixins, authentication, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

import docker as docker_env

from module.models import *
from module.serializers import *
from module.utils import handle_uploaded_file

import os
import json
import time
import string
import random


class CheckPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.method == "POST":
            return False
        print(request)
        return request.user.has_perms(request.data["permissions"])


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def checkPermissionsAPI(request):
    if request.user.has_perms(request.data["permissions"]):
        return Response(True)
    else:
        return Response("Permission denied",
                        status=status.HTTP_403_FORBIDDEN)


class retrieveModule(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetrieveModuleSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            return Response(
                self.serializer_class(Docker.objects.get(
                    image_name=self.kwargs['pk'])).data
            )
        except ObjectDoesNotExist:
            return Response("Module not found",
                            status=status.HTTP_404_NOT_FOUND)


class deleteContainer(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetrieveModuleSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            docker = Docker.objects.get(image_name=self.kwargs['pk'], state__in=[
                                        'active', 'stopped', 'building'])
            docker.delete_module()
            return Response(
                self.serializer_class(docker).data
            )
        except ObjectDoesNotExist:
            return Response("Module not found",
                            status=status.HTTP_404_NOT_FOUND)


class stopContainer(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetrieveModuleSerializer

    def update(self, request, *args, **kwargs):
        try:
            docker = Docker.objects.get(
                image_name=self.kwargs['pk'], state='active')
            docker.stop_container()
            return Response(
                self.serializer_class(docker).data
            )
        except ObjectDoesNotExist:
            return Response("Module not found",
                            status=status.HTTP_404_NOT_FOUND)


class startContainer(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetrieveModuleSerializer

    def update(self, request, *args, **kwargs):
        try:
            docker = Docker.objects.get(
                image_name=self.kwargs['pk'], state='stopped')
            docker.run_container()
            return Response(
                self.serializer_class(docker).data
            )
        except ObjectDoesNotExist:
            return Response("Module not found",
                            status=status.HTTP_404_NOT_FOUND)


class listImages(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ImageSerializer

    def get_queryset(self):
        client = docker_env.from_env()
        return [Image(image.id, tag) for image in client.images.list() for tag in image.tags if Docker.objects.filter(image_name=tag.split(':')[0]).count() == 0]


class listModule(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListModuleSerializer

    def list(self, request, *args, **kwargs):
        role = self.request.user.role

        if role == 'admin':
            others = Docker.objects.filter(
                state__in=['building', 'stopped'])

            actives = Docker.objects.filter(
                state='active')

            for active in actives:
                if not active.check_active_state():
                    active.state = 'stopped'
                    active.save()

        elif role == 'developer':
            others = Docker.objects.filter(
                state__in=['building', 'stopped'], user=self.request.user)

            actives = Docker.objects.filter(
                state='active', user=self.request.user)

            for active in actives:
                if not active.check_active_state():
                    active.state = 'stopped'
                    active.save()

        else:
            others = Docker.objects.filter(state='active')
            return Response(self.serializer_class(others.order_by('timestamp'), many=True).data)

        return Response(self.serializer_class(actives.union(others).order_by('timestamp'), many=True).data)


class createExperiment(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetrieveModuleSerializer

    def create(self, request, *args, **kwargs):
        try:
            docker = Docker.objects.get(
                image_name=self.kwargs['pk'], state='active')

            input = docker.elements_type.filter(kind='input').get()
            output = docker.elements_type.filter(kind='output')

            if output.count() == 0:
                output = False
            else:
                output = True

            if int(input.len) > 0:
                experiment, created = Experiment.objects.get_or_create(
                    docker=docker, user=self.request.user, state='created')
                if created:
                    experiment.create_workdir(outputs=output)
                experiments = [experiment]
            else:
                experiments = Experiment.objects.filter(
                    docker=docker, user=self.request.user, state='created')
                if experiments.count() == 0:
                    experiment = Experiment.objects.create(
                        docker=docker, user=self.request.user, state='created')
                    experiment.create_workdir(outputs=output)
                    experiments = [experiment]

            element_data = []
            for exp in experiments:
                for data in exp.elements.all():
                    element_data.append(data)

            data = dict(**self.serializer_class(docker).data)
            data["elements"] = RetrieveElementDataSerializer(
                element_data, many=True).data
            return Response(data)
        except ObjectDoesNotExist:
            return Response("Module not found",
                            status=status.HTTP_404_NOT_FOUND)


class createElementData(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetrieveElementDataSerializer

    def create(self, request, *args, **kwargs):
        try:
            docker = Docker.objects.get(
                image_name=self.kwargs['pk'], state='active')

            input = docker.elements_type.filter(kind='input').get()
            output = docker.elements_type.filter(kind='output')

            if output.count() == 0:
                output = False
            else:
                output = True

            experiment = None

            if int(input.len) > 0:
                experiment, created = Experiment.objects.get_or_create(
                    docker=docker, user=self.request.user, state='created')
                if created:
                    experiment.create_workdir(outputs=output)
            else:
                experiments = Experiment.objects.filter(
                    docker=docker, user=self.request.user, state='created')

                if experiments.count() > 0:
                    for exp in experiments:
                        if exp.elements.all().count() == 0:
                            experiment = exp

                    if not experiment:
                        experiment = Experiment.objects.create(
                            docker=docker, user=self.request.user, state='created')
                        experiment.create_workdir(outputs=output)

                else:
                    experiment, created = Experiment.objects.create(
                        docker=docker, user=self.request.user, state='created')
                    if created:
                        experiment.create_workdir(outputs=output)

            file = request.FILES['file']

            element = ElementData.objects.create(
                experiment=experiment, kind='input', element=Element.objects.get(name='input'), name=file.name)

            element.value = handle_uploaded_file(
                file, experiment.inputs(), 'input_{}'.format(element.id))

            element.save()
            return Response(self.serializer_class(element).data)
        except ObjectDoesNotExist:
            return Response("Module not found",
                            status=status.HTTP_404_NOT_FOUND)


class DeleteElementData(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetrieveElementDataSerializer

    def delete(self, request, *args, **kwargs):
        input = ElementData.objects.get(id=self.kwargs['pk'])
        input.delete()

        experiment = input.experiment
        experiments = experiment.docker.experiments.filter(
            user=self.request.user, state='created')
        if experiments.count() > 1:
            experiment.delete()
        return Response(True)


class checkCreateModule(generics.CreateAPIView):
    permission_classes = [permissions.DjangoModelPermissions]
    serializer_class = CreateModuleSerializer

    def create(self, request, *args, **kwargs):
        return Response(True)


class createModule(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateModuleSerializer

    def create(self, request, *args, **kwargs):
        # verificando permisos
        if not self.request.user.has_perm('module.add_docker'):
            return Response("Permission denied", status=status.HTTP_403_FORBIDDEN)

        # Cargando los datos
        data = dict(request.data)

        # verificando la existencia de los datos en el contanedor
        client = docker_env.from_env()
        try:
            exist_workdir = client.containers.run(
                image=data["image"], command="test -d {0}".format(data["workdir"]))
        except docker_env.errors.ContainerError as error:
            return Response({"workdir": ["Path to workdir not found in image {}".format(data["image"])]}, status=status.HTTP_409_CONFLICT)
        except docker_env.errors.ImageNotFound as error:
            return Response({"image": ["Image not found"]}, status=status.HTTP_409_CONFLICT)

        try:
            exist_file = client.containers.run(
                image=data["image"], command="ls -d {0}/{1}".format(data["workdir"], data["file"]))
        except docker_env.errors.ContainerError as error:
            return Response({"file": ["This file not exist in your {0}".format(data["workdir"])]}, status=status.HTTP_409_CONFLICT)
        except docker_env.errors.ImageNotFound as error:
            return Response({"image": ["Image not found"]}, status=status.HTTP_409_CONFLICT)

        try:
            exist_classname = client.containers.run(
                image=data["image"], command="grep 'class {0}' {1}/{2}".format(data["classname"], data["workdir"], data["file"]))
        except docker_env.errors.ContainerError as error:
            return Response({"classname": ["Class not exist in {0}/{1}".format(data["workdir"], data["file"])]}, status=status.HTTP_409_CONFLICT)
        except docker_env.errors.ImageNotFound as error:
            return Response({"image": ["Image not found"]}, status=status.HTTP_409_CONFLICT)

        id = ''.join([random.choice(string.ascii_letters)
                      for i in range(32)])
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
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)


class executeContainer(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateModuleSerializer

    def retrieve(self, request, *args, **kwargs):
        docker = Docker.objects.get(
            image_name=self.kwargs['pk'], state='active')

        experiments = Experiment.objects.filter(
            docker=docker, user=self.request.user, state='created')

        print(experiments)

        for experiment in experiments:
            experiment.run()

        return Response(True)


class listExperiments(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateExperimentSerializer

    def get_queryset(self):
        return Experiment.objects.filter(state='executing')


class retriveExperiment(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateExperimentSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            experiment = Experiment.objects.get(
                id=self.kwargs['pk'])
            return Response(
                self.serializer_class(experiment).data
            )
        except ObjectDoesNotExist:
            return Response("Module not found",
                            status=status.HTTP_404_NOT_FOUND)
