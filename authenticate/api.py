from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.db.models.functions import Concat, Lower
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, mixins, authentication, permissions, status
import os
from django.conf import settings
from rest_framework.response import Response
from module.utils import handle_uploaded_file
from module.models import Docker, Experiment, ElementData, Element
from .models import Notification, User
from .serializers import MyTokenObtainPairSerializer, ListModuleSerializer, ListExperimentSerializer, RetrieveExperimentSerializer, FilterDockerSerializers, listSubscriptionSerializer, listTestSerializer, listRunningSerializer, listCompletedSerializer, ListActiveModules, NotificationsSerializer, UserSerializer, SignUpSeralizers, UpdateUserSerializer, UserRedux


class SignUp(generics.CreateAPIView):
    serializer_class = SignUpSeralizers

    def create(self, request, *args, **kwargs):
        if User.objects.filter(email=self.request.data["email"]).count() > 0:
            return Response({"email": ["This email is in use, try with other"]}, status=status.HTTP_409_CONFLICT)
        if not self.request.data["password"] == self.request.data["password2"]:
            return Response({"password": ["Passwords do not match"]}, status=status.HTTP_409_CONFLICT)
        temp = self.request.data.copy()
        del temp["password2"]

        serializer = self.serializer_class(data=temp)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_409_CONFLICT)


class LoginAPI(TokenObtainPairView):  # NOTE Login
    serializer_class = MyTokenObtainPairSerializer


class listSubscriptions(generics.ListAPIView):  # NOTE list module
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = listSubscriptionSerializer

    def list(self, request, *args, **kwargs):
        others = self.request.user.subscriptions.filter(
            state__in=['building', 'stopped'])
        actives = self.request.user.subscriptions.filter(
            state='active')
        for active in actives:
            if not active.check_active_state():
                active.state = 'stopped'
                active.save()
        modules = []
        for module in actives.union(others).order_by('created_at'):
            module.background = f"{module.get_public_path()}/{module.background}"
            modules.append(module)

        return Response(self.serializer_class(modules, many=True).data)


class listTests(generics.ListAPIView):  # NOTE list experiments
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            if self.request.user.role == 'developer':
                docker = Docker.objects.get(image_name=self.kwargs['pk'])
                if not docker.user.id == self.request.user.id:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)
            elif self.request.user.role == 'user':
                if self.request.user.subscriptions.filter(image_name=self.kwargs['pk']).count() == 0:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)
                docker = Docker.objects.get(image_name=self.kwargs['pk'])
            elif self.request.user.role == 'admin':
                docker = Docker.objects.get(image_name=self.kwargs['pk'])
            else:
                return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

            data = dict()
            data["test"] = listTestSerializer(docker.experiments.filter(
                user=self.request.user, state__in=['executing', 'executed', 'error']).order_by('-updated_at'), many=True).data
            data["docker"] = ListModuleSerializer(docker).data
            return Response(data)
        except ObjectDoesNotExist:
            return Response("Module not found", status=status.HTTP_404_NOT_FOUND)


class deleteExperiments(generics.DestroyAPIView):  # NOTE Delete experiment
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            experiment = Experiment.objects.get(id=self.kwargs['pk'])
            if not experiment.user.id == self.request.user.id:
                return Response("Permissions denied", status=status.HTTP_403_FORBIDDEN)
            experiment.delete()
            return Response(True)
        except ObjectDoesNotExist:
            return Response("Module not found", status=status.HTTP_404_NOT_FOUND)


class cloneExperiment(generics.CreateAPIView):  # NOTE Clone experiment
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            if self.request.user.role == 'developer':
                experiment = Experiment.objects.get(id=self.kwargs['pk'])
                if not experiment.user.id == self.request.user.id:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)
            elif self.request.user.role == 'user':
                experiment = Experiment.objects.get(id=self.kwargs['pk'])
                if not experiment.user.id == self.request.user.id:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)
            elif self.request.user.role == 'admin':
                experiment = Experiment.objects.get(id=self.kwargs['pk'])
            else:
                return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

            if not experiment.docker.state == 'active':
                return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

            output = experiment.docker.elements_type.filter(kind='output')
            output = False if output.count() == 0 else True

            new_experiment, created = Experiment.objects.get_or_create(
                docker=experiment.docker, user=self.request.user, state='created')
            if created:
                new_experiment.create_workdir(outputs=output)

            for data in experiment.elements.filter(kind='input'):
                element = ElementData.objects.create(
                    experiment=new_experiment, kind='input', element=Element.objects.get(name='input'), name=data.name)
                element.value = data.copy_input(
                    f"{new_experiment.get_workdir()}/inputs/input_{element.id}.{data.name.split('.')[-1]}")
                if experiment.user.id == self.request.user.id:
                    element.example = True
                element.save()

            return Response(True)
        except ObjectDoesNotExist:
            return Response("Module not found", status=status.HTTP_404_NOT_FOUND)


class listRunningExperiments(generics.ListAPIView):  # NOTE list running
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = listRunningSerializer

    def list(self, request, *args, **kwargs):
        try:
            if self.request.user.role == 'developer':
                dockers = self.request.user.owner.filter(
                    state__in=['active', 'builded'])
            elif self.request.user.role == 'user':
                dockers = self.request.user.subscriptions.filter(
                    state='active')
            elif self.request.user.role == 'admin':
                dockers = Docker.objects.filter(state__in=['active'])
            else:
                return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)
            group_experiments = []
            for docker in dockers:
                exp = docker.experiments.filter(
                    user=self.request.user, state='executing').order_by('-created_at')
                if exp.count() > 0:
                    group_experiments.append(self.serializer_class(
                        exp, many=True).data)

            return Response(group_experiments)
        except ObjectDoesNotExist:
            return Response("Module not found", status=status.HTTP_404_NOT_FOUND)


