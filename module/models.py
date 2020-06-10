from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from authenticate.models import User
from .utils import *
from .managers import UserManager
import shutil
import os

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
    state = models.BooleanField(default=True)
    name = models.CharField(max_length=100, unique=True)
    ip = models.CharField(max_length=30, unique=True, null=True)
    user = models.ForeignKey(
        User, null=True, on_delete=models.CASCADE, related_name='owner')
    languaje = models.CharField(max_length=100, choices=lenguaje_choices)
    proto_path = models.CharField(max_length=500, null=True)
    base_path = models.CharField(max_length=500, null=True)
    img_name = models.CharField(max_length=500, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    def get_container(self):
        client = docker_env.from_env()
        return client.containers.get(self.img_name)

    def get_proto_name(self):
        return self.proto_path.split('.')[0]

    def get_experiments(self):
        return self.experiments.order_by('id')

    def get_last_experiment(self):
        return self.experiments.order_by('-id')[0]

    def have_experiments(self):
        return len(self.experiments.all()) > 0

    def get_path(self):
        return '%s/%s' % (settings.MEDIA_ROOT, self.img_name.lower())

    def create_folders(self):
        os.makedirs('%s/experiments' % self.get_path(), 0o777)

    def create_docker(self, file):
        try:
            self.create_folders()
            handle_uploaded_file(file, self.get_path())
            terminal_out(
                "python -m grpc_tools.protoc --proto_path=%(media)s --python_out=%(media)s/%(img_name)s --grpc_python_out=%(media)s/%(img_name)s %(img_name)s/%(proto)s" % {
                    'media': settings.MEDIA_ROOT,
                    'img_name': self.img_name.lower(),
                    'proto':  self.proto_path
                }
            )
            shutil.move('%(media)s/%(img_name)s/%(img_name)s' % {
                'media': settings.MEDIA_ROOT, 'img_name': self.img_name.lower()
            },
                settings.ENV_ROOT
            )
            self.run_model()
            container = self.get_container()
            self.ip = '%s:50051' % container.attrs['NetworkSettings']['IPAddress']
        except:
            self.delete_model()
            return False
        self.save()
        return True

    def run_model(self):
        client = docker_env.from_env()
        client.containers.run(
            image=self.img_name,
            command='python server.py',
            detach=True,
            name=self.img_name,
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
        shutil.rmtree('%s/%s' % (
            settings.ENV_ROOT, self.img_name.lower()
        ))
        self.stop_model()
        self.delete()


    # def create_folder(self):
    #     os.makedirs('%s/%s/experiments/user_%s/%s/input' % (settings.MEDIA_ROOT,
    #                                                         self.img_name, request.user.id_card, experiment.id), 0o777)
    #     os.makedirs('%s/%s/experiments/user_%s/%s/output' % (settings.MEDIA_ROOT,
    #                                                             self.img_name, request.user.id_card, experiment.id), 0o777)

    def create_folder_docker(self):
        path = '%(media)s/%(img_name)s/experiments' % paths
        os.makedirs(path, 0o777)


class ElementType(models.Model):
    kind_choices = (
        ('img', 'Image'),
        ('txt', 'Text'),
        ('video', 'Video'),
        ('graph', 'Graph'),
    )
    kind = models.CharField(max_length=30, choices=kind_choices)
    docker = models.ForeignKey(Docker, null=False, blank=False,
                               on_delete=models.CASCADE, related_name='elements_type')
    element = models.ForeignKey(
        'Element', null=False, blank=False, on_delete=models.CASCADE, related_name='types')


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
