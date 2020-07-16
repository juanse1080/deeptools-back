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
        dockers = self.request.user.subscriptions.all()
        print(dockers)
        return Response(self.serializer_class(dockers, many=True).data)


class listTests(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListExperimentSerializer

    def list(self, request, *args, **kwargs):
        dockers = self.request.user.subscriptions.filter(
            image_name=self.kwargs['pk'])
        if dockers.count() == 0:
            return Response("Module not found", status=status.HTTP_404_NOT_FOUND)
        elif dockers.count() == 1:
            data = dict()
            data["test"] = self.serializer_class(dockers.get().experiments.filter(
                state__in=['executing', 'executed']), many=True).data
            data["docker"] = ListModuleSerializer(dockers.get()).data
            return Response(data)
        else:
            return Response("Error", status=status.HTTP_409_CONFLICT)
