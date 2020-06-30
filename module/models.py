from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from authenticate.models import User
from .utils import *
from .generate.proto import ProtoFile
from .generate.server import ServerFile
from .managers import UserManager
import shutil
import os
import json

import traceback
import sys

import docker as docker_env
from channels.layers import get_channel_layer


class Image:
    def __init__(self, id, image):
        self.id = id
        self.name = image
        self.label = image.split(':')[0]


class Docker(models.Model):
    lenguaje_choices = (
        ('python', 'Python'),
    )

    state_choices = (
        ('stopped', 'Stopped'),
        ('deleted', 'Deleted'),
        ('building', 'Building'),
        ('active', 'Active'),
    )

    id = models.CharField(max_length=32, primary_key=True)
    image_name = models.CharField(max_length=32, unique=True)

    state = models.CharField(
        max_length=10, choices=state_choices, default='building')
    ip = models.CharField(max_length=30, null=True)
    proto = models.CharField(max_length=500, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        User, null=True, on_delete=models.CASCADE, related_name='owner')
    language = models.CharField(
        max_length=100, choices=lenguaje_choices, default='python')

    protocol = models.TextField()

    name = models.CharField(max_length=100, unique=True)
    image = models.CharField(max_length=100, null=True)
    workdir = models.CharField(max_length=500, null=True)
    file = models.CharField(max_length=100, null=True)
    classname = models.CharField(max_length=100, null=True)

    def get_container(self):
        client = docker_env.from_env()
        return client.containers.get(self.image_name)

    def get_path(self):
        return '{0}/{1}'.format(settings.MEDIA_ROOT, self.id)

    def create_folders(self):
        os.makedirs('{0}/experiments'.format(self.get_path()), 0o777)

    def dockerfile(self):
        """
            proto:
                {0}: ubicación absoluta del archivo (media_root)
                {1}: archivo proto (proto)
                {2}: ubicación del contenedor (path)
            image:
                {0}: nombre de la imagen creada (image)
            compile:
                {0}: ubicación del contenedor (path)
                {1}: carpeta contenedora de los archivos de comunicación (id)
                {2}: ruta relativa del archivo proto (proto)
        """
        commands = {
            'image': 'FROM {0}'.format(self.image),
            'server': 'COPY ./server.py {0}'.format(self.workdir),
            'proto': 'COPY ./protobuf.proto {0}'.format(self.workdir),

            'mkdir': 'RUN mkdir {0}/{1}'.format(self.workdir, self.id),
            'requirements': 'RUN pip install grpcio grpcio-tools',
            'compile': 'RUN python -m grpc_tools.protoc --proto_path={0} --python_out={0}/{1} --grpc_python_out={0}/{1} protobuf.proto'.format(self.workdir, self.id),
            'init': 'RUN touch {0}/{1}/__init__.py'.format(self.workdir, self.id)
        }

        dockerfile = '{0}/Dockerfile'.format(self.get_path())

        with open(dockerfile, '+w') as file:
            for command in commands.values():
                file.write('{0}\n'.format(command))

    def protobuf(self):
        protobuf = '{0}/{1}'.format(settings.MEDIA_ROOT, self.proto)

        with open(protobuf, '+w') as file_:
            proto = ProtoFile(items=[{
                'kind': element.kind,
                'len': element.len
            } for element in self.elements_type.all()])

            file_.write(proto.create_protobuf())

    def server(self):
        server = '{0}/{1}/server.py'.format(settings.MEDIA_ROOT, self.id)

        with open(server, '+w') as file_:
            aux = ServerFile(items=[{
                'kind': element.kind,
                'len': element.len
            } for element in self.elements_type.all()])

            file_.write(aux.create_server(self.id, ''.join(self.file.split(
                '.')[:-1]), self.workdir, self.classname))

    def create_docker(self):

        try:
            # Creando el WORKDIR
            self.create_folders()

            # Generando los archivos de comunicación
            self.protobuf()
            self.dockerfile()
            self.server()

            # Compilando el archivo de comunicación
            terminal_out(
                "python -m grpc_tools.protoc --proto_path=%(media)s --python_out=%(media)s/%(id)s --grpc_python_out=%(media)s/%(id)s %(id)s/%(proto)s" % {
                    'media': settings.MEDIA_ROOT,
                    'id': self.id,
                    'proto':  'protobuf.proto'.format(self.id)
                })

            shutil.move('%(media)s/%(id)s/%(id)s' % {
                'media': settings.MEDIA_ROOT, 'id': self.id
            },
                settings.ENV_ROOT
            )

            # self.run_model()
            # container = self.get_container()
            # self.ip = '%s:50051' % container.attrs['NetworkSettings']['IPAddress']
        except:
            exc_type, exc_obj, tb = sys.exc_info()
            print(exc_type)
            print(exc_obj)
            traceback.print_exc()
            self.__delete_model()
        self.save()
        return True

    def build_docker(self):
        try:
            client = docker_env.APIClient(
                base_url='unix://var/run/docker.sock')
            steps = [
                [
                    "Step 1/7:",
                    "Loading image {0} ...".format(self.image),
                    "Loaded image {0}".format(self.image)
                ], [
                    "Step 2/7:",
                    "Creating service files ...",
                    "Created service files"
                ], [
                    "Step 3/7:",
                    "Creating comunication files ...",
                    "Created comunication files"
                ], [
                    "Step 4/7:",
                    "Moving comunication and service files to workdir('{0}') ...".format(
                        self.workdir),
                    "Moved comunication and service files to workdir('{0}')".format(
                        self.workdir)
                ], [
                    "Step 5/7:",
                    "Instaling dependencies of comunication ...",
                    "Instaled dependencies of comunication"
                ], [
                    "Step 6/7:",
                    "Compiling comunication files ...",
                    "Compiled comunication files"
                ], [
                    "Step 7/7:",
                    "Cleaning records ...",
                    "Cleaned records"
                ]
            ]

            return (
                client.build(path=self.get_path(), rm=True,
                             tag='{0}:latest'.format(self.image_name)),
                steps
            )
        except expression as identifier:
            self.__delete_model()
            return [{'stream': "error"}, {'stream': "error"}], [["Error:", "An error occurred during model shrinkage. Check the data and try again"]]

    def run_model(self):
        try:
            client = docker_env.from_env()
            client.containers.run(
                image=self.image_name,
                command='python server.py',
                detach=True,
                name=self.image_name,
                # ports={50051: 50051},
                remove=True,
                working_dir=self.workdir,
                volumes={
                    '{}/experiments'.format(self.get_path()): {
                        'bind': '{}/media'.format(self.workdir), 'mode': 'rw'
                    }
                }
            )
            container = self.get_container()
            self.ip = '%s:50051' % container.attrs['NetworkSettings']['IPAddress']
            self.state = 'active'
            self.save()
        except docker_env.errors.ContainerError as error:
            print(error)
            return error
        except docker_env.errors.APIError as error:
            print(error)
            return error

    def stop_model(self):
        self.get_container().stop()
        self.state = 'stopped'
        self.ip = ''
        self.save()

    def delete_module(self):
        if self.state == 'active':
            self.get_container().stop()

        client = docker_env.from_env()
        client.images.remove(image=self.image_name, force=True)
        self.state = 'deleted'
        self.save()

    def __delete_model(self, delete_img=False):
        shutil.rmtree(self.get_path())
        shutil.rmtree('{0}{1}'.format(
            settings.ENV_ROOT, self.id
        ))
        self.delete()


class ElementType(models.Model):
    kind = models.CharField(max_length=30)
    docker = models.ForeignKey(Docker, null=False, blank=False,
                               on_delete=models.CASCADE, related_name='elements_type')
    element = models.ForeignKey(
        'Element', null=False, blank=False, on_delete=models.CASCADE, related_name='types')
    len = models.CharField(max_length=1, default=0)
    value = models.TextField()

    def __str__(self):
        return self.kind


class Element(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Experiment(models.Model):
    state = models.CharField(max_length=10, default='created')
    user = models.ForeignKey(User, null=True, blank=False,
                             on_delete=models.CASCADE, related_name='experiments')
    docker = models.ForeignKey(Docker, null=True, blank=False,
                               on_delete=models.CASCADE, related_name='experiments')
    timestamp = models.DateTimeField(auto_now=True)

    def create_workdir(self):
        os.makedirs('{0}/experiments/user_{1}/exp_{2}'.format(
            self.docker.get_path(), self.user.id, self.id), 0o777)


class ElementData(models.Model):
    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name='elements')
    kind = models.CharField(max_length=30)
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    value = models.TextField()
