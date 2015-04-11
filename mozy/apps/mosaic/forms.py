from django import forms

from mozy.apps.mosaic.models import SourceImage


class SourceImageForm(forms.ModelForm):
    class Meta:
        model = SourceImage
        fields = ('original',)
