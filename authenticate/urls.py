from django.urls import path
# Import other modules
from rest_framework_simplejwt.views import TokenRefreshView
# Import local
from .api import *
from .views import template

urlpatterns = [
    path('sign-in', template, name='template'),
    path('login/', LoginAPI.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('subscriptions/<str:pk>', listTests.as_view(), name='tests'),
    path('subscriptions/', listSubscriptions.as_view(), name='subscriptions'),
    path('algorithms/', listModules.as_view(), name='algorithms'),
    path('experiment/delete/<str:pk>',
         deleteExperiments.as_view(), name='remove_experiment'),
    path('experiment/clone/<str:pk>',
         cloneExperiment.as_view(), name='clone_experiment'),
    path('running', listRunningExperiments.as_view(), name='running'),
    path('notifications/<int:pk>', UpdateNotification.as_view(),
         name='show_notification'),
    path('notifications/', listNotifications.as_view(), name='notifications'),
    path('profile/<int:pk>', profile.as_view(), name='profile'),
]
