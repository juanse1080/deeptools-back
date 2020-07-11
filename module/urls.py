from django.conf.urls import include, url
from django.urls import path
from . import views
from .api import *
# from django.contrib.auth.views import login

urlpatterns = [
    ############# Nuevas rutas ######################
    path('images', listImages.as_view(), name="list_images"),

    path('create', createModule.as_view(), name="create_module"),
    path('check', checkPermissionsAPI, name="check_permissions"),
    path('stop/<str:pk>', stopContainer.as_view(), name="stop_container"),
    path('start/<str:pk>', startContainer.as_view(), name="stop_container"),
    path('delete/<str:pk>', deleteContainer.as_view(), name="delete_container"),

    path('run/<str:pk>', createExperiment.as_view(), name="run_container"),
    path('experiment', listExperiments.as_view(), name="list_experiments"),
    path('experiment/<int:pk>', retriveExperiment.as_view(),
         name="retrieve_experiment"),
    path('upload/<str:pk>', createElementData.as_view(), name="upload_experiment"),
    path('upload/remove/<str:pk>', DeleteElementData.as_view(),
         name="upload_experiment"),
    path('execute/<str:pk>', executeContainer.as_view(), name="upload_experiment"),


    path('<str:pk>', retrieveModule.as_view(), name="detail_module"),
    path('', listModule.as_view(), name="list_modules"),

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
