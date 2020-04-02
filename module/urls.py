from django.conf.urls import include, url
from . import views
# from django.contrib.auth.views import login

urlpatterns = [
    # url('create/', views.create_docker, name='create_docker'),
    url('create/', views.create_docker, name='create_docker'),
    url('graph/(?P<docker_id>[0-9]+)/', views.graph, name="graph"),

    url('(?P<docker_id>[0-9]+)/(?P<experiment_id>[0-9]+)', views.show_experiments, name="show_experiments"),
    url('usr/', views.create_usr, name='create_usr'),
    url('(?P<docker_id>[0-9]+)/', views.run_process, name="run_process"),
    
    # url('background/', views.background, name='background'),
    url('cnn/', views.cnn, name='cnn'),
]