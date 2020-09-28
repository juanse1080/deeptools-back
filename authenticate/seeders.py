from .models import User
from module.models import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission

role_permissions = {
    'developer': [
        'view_user',
        'add_docker',
        'change_docker',
        'delete_docker',
        'view_docker',
        'add_elementdata',
        'change_elementdata',
        'delete_elementdata',
        'view_elementdata',
        'add_elementtype',
        'change_elementtype',
        'delete_elementtype',
        'view_elementtype',
        'add_experiment',
        'change_experiment',
        'delete_experiment',
        'view_experiment',
        'add_records',
        'change_records',
        'delete_records',
        'view_records',
    ],
    'user': [
        'view_user',
        'view_docker',
        'add_records',
        'change_records',
        'delete_records',
        'view_records',
        'add_elementdata',
        'change_elementdata',
        'delete_elementdata',
        'view_elementdata',
    ]
}


def create_seeder():

    for i in ['input', 'output', 'response', 'graph', 'examples']:
        Element.objects.create(name=i)

    for role, permissions in role_permissions.items():
        group = Group.objects.create(name=role)
        for permission in permissions:
            group.permissions.add(Permission.objects.get(codename=permission))
        group.save()

    # User.objects.create(
    #     email='admin@gmail.com',
    #     password=make_password('clave'),
    #     role='admin',
    #     photo="/media/users/3.jpg"
    #     is_superuser=True,
    #     is_staff=True,
    #     is_active=True,
    #     birth='1997-09-14',
    #     first_name='Juan',
    #     last_name='Marcon',
    # )

    # developer = User.objects.create(
    #     email='developer@gmail.com',
    #     password=make_password('clave'),
    #     role='developer',
    #     photo="/media/users/2.jpg"
    #     is_superuser=False,
    #     is_staff=False,
    #     is_active=True,
    #     birth='1997-09-14',
    #     first_name='Edgar',
    #     last_name='Rangel',
    # )
    # developer.groups.add(Group.objects.get(name='developer'))
    # developer.save()

    # user = User.objects.create(
    #     email='user@gmail.com',
    #     password=make_password('clave'),
    #     role='user',
    #     photo="/media/users/3.jpg"
    #     is_superuser=False,
    #     is_staff=False,
    #     is_active=True,
    #     birth='1997-09-14',
    #     first_name='Oscar',
    #     last_name='Mendoza',
    # )
    # user.groups.add(Group.objects.get(name='user'))
    # user.save()
