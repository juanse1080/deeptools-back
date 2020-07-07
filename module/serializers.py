from rest_framework import serializers
from .models import *
from authenticate.models import User
from django.db import transaction


class ImageSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=500)
    label = serializers.CharField(max_length=200)
    name = serializers.CharField(max_length=200)


class CreateElementsType(serializers.Serializer):
    kind = serializers.CharField(max_length=30)
    len = serializers.IntegerField()
    state = serializers.BooleanField(required=False)
    value = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CheckBuildSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=32)


class ElementTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementType
        fields = '__all__'


class ListModuleSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Docker
        fields = '__all__'


class RetrieveModuleSerializer(serializers.ModelSerializer):
    elements_type = ElementTypeSerializer(many=True)

    class Meta:
        model = Docker
        fields = '__all__'


class RetrieveElementDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementData
        fields = '__all__'


class CreateExperimentSerializer(serializers.ModelSerializer):
    docker = RetrieveModuleSerializer()

    class Meta:
        model = Experiment
        fields = '__all__'


class ListExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        fields = '__all__'


class CreateModuleSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=32, required=False)
    image_name = serializers.CharField(max_length=32, required=False)
    elements = CreateElementsType(many=True)

    def create(self, validated_data):
        temp = validated_data.copy()
        del temp["elements"]
        with transaction.atomic():
            docker = Docker.objects.create(**temp)
            for element in validated_data["elements"]:
                ElementType.objects.create(
                    kind=element['kind'],
                    docker=docker,
                    element=Element.objects.get(name=element['kind']),
                    value=element['value'],
                    len=element['len']
                )
        return docker

    class Meta:
        model = Docker
        fields = '__all__'
