
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db import models

import docker as docker_env
from channels.layers import get_channel_layer

from authenticate.models import User
from .utils import *
from .generate.proto import ProtoFile
from .generate.server import ServerFile
from .managers import UserManager

import importlib
import shutil
import traceback
import json
import shutil
import sys
import os

# import __Rmyw9LxbPBhhegjOy3IjvADs9U1KlT.protobuf_pb2 as objects


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
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owner')
    subscribers = models.ManyToManyField(User, related_name='subscriptions')
    language = models.CharField(
        max_length=100, choices=lenguaje_choices, default='python')

    protocol = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=250, unique=True)
    description = models.TextField(null=True)
    image = models.CharField(max_length=100, null=True)
    workdir = models.CharField(max_length=500, null=True)
    file = models.CharField(max_length=100, null=True)
    classname = models.CharField(max_length=100, null=True)
    view = models.CharField(max_length=1, blank=False)
    extensions = models.CharField(max_length=250, null=True, blank=False)

    def get_container(self):
        try:
            client = docker_env.from_env()
            return client.containers.get(self.image_name)
        except docker_env.errors.NotFound as error:
            return None

    def check_active_state(self):
        if self.state == 'active':
            docker = self.get_container()
            return True if docker else False

    def get_container_or_run(self):
        container = self.get_container()
        if container:
            return container
        else:
            return self.run_container()

    def get_public_path(self):
        return f'{settings.MEDIA_URL}{self.id}'

    def get_path(self):
        return f'{settings.MEDIA_ROOT}/{self.id}'

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

            file_.write(proto.create_protobuf(self.image_name))

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
        except:
            exc_type, exc_obj, tb = sys.exc_info()
            print(exc_type)
            print(exc_obj)
            traceback.print_exc()
            # self.delete()
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
            self.delete()
            return [{'stream': "error"}, {'stream': "error"}], [["Error:", "An error occurred during model shrinkage. Check the data and try again"]]

    def run_container(self, builded=False):
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
            self.state = 'builded' if builded else 'active'
            self.save()
            return container
        except docker_env.errors.ContainerError as error:
            print(error)
            return error
        except docker_env.errors.APIError as error:
            print(error)
            return error

    def stop_container(self):
        try:
            container = self.get_container()
            if container:
                self.get_container().stop()
                self.state = 'stopped'
                self.ip = ''
                self.save()
                return True
            return False
        except ValueError as error:
            print(error)
            return False
        except docker_env.errors.APIError as error:
            return False

    def delete_image(self):
        try:
            client = docker_env.from_env()
            client.images.remove(image=self.image_name, force=True)
        except docker_env.errors.ImageNotFound as error:
            print(error)

    def delete_module(self):
        self.stop_container()
        self.delete_image()
        self.state = 'deleted'
        self.save()

    def delete(self, delete_img=False):
        super().delete()
        shutil.rmtree(self.get_path(), ignore_errors=True)
        shutil.rmtree('{0}{1}'.format(
            settings.ENV_ROOT, self.id), ignore_errors=True)


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_logs(self):
        return f"{self.get_workdir()}/logs.txt"

    def get_public_logs(self):
        return f"{self.get_public_path()}/logs.txt"

    def create_workdir(self, outputs=False):
        os.makedirs(self.inputs(), 0o777)
        open(self.get_logs(), "x")
        if outputs:
            os.makedirs(self.outputs(), 0o777)

    def inputs(self):
        return f"{self.get_workdir()}/inputs"

    def outputs(self):
        return f"{self.get_workdir()}/outputs"

    def get_public_path(self):
        return f"{self.docker.get_public_path()}/experiments/user_{self.user.id}/exp_{self.id}"

    def get_workdir(self):
        return '{0}/experiments/user_{1}/exp_{2}'.format(
            self.docker.get_path(), self.user.id, self.id)

    def delete(self):
        shutil.rmtree(self.get_workdir())
        super().delete()

    def run(self):
        try:
            objects = importlib.import_module(
                '{}.protobuf_pb2'.format(self.docker.id))

            input = self.docker.elements_type.filter(kind='input').get()

            if int(input.len) > 0:
                inputs_data = ['{0}/media/user_{1}/exp_{2}/inputs/{3}'.format(
                    self.docker.workdir, self.user.id, self.id, data.value) for data in self.elements.filter(kind='input')]
            else:
                inputs_data = ['{0}/media/user_{1}/exp_{2}/inputs/{3}'.format(
                    self.docker.workdir, self.user.id, self.id, data.value) for data in self.elements.filter(kind='input')][-1]

            outputs = self.docker.elements_type.filter(kind='output')
            have_output = outputs.count() == 1

            if have_output:
                outputs_data = '{0}/media/user_{1}/exp_{2}/outputs'.format(
                    self.docker.workdir, self.user.id, self.id)

            def get_inputs_obj(values, len):
                if len > 0:
                    return objects.Inputs(inputs=(objects.Input(value=value) for value in values))
                else:
                    return objects.Inputs(inputs=objects.Input(value=values))

            def createIn(inputs, outputs, len, have_output=False):
                # print(inputs, outputs, len, have_output)
                if have_output:
                    return {'inputs': get_inputs_obj(inputs, len), 'output': objects.Output(value=outputs)}
                else:
                    return {'inputs': get_inputs_obj(inputs, len)}

            print(createIn(inputs_data, outputs_data, int(input.len), have_output))

            return objects.In(
                **createIn(inputs_data, outputs_data, int(input.len), have_output)
            )

        except ValueError as erro:
            print("############ ERROR", erro)
            return ({"progress": 0, "state": 'Error', "description": "Something unexpected happened, try again"})


class ElementData(models.Model):
    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name='elements')
    kind = models.CharField(max_length=30)
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    value = models.TextField(null=True)
    name = models.TextField(null=True)
    example = models.BooleanField(default=False)

    def rename_output(self):
        if self.kind == "output":
            ext = self.name.split('.')[-1]
            new_name = f"output_{self.id}"
            self.value = f"{new_name}.{ext}"
            os.rename(f"{self.experiment.outputs()}/{self.name}",
                      f"{self.experiment.outputs()}/{self.value}")
            self.save()
        else:
            raise Exception("This is not a kind output")

    def copy_input(self, to):
        print(to)
        if self.kind == "input":
            shutil.copyfile(self.get_root_path(), to)
            return to.split('/')[-1]
        else:
            raise Exception("This is not a kind input")

    def get_root_path(self):
        if self.kind == "input":
            return '{}/{}'.format(self.experiment.inputs(), self.value)
        if self.kind == "output":
            return'{}/{}'.format(self.experiment.outputs(), self.value)

    def get_public_path(self):
        if self.kind == "input":
            return f"{self.experiment.get_public_path()}/inputs/{self.value}"
        if self.kind == "output":
            return f"{self.experiment.get_public_path()}/outputs/{self.value}"
        return None

    def delete(self):
        if os.path.exists(self.get_root_path()):
            os.remove(self.get_root_path())
        super().delete()


class Records(models.Model):
    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name='records')
    description = models.CharField(max_length=200)
    progress = models.CharField(max_length=30)
    state = models.CharField(max_length=20, default='execute')

    def write(self):
        with open(self.experiment.get_logs(), "a") as file:
            file.write(f"{self.description}\n")
