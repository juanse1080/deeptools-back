from django.core.exceptions import ObjectDoesNotExist

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import permission_classes

from module.models import *
from module.serializers import *
from module.utils import handle_uploaded_file


class createExperiment(generics.CreateAPIView):  # NOTE Create Experiment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetrieveModuleSerializer

    def create(self, request, *args, **kwargs):
        try:
            if self.request.user.role == 'developer':
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'], state__in=['active', 'builded'])

                if not docker.user.id == self.request.user.id:
                    return Response("Permission denied", status=status.HTTP_401_UNAUTHORIZED)

            elif self.request.user.role == 'user':
                if self.request.user.subscriptions.filter(image_name=self.kwargs['pk'], state__in=['active', 'builded']).count() == 0:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'], state__in=['active', 'builded'])

            elif self.request.user.role == 'admin':
                docker = Docker.objects.get(image_name=self.kwargs['pk'])

            else:
                return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

            if docker.state == 'builded':
                if not docker.user.id == self.request.user.id:
                    return Response("Permission denied", status=status.HTTP_401_UNAUTHORIZED)

            input = docker.elements_type.filter(kind='input').get()
            output = docker.elements_type.filter(kind='output')

            output = False if output.count() == 0 else True

            if int(input.len) > 0:
                experiment, created = Experiment.objects.get_or_create(
                    docker=docker, user=self.request.user, state='created')
                if created:
                    experiment.create_workdir(outputs=output)
                experiments = [experiment]
            else:
                experiments = Experiment.objects.filter(
                    docker=docker, user=self.request.user, state='created')
                if experiments.count() == 0:
                    experiment = Experiment.objects.create(
                        docker=docker, user=self.request.user, state='created')
                    experiment.create_workdir(outputs=output)
                    experiments = [experiment]

            element_data = []
            for exp in experiments:
                for data in exp.elements.all():
                    element_data.append(data)

            data = dict(**self.serializer_class(docker).data)
            data["elements"] = RetrieveElementDataSerializer(
                element_data, many=True).data
            return Response(data)
        except ObjectDoesNotExist:
            return Response("Module not found", status=status.HTTP_404_NOT_FOUND)


class listExamplesModule(generics.ListAPIView):  # NOTE List examples
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListExamplesModule

    def list(self, request, *args, **kwargs):
        try:
            if self.request.user.role == 'developer':
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'], state__in=['active'])
                if not docker.user.id == self.request.user.id:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

            elif self.request.user.role == 'user':
                if self.request.user.subscriptions.filter(image_name=self.kwargs['pk'], state__in=['active']).count() == 0:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'], state__in=['active'])

            elif self.request.user.role == 'admin':
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'], state__in=['active'])

            else:
                return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

            experiments = docker.experiments.filter(docker=docker)
            examples = []
            for exp in experiments.all():
                for element in exp.elements.filter(example=True).all():
                    element.href = element.get_public_path()
                    examples.append(element)

            return Response(self.serializer_class(examples, many=True).data)
        except ObjectDoesNotExist:
            return Response("Module not found",
                            status=status.HTTP_404_NOT_FOUND)


class uploadExamples(generics.CreateAPIView):  # NOTE Upload examples experiment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetrieveElementDataSerializer

    def create(self, request, *args, **kwargs):
        try:
            if self.request.user.role == 'developer':
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'], state__in=['active'])
                if not docker.user.id == self.request.user.id:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

            elif self.request.user.role == 'user':
                if self.request.user.subscriptions.filter(image_name=self.kwargs['pk'], state__in=['active']).count() == 0:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'], state__in=['active'])

            elif self.request.user.role == 'admin':
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'], state__in=['active'])

            else:
                return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

            input = docker.elements_type.filter(kind='input').get()
            output = docker.elements_type.filter(kind='output')

            output = False if output.count() == 0 else True

            experiment = None

            if int(input.len) > 0:
                experiment, created = Experiment.objects.get_or_create(
                    docker=docker, user=self.request.user, state='created')
                if created:
                    experiment.create_workdir(outputs=output)

                for id in request.data["examples"]:
                    ref = ElementData.objects.get(id=id)
                    element = ElementData.objects.create(
                        experiment=experiment, kind='input', element=Element.objects.get(name='input'), name=ref.name)
                    element.value = ref.copy_input(
                        f"{experiment.get_workdir()}/inputs/input_{element.id}.{ref.name.split('.')[-1]}")
                    element.save()
            else:
                experiments = Experiment.objects.filter(
                    docker=docker, user=self.request.user, state='created')

                if experiments.count() > 0:
                    for exp in experiments:
                        if exp.elements.all().count() == 0:
                            experiment = exp

                    if not experiment:
                        experiment = Experiment.objects.create(
                            docker=docker, user=self.request.user, state='created')
                        experiment.create_workdir(outputs=output)

                else:
                    experiment, created = Experiment.objects.create(
                        docker=docker, user=self.request.user, state='created')
                    if created:
                        experiment.create_workdir(outputs=output)

                ref = ElementData.objects.get(id=request.data["examples"][0])
                element = ElementData.objects.create(
                    experiment=experiment, kind='input', element=Element.objects.get(name='input'), name=ref.name)
                element.value = ref.copy_input(
                    f"{experiment.get_workdir()}/inputs/input_{element.id}.{ref.name.split('.')[-1]}")
                element.save()

                for id in request.data["examples"][1:]:
                    experiment = Experiment.objects.create(
                        docker=docker, user=self.request.user, state='created')
                    experiment.create_workdir(outputs=output)
                    ref = ElementData.objects.get(id=id)
                    element = ElementData.objects.create(
                        experiment=experiment, kind='input', element=Element.objects.get(name='input'), name=ref.name)
                    element.value = ref.copy_input(
                        f"{experiment.get_workdir()}/inputs/input_{element.id}.{ref.name.split('.')[-1]}")
                    element.save()

            return Response(True)
        except ObjectDoesNotExist:
            return Response("Module not found",
                            status=status.HTTP_404_NOT_FOUND)


