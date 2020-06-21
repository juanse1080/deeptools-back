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
import sys

from django.utils.crypto import get_random_string

import docker as docker_env


class Image:
    def __init__(self, id, image):
        self.id = id
        self.name = image
        self.label = image.split(':')[0]


class Docker(models.Model):
    lenguaje_choices = (
        ('python', 'Python'),
    )

    id = models.CharField(max_length=32, primary_key=True)
    state = models.BooleanField(default=True)
    ip = models.CharField(max_length=30, unique=True, null=True)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = '__{}'.format(get_random_string(length=30))
        self.proto = '{0}/protobuf.proto'.format(self.id)

    def get_container(self):
        client = docker_env.from_env()
        return client.containers.get(self.id)

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
            'server': 'COPY {0}/{1}/server.py {2}'.format(settings.MEDIA_ROOT, self.id, self.workdir),
            'proto': 'COPY {0}/{1} {2}'.format(settings.MEDIA_ROOT, self.proto, self.workdir),
            'requirements': 'RUN pip install grpcio grpcio-tools',
            'compile': 'RUN python -m grpc_tools.protoc --proto_path={0} --python_out={0}/{1} --grpc_python_out={0}/{1} protobuf.proto && touch {0}/{1}/__init__.py'.format(self.workdir, self.id)
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

            file_.write(aux.create_server(self.id, self.file, self.classname))

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
            print("####### entro")
            self.build_image()
            print("####### salio")

            self.run_model()
            container = self.get_container()
            self.ip = '%s:50051' % container.attrs['NetworkSettings']['IPAddress']
        except:
            exc_type, exc_obj, tb = sys.exc_info()
            print(exc_type)
            print(exc_obj)
            traceback.print_exc()
            # self.delete_model()
            return False
        self.save()
        return True

    def build_image(self):
        try:
            client = docker_env.from_env()
            client.images.build(path=self.get_path(), tag=self.id)
        except:
            print("####### ERROR ", identifier)

    def run_model(self):
        client = docker_env.from_env()
        client.containers.run(
            image=self.image,
            command='python server.py',
            detach=True,
            name=self.id,
            ports={50051: 50051},
            remove=True,
            volumes={
                '%s/experiments' % self.get_path(): {
                    'bind': '/media', 'mode': 'rw'
                }
            }
        )

    def stop_model(self):
        self.state = not self.state
        self.get_container().stop()

    def delete_model(self, delete_img=False):
        shutil.rmtree(self.get_path())
        shutil.rmtree('{0}{1}'.format(
            settings.ENV_ROOT, self.id
        ))
        self.stop_model()
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
    user = models.ForeignKey(User, null=True, blank=False,
                             on_delete=models.CASCADE, related_name='experiments')
    docker = models.ForeignKey(Docker, null=True, blank=False,
                               on_delete=models.CASCADE, related_name='experiments')
    input_file = models.CharField(max_length=500, null=True)
    output_file = models.CharField(max_length=500, null=True)
    response = models.CharField(max_length=1000, null=True)
    timestamp = models.DateTimeField(auto_now=True)


class GraphType(models.Model):
    kind_choices = (
        ('bar', 'Bar graphic'),
        ('donut', 'Donut chart'),
    )
    name = models.CharField(max_length=30, choices=kind_choices)


class Graph(models.Model):
    experiment = models.ForeignKey(
        Experiment, null=False, blank=False, on_delete=models.CASCADE, related_name='graphs')


class Serie(models.Model):
    graph = models.ForeignKey(
        Graph, null=False, blank=False, on_delete=models.CASCADE, related_name='series')


class Point(models.Model):
    serie = models.ForeignKey(
        Serie, null=False, blank=False, on_delete=models.CASCADE, related_name='points')
    x = models.CharField(max_length=100, null=True, blank=True)
    y = models.FloatField(max_length=100, null=True, blank=True)
