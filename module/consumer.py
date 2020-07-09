from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from .models import *
from .serializers import RecordsSerializer
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
        module.run_container()

    commands = {
        'build': build,
    }

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["pk"]
        self.room_group_name = 'chat_%s' % self.room_name

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


class ExperimentConsumer(WebsocketConsumer):
    def execute(self, data):
        print("execute")
        experiment = Experiment.objects.get(id=self.room_name)
        generator = experiment.run()
        experiment.state = 'executing'
        experiment.save()
        for return_ in generator:
            content = {
                'progress': return_.state.value,
                'description': return_.state.description,
                'state': 'execute'
            }
            Records.objects.create(**content, experiment=experiment)
            self.progress_group([content])

        experiment.state = 'executed'
        experiment.save()
        content = {
            'progress': '100',
            'description': 'Finalized',
            'state': 'success'
        }
        record = Records.objects.create(experiment=experiment, **content)
        self.progress_group([content])

    commands = {
        'execute': execute,
    }

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["pk"]
        self.user_name = self.scope["user"].id
        self.room_group_name = f"{self.room_name}_{self.user_name}"

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
