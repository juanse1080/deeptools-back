from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from .models import *
from authenticate.models import Notification
from authenticate.serializers import NotificationsSerializer
import asyncio
import json

from io import BytesIO
import time
from datetime import datetime
from django.conf import settings


class BuildConsumer(WebsocketConsumer):
    def build(self, data):
        item = []
        index = 0
        progress = 0
        module = Docker.objects.get(image_name=self.room_name)
        generator, steps = module.build_docker()
        for description in generator:
            print(type(description))
            print(description)
            aux = json.loads(description.decode('utf-8'))
            if "stream" in aux:
                if aux["stream"] == 'error':
                    content = {
                        'progress': progress,
                        'description': steps[index][-1],
                        'state': 'error'
                    }
                    print(content)
                    item.append(content)
                    self.progress_group(item)
                    index += 1

                split_ = aux["stream"].split(':')
                numbers = split_[0].split("Step ")
                if len(split_) > 1 and len(numbers) > 1:
                    data = numbers[1].split('/')
                    progress = 100*int(data[0])/float(data[1])
                    if index > 0:
                        content = {
                            'progress': progress,
                            'description': steps[index - 1][-1],
                            'state': 'execute'
                        }
                        print(content)
                        item.append(content)
                        self.progress_group(item)

                    for step in steps[index][:-1]:
                        content = {
                            'progress': progress,
                            'description': step,
                            'state': 'execute'
                        }
                        print(content)
                        item.append(content)
                        self.progress_group(item)

                    index += 1

        content = {
            'progress': progress,
            'description': steps[-1][-1],
            'state': 'success'
        }
        item.append(content)
        self.progress_group(item)
        module.run_container(builded=True)

    commands = {
        'build': build,
    }

    def connect(self):
        print("CONNECT")
        self.room_name = self.scope["url_route"]["kwargs"]["pk"]
        self.room_group_name = f"{self.room_name}_building"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def progress_group(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send_progress',
                'message': message
            }
        )

    def send_progress(self, event):
        self.send(text_data=json.dumps(event["message"]))


def obj_to_data(experiment, elements):
    # outputs elements
    outputs = experiment.docker.elements_type.filter(kind='output')
    path = '{0}/media/user_{1}/exp_{2}/outputs/'.format(
        experiment.docker.workdir, experiment.user.id, experiment.id)
    print(elements.outputs)
    if outputs.count() == 1:
        if int(outputs.get().len) > 0:
            for output in elements.outputs.outputs:
                element = ElementData.objects.create(experiment=experiment, kind='output', element=Element.objects.get(
                    name='output'), name=output.value.split(path)[1])
                element.rename_output()
        else:
            element = ElementData.objects.create(experiment=experiment, kind='output', element=Element.objects.get(
                name='output'), name=elements.outputs.outputs.value.split(path)[1])
            element.rename_output()

    ElementData.objects.create(experiment=experiment, kind='response', element=Element.objects.get(
        name='response'), value=elements.responses.value)

    # graphs elements
    graphs = experiment.docker.elements_type.filter(kind='graph')
    if graphs.count() == 1:
        graph = graphs.get()
        structure = json.loads(graph.value)
        if int(graph.len) > 0:
            for index, serie in enumerate(elements.graphs.graphs.series):
                points = []
                for point in serie.points:
                    points.append([point.x, float(point.y)])
                structure["series"][index]["data"] = points

            ElementData.objects.create(experiment=experiment, kind='graph', element=Element.objects.get(
                name='graph'), value=json.dumps(structure))
        else:
            structure["series"][0]["data"] = [[point.x, float(point.y)]
                                              for point in elements.graphs.graphs.series.points]
            ElementData.objects.create(experiment=experiment, kind='graph', element=Element.objects.get(
                name='graph'), value=json.dumps(structure))

    elif graphs.count() > 1:
        for index, graph in enumerate(elements.graphs.graphs):
            current_graph = graphs[index]
            structure = json.loads(current_graph.value)
            if int(current_graph.len) > 0:
                for index, serie in enumerate(graph.series):
                    points = []
                    for point in serie.points:
                        points.append([point.x, float(point.y)])
                    structure["series"][index]["data"] = points

                ElementData.objects.create(experiment=experiment, kind='graph', element=Element.objects.get(
                    name='graph'), value=json.dumps(structure))
            else:
                structure["series"][0]["data"] = [[point.x, float(point.y)]
                                                  for point in graph.series.points]
                ElementData.objects.create(experiment=experiment, kind='graph', element=Element.objects.get(
                    name='graph'), value=json.dumps(structure))


