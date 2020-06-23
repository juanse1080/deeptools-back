from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import *
import asyncio
import json


class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def build_module(self, id):
        module = Docker.objects.get(image_name=id)
        module.build_image()

    async def build(self, data):
        await self.build_module(self.room_name)
        content = {
            'command': 'all',
            'progress': "prueba"
        }
        await self.send_progress(content)

    commands = {
        'build': build,
    }

    async def connect(self):

        self.room_name = self.scope["url_route"]["kwargs"]["pk"]
        self.room_group_name = 'progress_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.commands[data['command']](self, data)

    async def disconnect(self, close_code):
        # leave group room
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def send_progress(self, progress):
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'progress_group',
                'progress': progress
            }
        )

    async def progress_group(self, event):
        self.items = (event['progress'])
        print("PROGRESS GROUP")
        print(event["progress"])
        content = {
            'command': 'all',
            'progress': event["progress"]
        }
        await self.send(text_data=json.dumps(content))
