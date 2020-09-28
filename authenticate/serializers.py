from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Notification
from django.contrib.auth.hashers import make_password
from module.models import *
from django.contrib.auth.models import Group


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name",
                  "photo", "role", "owner", "subscriptions", "email"]


class UpdateUserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=60, allow_null=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name",
                  "photo", "email"]


class UserRedux(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "role",
                  "photo", "id"]


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
        data['token']['refresh'] = str(refresh)
        data['token']['access'] = str(refresh.access_token)

        data['user'] = UserRedux(self.user).data

        return data


class SignUpSeralizers(serializers.ModelSerializer):

    def validate(self, attrs):
        print("VALIDATE: ", attrs)
        data = super().validate(attrs)
        user = User.objects.create(**attrs)
        user.password = make_password(attrs['password'])
        if user.role in ["user", "developer"]:
            user.groups.add(Group.objects.get(name=user.role))
        user.save()

        refresh = RefreshToken.for_user(user)

        data['token'] = {}
        data['user'] = {}

        data['token']['refresh'] = str(refresh)
        data['token']['access'] = str(refresh.access_token)
        data['user']['first_name'] = user.first_name
        data['user']['last_name'] = user.last_name
        data['user']['role'] = user.role
        data['user']['photo'] = user.photo
        data['user']['id'] = user.id
        return data

    class Meta:
        model = User
        fields = "__all__"


# NOTE list subscriptions
class listSubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Docker
        fields = ["image_name", "state", "user",
                  "created_at", "name", "description", "background"]


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


class listCompletedSerializer(serializers.ModelSerializer):  # NOTE list running

    class docker(serializers.ModelSerializer):
        user = UserSerializer()

        class Meta:
            model = Docker
            fields = ["user", "name", "image_name", "state"]

    class records(serializers.ModelSerializer):
        class Meta:
            model = Docker
            fields = ["description"]

    docker = docker()
    records = records(many=True)

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
    count = serializers.IntegerField(allow_null=True)

    class Meta:
        model = Docker
        fields = ["image_name", "state", "user",
                  "created_at", "name", "description", "image", "subscribers", "background", "count"]


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


class FilterDockerSerializers(serializers.ModelSerializer):
    class Meta:
        model = Docker
        fields = ["image_name", "name", "description",
                  "subscribers", "background"]
