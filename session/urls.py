from django.conf.urls import include, url
from . import views
# from django.contrib.auth.views import login

urlpatterns = [
    url('login/', views.template, name='login'),
    url('logout/', views.logout_view, name='logout'),
]