class UpdateNotification(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        try:
            notification = Notification.objects.get(id=self.kwargs['pk'])
            if not notification.owner.id == self.request.user.id:
                return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

            notification.is_active = False
            notification.save()

            return Response(True)
        except ObjectDoesNotExist:
            return Response("Notification not found", status=status.HTTP_404_NOT_FOUND)


class listModules(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListActiveModules

    def list(self, request, *args, **kwargs):
        modules = Docker.objects.filter(state='active')
        subscriptions = self.request.user.subscriptions.exclude(
            state='deleted')
        all = (subscriptions | modules).distinct()
        for module in all:
            module.image = module.subscribers.count()
            module.background = f"{module.get_public_path()}/{module.background}"
        data = self.serializer_class(all, many=True).data
        # print(data[0])
        return Response(data)


class listNotifications(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationsSerializer

    def list(self, request, *args, **kwargs):
        notifications = self.request.user.notifications.all().order_by('-created_at')
        return Response(self.serializer_class(notifications, many=True).data)


class UserInfo(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        return Response(self.serializer_class(self.request.user).data)


class UpdateUser(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateUserSerializer

    def update(self, request, *args, **kwargs):
        data = dict()
        user = self.request.user
        for key, value in self.request.data.items():
            print(key, value, type(value))
            data[key] = value

        if "photo" in data:
            path = f'{settings.MEDIA_ROOT}/users'
            if os.path.exists(user.photo) and not user.photo == "/media/users/default.png":
                os.remove(user.photo)
            name = handle_uploaded_file(data["photo"], path, user.id)
            data["photo"] = f"/media/users/{name}"

        if "email" in data:
            user_with_email = User.objects.filter(email=data["email"])
            if user_with_email.count() == 1:
                if not user_with_email.get().id == user.id:
                    return Response({"email": ["This email is used"]}, status=status.HTTP_409_CONFLICT)

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            for key, value in data.items():
                setattr(user, key, value)
            user.save()
            return Response(UserRedux(user).data)
        else:
            return Response(serializer.errors, status=status.HTTP_409_CONFLICT)


class profile(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=self.kwargs['pk'])
            if self.request.user.role == 'user' and not self.request.user.id == self.kwargs['pk'] and user.role == 'user':
                return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)
            if self.request.user.role == 'developer' and not self.request.user.id == self.kwargs['pk']:
                _is = False
                for docker in self.request.user.owner.exclude(state='active'):
                    if user in docker.subscribers.all():
                        _is = True
                        break
                if not _is:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

            if user.role == 'developer':
                dockers = user.owner.filter(state='active')
            elif user.role == 'user':
                if self.request.user.id == self.kwargs['pk']:
                    dockers = user.subscriptions.all()
                else:
                    dockers = user.subscriptions.filter(
                        user=self.request.user).exclude(state='deleted')
            else:
                return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

            modules = []
            for module in dockers:
                module.image = module.subscribers.count()
                module.background = f"{module.get_public_path()}/{module.background}"
                modules.append(module)
            data = self.serializer_class(user).data
            data["algorithms"] = ListActiveModules(modules, many=True).data
            data["subscriptions"] = user.subscriptions.count() if self.request.user.id == self.kwargs['pk'] else user.subscriptions.filter(
                user=self.request.user).exclude(state='deleted').count()
            data["owner"] = user.owner.filter(state='active').count()
            return Response(data)
        except ObjectDoesNotExist:
            return Response("Module not found", status=status.HTTP_404_NOT_FOUND)


class dashboard(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            data = {}
            data["running"] = listRunningSerializer(self.request.user.experiments.filter(
                state='executing', docker__state='active').order_by('-created_at')[0:10], many=True).data
            data["last"] = listCompletedSerializer(self.request.user.experiments.filter(
                state='executed').order_by('-created_at')[0:10], many=True).data

            if self.request.user.role == "user":
                modules = []
                for module in Docker.objects.filter(state='active').exclude(subscribers=self.request.user).order_by('-created_at')[0:10]:
                    # print(type(module))
                    module.image = module.subscribers.count()
                    module.background = f"{module.get_public_path()}/{module.background}"
                    modules.append(module)
            elif self.request.user.role == "developer":
                modules = []
                for module in Docker.objects.filter(user=self.request.user).order_by('-created_at')[0:10]:
                    module.image = module.subscribers.count()
                    module.background = f"{module.get_public_path()}/{module.background}"
                    modules.append(module)
            data["news"] = ListActiveModules(modules, many=True).data
            return Response(data)
        except ObjectDoesNotExist:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)


class findAll(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        dockers = []
        print(
            Docker.objects.annotate(name_lower=Lower('name'), description_lower=Lower('description')).filter(
                Q(Q(name_lower__contains=self.request.data["value"].lower()) | Q(description_lower__contains=self.request.data["value"])), state='active').query
        )
        for docker in Docker.objects.annotate(name_lower=Lower('name'), description_lower=Lower('description')).filter(
                Q(Q(name_lower__contains=self.request.data["value"].lower()) | Q(description_lower__contains=self.request.data["value"])), state='active')[:10]:
            docker.background = f"{docker.get_public_path()}/{docker.background}"
            dockers.append(docker)
        users = User.objects.annotate(name=Lower(Concat('first_name', 'last_name'))).filter(
            role='developer', name__contains=self.request.data["value"].lower())
        data = {}
        data["dockers"] = FilterDockerSerializers(dockers, many=True).data
        data["users"] = UserSerializer(users, many=True).data
        return Response(data)
