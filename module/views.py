from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages

import docker
import json
import sys
import os

from .forms import *
from .models import *
from .utils import *
from django.conf import settings
import grpc
import shutil

from django.contrib.auth.hashers import make_password

from google.protobuf.json_format import MessageToDict


def create_usr(request):
    for i in ['input', 'output', 'response', 'graph', 'examples']:
        ele = Element.objects.create(
            name=i
        )
        ele.save()
    for i in [['bar', 'Bar graphic'], ['donut', 'Donut chart']]:
        # print(i)
        gr = GraphType.objects.create(
            name=i[0]
        )
        gr.save()
    esp = User.objects.create(
        email='santiago@gmail.com',
        password=make_password('clave'),
        role='admin',
        is_superuser=True,
        is_staff=True,
        is_active=True,
        id_card=1,
        birth='1997-09-14',
        first_name='Especialista',
        last_name='Ortopedista',
    )
    esp.save()
    ing = User.objects.create(
        email='edgar@gmail.com',
        password=make_password('clave'),
        role='creator',
        is_superuser=False,
        is_staff=True,
        is_active=True,
        id_card=2,
        birth='1997-09-14',
        first_name='Ingenieria',
        last_name=' Inversa',
    )
    ing.save()
    ana = User.objects.create(
        email='nico@gmail.com',
        password=make_password('clave'),
        role='user',
        is_superuser=False,
        is_staff=True,
        is_active=True,
        id_card=3,
        birth='1997-09-14',
        first_name='Analista',
        last_name='Requerimientos',
    )
    ana.save()
    return render(request, 'docker/run_process.html')


@login_required
def create_docker(request):
    client = docker.from_env()
    images = [i.tags[0].split(':')[0] for i in client.images.list() if i.tags]
    if request.method == "POST":
        form = DockerForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            paths = {'media': settings.MEDIA_ROOT, 'img_name': request.POST.get(
                'img_name').lower(), 'proto': data['proto_path'].name}
            query_copy = request.POST.copy()

            docker_ = form.save()
            docker_.user = request.user
            docker_.base_path = '%s%s' % (
                settings.MEDIA_URL, paths['img_name'])
            docker_.save()
            port = created_port(docker_.id)
            paths.update({'ip': port})
            docker_.ip = port
            print(images)
            try:
                os.makedirs('%(media)s/%(img_name)s/experiments' %
                            paths, 0o777)
                handle_uploaded_file(
                    data['proto_path'], '%(media)s/%(img_name)s' % paths)
                terminal_out(
                    "python -m grpc_tools.protoc --proto_path=%(media)s --python_out=%(media)s/%(img_name)s --grpc_python_out=%(media)s/%(img_name)s %(img_name)s/%(proto)s" % paths)
                shutil.move('%(media)s/%(img_name)s/%(img_name)s' % paths,
                            '/home/juanmarcon/Documents/Project/django/lib/python3.7/site-packages/')
                client.containers.run(image=paths['img_name'], command='python server.py', detach=True, name=docker_.img_name, ports={
                                      50051: paths['ip']}, remove=True, volumes={'%(media)s/%(img_name)s/experiments' % paths: {'bind': '/media', 'mode': 'rw'}})

                # terminal_out("sudo docker run -d --rm --name %(img_name)s -p %(ip)s:50051 -v %(media)s/%(img_name)s/experiments:/media %(img_name)s:latest python server.py" % paths)
            except Exception as e:
                messages.error(request, e)
                return render(request, 'docker/create.html', {'kind': GraphType.kind_choices, 'images': images})
            docker_.proto_path = data['proto_path'].name
            docker_.save()

            for item, value in enumerate(query_copy.pop('type')):
                print(item, value)
                if value != 'none':
                    ElementType.objects.create(
                        kind=value,
                        docker=docker_,
                        element=Element.objects.get(id=item+1),
                    )
            return redirect('run_process', docker_id=docker_.id)
        return render(request, 'docker/create.html', {'errors': form.errors, 'kind': GraphType.kind_choices, 'images': images})
    return render(request, 'docker/create.html', {'kind': GraphType.kind_choices, 'images': images})


