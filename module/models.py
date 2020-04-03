from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from .utils import *
from .managers import UserManager
import shutil
import os

# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):

    role_choices = (
        ('admin', 'Administrador'),
        ('creator', 'Creator'),
        ('user', 'User'),
    )
    id_card = models.CharField(primary_key=True, max_length=15, unique=True)
    dockers = models.ManyToManyField('Docker', related_name='users')
    role = models.CharField(max_length=10, choices=role_choices)
    birth = models.DateField(null=True)
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    email = models.CharField(max_length=60, unique=True)
    timestamp = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
            This method get full name 
            Returns:
                {str}
                    This is the full name
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
            This method get short name
            Returns:
                {str}
                    This is the fist name
        """
        return self.first_name

    def get_template(self):
        template = {
            'admin': 'navbar/layout.html',
            'creator': 'navbar/layout.html',
            'user': 'navbar/user.html'
        }
        return template[self.role]

    # def email_user(self, subject, message, from_email=None, **kwargs):
    #     '''
    #     Sends an email to this User.
    #     '''
    #     send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        """
            This method cast user to str
            Returns:
                {str}
                    This is user identification
        """
        return self.id_card

    def show(self):
        """
            This method cast user to dict
            Returns:
                {dict}
                    This is user in dict format
        """
        return self.__dict__


class Docker(models.Model):
    lenguaje_choices = (
        ('python', 'Python'),
    )
    name = models.CharField(max_length=100, unique=True)
    ip = models.CharField(max_length=15, unique=True, null=True)
    user = models.ForeignKey(
        User, null=True, on_delete=models.CASCADE, related_name='owner')
    languaje = models.CharField(max_length=100, choices=lenguaje_choices)
    proto_path = models.CharField(max_length=500, null=True)
    base_path = models.CharField(max_length=500, null=True)
    img_name = models.CharField(max_length=500, null=True)

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

    def create_docker(self, file, client):
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
            self.container = client.containers.run(
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
            self.ip = '%s:50051' % self.container.attrs['NetworkSettings']['IPAddress']
            print(self.container.attrs['NetworkSettings']['IPAddress'])
        except:
            self.delete_model()
            return False
        self.save()
        return True

    def delete_model(self, delete_img=False):
        shutil.rmtree(self.get_path())
        shutil.rmtree('%s/%s' % (
            settings.ENV_ROOT, self.img_name.lower()
        ))
        self.container.stop()
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
