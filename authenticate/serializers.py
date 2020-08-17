from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Notification
from module.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name"]


class RetrieveRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Records
        fields = '__all__'


class MyTokenObtainPairSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data['token'] = {}
        data['user'] = {}

        data['token']['refresh'] = str(refresh)
        data['token']['access'] = str(refresh.access_token)
        data['user']['first_name'] = self.user.first_name
        data['user']['last_name'] = self.user.last_name
        data['user']['role'] = self.user.role
        data['user']['id'] = self.user.id

        return data


# NOTE list subscriptions
class listSubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Docker
        fields = ["image_name", "state", "user",
                  "created_at", "name", "description"]


class listTestSerializer(serializers.ModelSerializer):  # NOTE list test
    records = RetrieveRecordSerializer(many=True)

    class Meta:
        model = Experiment
        fields = ["id", "created_at", "updated_at", "state", "records"]


class listRunningSerializer(serializers.ModelSerializer):  # NOTE list running

    class docker(serializers.ModelSerializer):
        user = UserSerializer()

        class Meta:
            model = Docker
            fields = ["user", "name", "image_name", "state"]

    docker = docker()

    class Meta:
        model = Experiment
        fields = '__all__'


class ListModuleSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Docker
        fields = ["image_name", "state", "user",
                  "created_at", "name", "description"]


class ListActiveModules(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Docker
        fields = ["image_name", "state", "user",
                  "created_at", "name", "description", "image", "subscribers", "background"]


class ListExperimentSerializer(serializers.ModelSerializer):
    records = RetrieveRecordSerializer(many=True)

    class Meta:
        model = Experiment
        fields = '__all__'


class ListModuleSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Docker
        fields = ["image_name", "state", "user",
                  "created_at", "name", "description"]


class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class listModuleNameUser(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Docker
        fields = ["user", "name", "image_name", "state"]


class RetrieveExperimentSerializer(serializers.ModelSerializer):
    docker = listModuleNameUser()

    class Meta:
        model = Experiment
        fields = '__all__'


class ListRunningExperiment(serializers.ModelSerializer):
    experiments = RetrieveExperimentSerializer(many=True)

    class Meta:
        model = Docker
        fields = '__all__'