class createElementData(generics.CreateAPIView):  # NOTE Create element data
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetrieveElementDataSerializer

    def create(self, request, *args, **kwargs):
        try:
            if self.request.user.role == 'developer':
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'], state__in=['active', 'builded'])
                if not docker.user.id == self.request.user.id:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

            elif self.request.user.role == 'user':
                if self.request.user.subscriptions.filter(image_name=self.kwargs['pk'], state__in=['active']).count() == 0:
                    return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'], state__in=['active', 'builded'])

            elif self.request.user.role == 'admin':
                docker = Docker.objects.get(
                    image_name=self.kwargs['pk'], state__in=['active', 'builded'])

            else:
                return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

            if docker.state == 'builded':
                if not docker.user.id == self.request.user.id:
                    return Response("Permission denied", status=status.HTTP_403_FORBIDDEN)

            input = docker.elements_type.filter(kind='input').get()
            output = docker.elements_type.filter(kind='output')

            output = False if output.count() == 0 else True

            experiment = None

            if int(input.len) > 0:
                experiment, created = Experiment.objects.get_or_create(
                    docker=docker, user=self.request.user, state='created')
                if created:
                    experiment.create_workdir(outputs=output)
            else:
                experiments = Experiment.objects.filter(
                    docker=docker, user=self.request.user, state='created')

                if experiments.count() > 0:
                    for exp in experiments:
                        if exp.elements.all().count() == 0:
                            experiment = exp

                    if not experiment:
                        experiment = Experiment.objects.create(
                            docker=docker, user=self.request.user, state='created')
                        experiment.create_workdir(outputs=output)

                else:
                    experiment, created = Experiment.objects.create(
                        docker=docker, user=self.request.user, state='created')
                    if created:
                        experiment.create_workdir(outputs=output)

            file = request.FILES['file']

            if docker.user.id == self.request.user.id:
                element = ElementData.objects.create(
                    experiment=experiment, kind='input', element=Element.objects.get(name='input'), name=file.name, example=True)
            else:
                element = ElementData.objects.create(
                    experiment=experiment, kind='input', element=Element.objects.get(name='input'), name=file.name)

            element.value = handle_uploaded_file(
                file, experiment.inputs(), 'input_{}'.format(element.id))

            element.save()
            return Response(self.serializer_class(element).data)
        except ObjectDoesNotExist:
            return Response("Module not found",
                            status=status.HTTP_404_NOT_FOUND)


class DeleteElementData(generics.DestroyAPIView):  # NOTE Delete element data
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetrieveElementDataSerializer

    def delete(self, request, *args, **kwargs):
        input = ElementData.objects.get(id=self.kwargs['pk'])
        if not input.experiment.user.id == self.request.user.id:
            return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)
        input.delete()

        experiment = input.experiment
        experiments = experiment.docker.experiments.filter(
            user=self.request.user, state='created')
        if experiments.count() > 1:
            experiment.delete()
        return Response(True)


class listExperiments(generics.ListAPIView):  # NOTE List experiments
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateExperimentSerializer

    def list(self, request, *args, **kwargs):
        if self.request.user.role == 'developer':
            experiment = Experiment.objects.filter(
                state="executing", user=self.request.user)

        elif self.request.user.role == 'user':
            experiment = Experiment.objects.filter(
                state="executing", user=self.request.user)

        elif self.request.user.role == 'admin':
            experiment = Experiment.objects.filter(state="executing")

        else:
            return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)
        return Response(self.serializer_class(experiment, many=True).data)


class retrieveExperiment(generics.RetrieveAPIView):  # NOTE Show experiment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RetriveExperimentSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            experiment = Experiment.objects.get(id=self.kwargs['pk'])
            if experiment.elements.filter(example=True, kind='input').count() == 0:
                if self.request.user.role == 'developer':
                    if not experiment.user.id == self.request.user.id:
                        return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

                elif self.request.user.role == 'user':
                    if not experiment.user.id == self.request.user.id:
                        return Response("Permissions denied", status=status.HTTP_401_UNAUTHORIZED)

                else:
                    return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

            data = dict(self.serializer_class(experiment).data)
            data["elements"] = {}
            data["file"] = experiment.get_public_logs()
            data["docker"] = ListModuleSerializer(experiment.docker).data
            data["experiments"] = [str(i.id) for i in experiment.docker.experiments.filter(
                user=self.request.user, state__in=['executed', 'executing', 'error']).all()]
            print(experiment.user.id == self.request.user.id)
            data["owner"] = experiment.user.id == self.request.user.id

            for element in experiment.elements.all():
                if element.kind in data["elements"]:
                    data["elements"][element.kind].append(
                        element.get_public_path() if element.get_public_path() else element.value)
                else:
                    data["elements"][element.kind] = [
                        element.get_public_path() if element.get_public_path() else element.value]

            return Response(data)
        except ObjectDoesNotExist:
            return Response("Module not found", status=status.HTTP_404_NOT_FOUND)
