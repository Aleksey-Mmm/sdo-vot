from examapp.models import Upload
from django import forms
from .models import *

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ('description', 'document', )
        labels = {'description': 'Имя файла', 'document': 'Файл'}
