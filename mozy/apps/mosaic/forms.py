from django import forms

from mozy.apps.mosaic.models import (
    SourceImage,
    MosaicImage,
)


class SourceImageForm(forms.ModelForm):
    tile_size = forms.TypedChoiceField(
        coerce=int,
        choices=MosaicImage.TILE_SIZE_CHOICES, required=False,
    )

    class Meta:
        model = SourceImage
        fields = ('original', 'tile_size')

    def save(self, *args, **kwargs):
        instance = super(SourceImageForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('tile_size'):
            instance.create_mosaic_image(tile_size=self.cleaned_data['tile_size'])
        return instance


class MosaicImageForm(forms.ModelForm):
    class Meta:
        model = MosaicImage
        fields = ('tile_size',)
