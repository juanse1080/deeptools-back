from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from .models import *
import asyncio
import json

from io import BytesIO
import time
from datetime import datetime
from django.conf import settings


class ChatConsumer(WebsocketConsumer):
    def build(self, data):
        item = []
        index = 0
        module = Docker.objects.get(image_name=self.room_name)
        generator, steps = module.build_docker()
        for description in generator:
            aux = json.loads(description.decode('utf-8'))
            if "stream" in aux:
                split_ = aux["stream"].split(':')
                numbers = split_[0].split("Step ")
                if len(split_) > 1 and len(numbers) > 1:
                    data = numbers[1].split('/')
                    state = 100*int(data[0])/float(data[1])
                    if index > 0:
                        content = {
                            'state': state,
                            'description': steps[index - 1][-1]
                        }
                        print(content)
                        item.append(content)
                        self.progress_group(item)

                    for step in steps[index][:-1]:
                        content = {
                            'state': state,
                            'description': step
                        }
                        print(content)
                        item.append(content)
                        self.progress_group(item)

                    index += 1

        content = {
            'state': state,
            'description': steps[-1][-1]
        }
        item.append(content)
        self.progress_group(item)
        module.build = False
        module.save()

        index += 1

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
