from django.urls import re_path, path
from front.views import front

urlpatterns = [
    re_path(r'^sign-in', front),
    re_path(r'^sign-up', front),
    re_path(r'^', front),
    path('*', front),
]
