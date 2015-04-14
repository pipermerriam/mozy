from django import forms

from mozy.apps.mosaic.models import (
    SourceImage,
    NormalizedSourceImage,
)


class SourceImageForm(forms.ModelForm):
    tile_size = forms.TypedChoiceField(
        coerce=int,
        choices=NormalizedSourceImage.TILE_SIZE_CHOICES, required=False,
        initial=NormalizedSourceImage.TILE_SIZE_CHOICES[0][0],
    )

    class Meta:
        model = SourceImage
        fields = ('original', 'tile_size')

    def save(self, *args, **kwargs):
        instance = super(SourceImageForm, self).save(*args, **kwargs)
        normalized_image = instance.create_normalize_image(
            tile_size=self.cleaned_data['tile_size'],
        )
        # TODO: this cannot happen like this.  it's slow
        from mozy.apps.mosaic import matcher
        matcher.create_mosaic(normalized_image)
        return instance


class NormalizedSourceImageForm(forms.ModelForm):
    class Meta:
        model = NormalizedSourceImage
        fields = ('tile_size',)
