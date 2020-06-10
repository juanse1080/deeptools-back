from .models import User
from module.models import *
from django.contrib.auth.hashers import make_password

def create_seeder():
  for i in ['input', 'output', 'response', 'graph', 'examples']:
    ele = Element.objects.create(name=i)
    # ele.save()
  for i in [['bar', 'Bar graphic'], ['donut', 'Donut chart']]: 
    gr = GraphType.objects.create( name=i[0] )
    # gr.save()
  esp = User.objects.create(
    email='santiago@gmail.com',
    password=make_password('clave'),
    role='admin',
    is_superuser=True,
    is_staff=True,
    is_active=True,
    id=1,
    birth='1997-09-14',
    first_name='Especialista',
    last_name='Ortopedista',
  )
  # esp.save()
  ing = User.objects.create(
    email='edgar@gmail.com',
    password=make_password('clave'),
    role='creator',
    is_superuser=False,
    is_staff=True,
    is_active=True,
    id=2,
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
    is_staff=True,
    is_active=True,
    id=3,
    birth='1997-09-14',
    first_name='Analista',
    last_name='Requerimientos',
  )
  # ana.save()
