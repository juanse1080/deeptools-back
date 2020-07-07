from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.conf.urls import url
from django.urls import path
from . import consumer

websocket_urlpatterns = [
    path('ws/build/<str:pk>', consumer.BuildConsumer),
    path('ws/execute/<int:pk>', consumer.ExperimentConsumer),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
