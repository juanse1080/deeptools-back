from django.conf.urls import include, url
from django.urls import path
from . import views
from .api import module, experiment

urlpatterns = [
    # NOTE: URLS EXPERIMENT
    path('run/<str:pk>/examples',
         experiment.listExamplesModule.as_view(), name="list_examples"),
    path('run/<str:pk>', experiment.createExperiment.as_view(), name="run_container"),
    path('experiment', experiment.listExperiments.as_view(),
         name="list_experiments"),
    path('experiment/<int:pk>', experiment.retrieveExperiment.as_view(),
         name="retrieve_experiment"),
    path('upload/<str:pk>/examples', experiment.uploadExamples.as_view(),
         name="upload_examples_experiment"),
    path('upload/<str:pk>', experiment.createElementData.as_view(),
         name="upload_element"),
    path('upload/remove/<str:pk>',
         experiment.DeleteElementData.as_view(), name="remove_element"),

    # NOTE: URLS MODULE
    path('check', module.checkPermissionsAPI, name="check_permissions"),
    path('images', module.listImages.as_view(), name="list_images"),
    path('create', module.createModule.as_view(), name="create_module"),
    path('stop/<str:pk>', module.stopContainer.as_view(), name="stop_container"),
    path('start/<str:pk>', module.startContainer.as_view(), name="start_container"),
    path('delete/<str:pk>', module.deleteContainer.as_view(),
         name="delete_container"),
    path('subscriptions/<str:pk>', module.subscriptionsContainer.as_view(),
         name="subscriptions_container"),
    path('subscribers/<str:pk>', module.subscribersContainer.as_view(),
         name="subscribers_container"),
    path('<str:pk>', module.retrieveModule.as_view(), name="detail_module"),
    path('', module.listModule.as_view(), name="list_modules"),
]
