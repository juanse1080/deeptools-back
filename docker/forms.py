from django import forms
from .models import Docker, Experiment

class UploadFileForm(forms.Form):
    # title = forms.CharField(max_length=50)
    file = forms.FileField()

class DockerForm(forms.ModelForm):
    lenguaje_choices = (
        ('python', 'Python'),
    )
    name = forms.CharField(max_length=100)
    img_name = forms.CharField(max_length=500)
    languaje = forms.ChoiceField(choices=lenguaje_choices)
    proto_path = forms.FileField()
    class Meta:
        model = Docker
        fields = [
            'name',
            'img_name',
            'languaje',
            'proto_path'
        ]

class ExperimentForm(forms.ModelForm):
    input_file = forms.FileField()
    class Meta:
        model = Experiment
        fields = ['input_file']


