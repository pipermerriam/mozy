from django import forms

from mozy.apps.mosaic.models import (
    SourceImage,
    NormalizedSourceImage,
)


class SourceImageForm(forms.ModelForm):
    tile_size = forms.TypedChoiceField(
        coerce=int,
        choices=NormalizedSourceImage.TILE_SIZE_CHOICES, required=False,
    )

    class Meta:
        model = SourceImage
        fields = ('original', 'tile_size')

    def save(self, *args, **kwargs):
        instance = super(SourceImageForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('tile_size'):
            instance.create_mosaic_image(tile_size=self.cleaned_data['tile_size'])
        return instance


class NormalizedSourceImageForm(forms.ModelForm):
    class Meta:
        model = NormalizedSourceImage
        fields = ('tile_size',)
