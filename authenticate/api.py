from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, mixins, authentication, permissions, status
from rest_framework.response import Response
from module.models import Docker, Experiment, ElementData, Element
from .models import Notification
from .serializers import MyTokenObtainPairSerializer, ListModuleSerializer, ListExperimentSerializer, RetrieveExperimentSerializer
from .serializers import listSubscriptionSerializer, listTestSerializer, listRunningSerializer, ListActiveModules, NotificationsSerializer


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
        return Response(self.serializer_class(actives.union(others).order_by('created_at'), many=True).data)


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
