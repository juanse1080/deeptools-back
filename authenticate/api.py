from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, mixins, authentication, permissions, status
from rest_framework.response import Response


class LoginAPI(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class listSubscriptions(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListModuleSerializer

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


class deleteExperiments(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListExperimentSerializer

    def delete(self, request, *args, **kwargs):
        try:
            experiment = Experiment.objects.get(id=self.kwargs['pk'])
            if not experiment.user.id == self.request.user.id:
                return Response("Permissions denied", status=status.HTTP_403_FORBIDDEN)
            experiment.delete()
            return Response(True)
        except ObjectDoesNotExist:
            return Response("Module not found",
                            status=status.HTTP_404_NOT_FOUND)


class listTests(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListExperimentSerializer

    def list(self, request, *args, **kwargs):

        try:
            if self.request.user.role == 'developer':
                docker = Docker.objects.get(
                    user=self.request.user, image_name=self.kwargs['pk'])
            elif self.request.user.role == 'user':
                docker = self.request.user.subscriptions.get(
                    image_name=self.kwargs['pk'])
            elif self.request.user.role == 'admin':
                docker = Docker.objects.get(image_name=self.kwargs['pk'])
            else:
                return Response("Permissions denied", status=status.HTTP_403_FORBIDDEN)

            data = dict()
            data["test"] = self.serializer_class(docker.experiments.filter(
                user=self.request.user, state__in=['executing', 'executed', 'error']), many=True).data
            data["docker"] = ListModuleSerializer(docker).data
            return Response(data)
        except expression as identifier:
            return Response("Module not found", status=status.HTTP_404_NOT_FOUND)