@login_required
def run_process(request, docker_id):
    docker = Docker.objects.get(id=docker_id)
    docker_data = docker.__dict__

    def create_iterator(paths):
        for url in paths:
            yield objects.Input(path=url)

    if request.method == "POST":
        form = ExperimentForm(request.POST, request.FILES)
        if form.is_valid():
            experiment = form.save()
            experiment.user = request.user
            experiment.docker = docker
            data = form.cleaned_data

            os.makedirs('%s/%s/experiments/user_%s/%s/input' % (settings.MEDIA_ROOT,
                                                                docker.img_name, request.user.id_card, experiment.id), 0o777)
            os.makedirs('%s/%s/experiments/user_%s/%s/output' % (settings.MEDIA_ROOT,
                                                                 docker.img_name, request.user.id_card, experiment.id), 0o777)

            file_ = handle_uploaded_file(data['input_file'], '%s/%s/experiments/user_%s/%s/input' % (
                settings.MEDIA_ROOT, docker.img_name, request.user, experiment.id))

            exec('from %s import %s_pb2_grpc' %
                 (docker.img_name, docker.get_proto_name()), globals())
            exec('from %s import %s_pb2' %
                 (docker.img_name, docker.get_proto_name()), globals())

            channel = grpc.insecure_channel('0.0.0.0:%s' % docker.ip)

            # create a stub (client)
            exec('stub = %s_pb2_grpc.ServerStub(channel)' %
                 docker.get_proto_name(), locals(), globals())
            exec('in_ = %s_pb2.Input()' %
                 docker.get_proto_name(), locals(), globals())

            in_.input_path = '/media/user_%s/%s/input/' % (
                request.user.id_card, experiment.id)
            in_.input_file = data['input_file'].name
            in_.output_path = '/media/user_%s/%s/output/' % (
                request.user.id_card, experiment.id)
            in_.output_file = 'output_%s' % data['input_file'].name

            metadata = [('ip', '0.0.0.0')]
            response = stub.Run(
                in_,
                metadata=metadata
            )

            elements = [i.element.name for i in docker.elements_type.all()]
            
            print(response)

            if 'graph' in elements:
                data_graph = [{'name': resp.class_, 'y': resp.value}
                              for resp in response.result]

                graph_type = GraphType.objects.all().filter(
                    name=docker.elements_type.all().filter(element__name='graph')[0].kind)[0]

                for i in data_graph:
                    Graph.objects.create(
                        x=i['name'],
                        y=i['y'],
                        experiment=experiment,
                        kind=graph_type
                    )

            if 'output' in elements:
                output_path = '%s%s/experiments/user_%s/%s/output/%s' % (
                    settings.MEDIA_URL, docker.img_name, request.user.id_card, experiment.id, response.path)
                experiment.output_file = output_path

            if 'input' in elements:
                input_path = '%s%s/experiments/user_%s/%s/input/%s' % (
                    settings.MEDIA_URL, docker.img_name, request.user.id_card, experiment.id, data['input_file'].name)
                experiment.input_file = input_path

            if 'response' in elements:
                experiment.response = response.response

            experiment.save()

            return redirect('show_experiments', docker_id=docker.id, experiment_id=experiment.id)
    return render(request, 'docker/run.html', {'docker': docker})


@login_required
def show_experiments(request, docker_id, experiment_id):
    def update_data(dict_, label, kind, value):
        """
            update data 
        """
        dict_.update({label: {'kind': kind, 'value': value}})

    docker = Docker.objects.get(id=docker_id)
    experiment = Experiment.objects.get(id=experiment_id)

    elements = [i.element.name for i in docker.elements_type.all()]
    view = {'elements': elements, 'docker': docker, 'experiment': int(experiment_id)}

    if 'graph' in elements:
        data_graph = [{'name': graph.x, 'y': graph.y}
                      for graph in experiment.graphs.all()]

        update_data(
            view,
            'graph',
            experiment.graphs.all()[0].kind.name,
            data_graph
        )
        
        view.update(
            {'categories': [graph.x for graph in experiment.graphs.all()]})
        
    if 'output' in elements:
        update_data(
            view,
            'output',
            docker.elements_type.all().filter(element__name='output')[0].kind,
            experiment.output_file
        )

    if 'input' in elements:
        update_data(
            view,
            'input',
            docker.elements_type.all().filter(element__name='input')[0].kind,
            experiment.input_file
        )

    if 'response' in elements:
        update_data(
            view,
            'response',
            docker.elements_type.all().filter(
                element__name='response')[0].kind,
            experiment.response
        )

    return render(request, select_view(elements), view)


def cnn(request):
    def create_iterator(paths):
        for url in paths:
            yield objects.Input(path=url)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        print(request.FILES)
        if form.is_valid():
            file_ = handle_uploaded_file(request.FILES['file'])
            file_name = file_.split('/')[-1]

            shutil.move("%s/%s" % (settings.MEDIA_ROOT, file_name),
                        "%s/CNN/data/%s" % (settings.MEDIA_ROOT, file_name))
            channel = grpc.insecure_channel('localhost:50051')

            # create a stub (client)
            stub = cnn_service.CnnStub(channel)
            metadata = [('ip', '127.0.0.1')]
            response = stub.Test(
                create_iterator(["data/%s" % file_name]),
                metadata=metadata
            )
            result = [resp.result.value for resp in response]
            print(result[0])
            return render(request, 'cnn/img.html', {'result': result[0], 'file': "/CNN/data/"+file_name})
        return render(request, 'cnn/img.html')
    else:

        # open a gRPC channel
        channel = grpc.insecure_channel('localhost:50051')

        # create a stub (client)
        stub = cnn_service.CnnStub(channel)
        metadata = [('ip', '127.0.0.1')]
        response = stub.History(objects.Empty(), metadata=metadata)
        response = MessageToDict(response)
        val_acc = [resp for resp in response['valAcc']['value']]
        # print([i for i in response['valAcc']['value']])
        acc = [resp for resp in response['acc']['value']]
        return render(request, 'cnn/show.html', {'val_acc': val_acc, 'acc': acc})
