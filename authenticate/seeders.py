from .models import User
from module.models import *
from django.contrib.auth.hashers import make_password


def create_seeder():
    for i in ['input', 'output', 'response', 'graph', 'examples']:
        ele = Element.objects.create(name=i)
        # ele.save()
    esp = User.objects.create(
        email='admin@gmail.com',
        password=make_password('clave'),
        role='admin',
        is_superuser=True,
        is_staff=True,
        is_active=True,
        birth='1997-09-14',
        first_name='Juan',
        last_name='Marcon',
    )
    # esp.save()
    ing = User.objects.create(
        email='edgar@gmail.com',
        password=make_password('clave'),
        role='developer',
        is_superuser=False,
        is_staff=False,
        is_active=True,
        birth='1997-09-14',
        first_name='Ingenieria',
        last_name=' Inversa',
    )
    # ing.save()
    ana = User.objects.create(
        email='nico@gmail.com',
        password=make_password('clave'),
        role='user',
        is_superuser=False,
        is_staff=False,
        is_active=True,
        birth='1997-09-14',
        first_name='Analista',
        last_name='Requerimientos',
    )
    # ana.save()
