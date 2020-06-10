from django.conf.urls import include, url
from django.urls import path
from . import views
from .api import *
# from django.contrib.auth.views import login

urlpatterns = [
    ############# Nuevas rutas ######################
    path('images/', listImages.as_view(), name="list_images"),

    ############# Rutas antiguas #######################
    url('graph/(?P<docker_id>[0-9]+)', views.graph, name="graph"),
    url('create', views.DockerCreate.as_view(), name='create_docker'),
    url('usr', views.create_usr, name='create_usr'),
    url('(?P<docker_id>[0-9]+)/(?P<experiment_id>[0-9]+)',
        views.show_experiments, name="show_experiments"),
    url('(?P<docker_id>[0-9]+)',
        views.DockerDetail.as_view(), name="detail_docker"),
    # url('(?P<docker_id>[0-9]+)', views.run_process, name="run_process"),
    # url('create/', views.create_docker, name='create_docker'),

    url('', views.DockerList.as_view(), name='list_docker'),





    # url('background/', views.background, name='background'),
    url('cnn/', views.cnn, name='cnn'),




]