class ExperimentConsumer(WebsocketConsumer):
    def execute(self, data):
        experiment = Experiment.objects.get(id=self.room_name)

        if experiment.docker.state == 'builded':
            if not experiment.docker.user.id == self.user_name:
                content = {
                    'progress': 0,
                    'description': "Permission denied",
                    'state': 'error'
                }
                self.progress_group([content])

        grpc = importlib.import_module('grpc')
        services = importlib.import_module(
            '{}.protobuf_pb2_grpc'.format(experiment.docker.id))
        channel = grpc.insecure_channel(experiment.docker.ip)
        stub = services.ServerStub(channel)

        try:
            generator = stub.execute(
                experiment.run()
            )
            experiment.state = 'executing'
            experiment.save()

            for return_ in generator:
                content = {
                    'progress': return_.state.value,
                    'description': return_.state.description,
                    'state': 'execute'
                }
                data = return_
                record = Records.objects.create(
                    **content, experiment=experiment)
                record.write()
                self.progress_group([content])

            print(data.elements)
            obj_to_data(experiment, data.elements)

            content = {
                'progress': data.state.value,
                'description': data.state.description,
                'state': 'success'
            }
            record = Records.objects.create(**content, experiment=experiment)
            record.write()
            experiment.state = 'executed'
            experiment.save()

            if experiment.docker.state == 'builded':
                experiment.docker.state = 'active'
                experiment.docker.save()

            self.progress_group([content])

            notification_data = {
                'title': "Your test has ended",
                'link': f"/module/experiment/{experiment.id}",
                'kind': "success",
                'description': f"The test of the {experiment.docker.name} algorithm has finished successfully, select this option for more details",
                'owner': experiment.user
            }

            print(notification_data)

            notification = Notification.objects.create(**notification_data)
            notification.send_notification()

        except grpc.RpcError as e:
            pro = experiment.records.all(
            )[-1].progress if experiment.records.count() > 0 else 0
            content = {
                'progress': pro,
                'description': "An error occurred in the server, our team will contact you when it is solved",
                'state': 'error'
            }
            experiment.state = "error"
            experiment.save()

            Records.objects.create(**content, experiment=experiment)
            self.progress_group([content])

            notification_data = {
                'title': "There was an error during the execution of your algorithm",
                'link': f"/module/{experiment.docker.id}",
                'kind': "error",
                'description': f"The {experiment.docker.name} algorithm had an error during its execution, go to it and check the activity log to solve this problem",
                'owner': experiment.docker.user
            }

            print(notification_data)

            notification = Notification.objects.create(**notification_data)
            notification.send_notification()

            print('###### CreateUser failed with {0}: {1}'.format(
                e.code(), e.details()), e, dir(e))

    commands = {
        'execute': execute,
    }

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["pk"]
        self.user_name = self.scope["url_route"]["kwargs"]["user"]
        self.room_group_name = f"{self.room_name}_{self.user_name}_experiments"

        experiment = Experiment.objects.get(id=self.room_name)
        content = [{'progress': i.progress, 'description': i.description,
                    'state': i.state} for i in experiment.records.all()]

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

        self.send(text_data=json.dumps(content))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def progress_group(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send_progress',
                'message': message
            }
        )

    def send_progress(self, event):
        self.send(text_data=json.dumps(event["message"]))


class NotificationsConsumer(WebsocketConsumer):

    def connect(self):
        self.user_name = self.scope["url_route"]["kwargs"]["user"]
        self.room_group_name = f"{self.user_name}_notifications"

        user = User.objects.get(id=self.user_name)
        content = NotificationsSerializer(
            user.notifications.filter(is_active=True).order_by('-created_at'), many=True).data
        print(content)

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

        self.send(text_data=json.dumps(
            {'action': 'fetch', 'content': content}))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def progress_group(self, action, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send_progress',
                'message': {'action': action, 'content': message}
            }
        )

    def send_progress(self, event):
        self.send(text_data=json.dumps(event["message"]))
