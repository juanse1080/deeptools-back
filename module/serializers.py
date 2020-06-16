from rest_framework import serializers
from .models import *
from django.db import transaction


class ImageSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=500)
    label = serializers.CharField(max_length=200)
    name = serializers.CharField(max_length=200)


class CreateElementsType(serializers.Serializer):
    kind = serializers.CharField(max_length=30)
    len = serializers.IntegerField()
    state = serializers.BooleanField(required=False)


class CreateModule(serializers.Serializer):
    id = serializers.CharField(max_length=32, required=False)
    elements = CreateElementsType(many=True)


class ModuleSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=32, required=False)
    elements = CreateElementsType(many=True)

    def create(self, validated_data):
        temp = validated_data
        del temp["elements"]
        with transaction.atomic():
            docker = Docker.objects.create(**temp)
            for type_ in validated_data["elements"]:
                for element in validated_data["elements"][type_]:
                    ElementType.objects.create(
                        kind=type_,
                        docker=docker,
                        element=Element.objects.get(name=key),
                        value=element.value,
                        len=element.len
                    )
        return docker

    class Meta:
        model = Docker
        fields = '__all__'
