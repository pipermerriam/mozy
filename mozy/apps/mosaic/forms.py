from django import forms

from mozy.apps.mosaic.models import (
    SourceImage,
    MosaicImage,
)


class SourceImageForm(forms.ModelForm):
    class Meta:
        model = SourceImage
        fields = ('original',)


class MosaicImageForm(forms.ModelForm):
    class Meta:
        model = MosaicImage
        fields = ('tile_size',)
