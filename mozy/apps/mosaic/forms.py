from django import forms

from mozy.apps.mosaic.models import (
    SourceImage,
)


class SourceImageForm(forms.ModelForm):
    class Meta:
        model = SourceImage
        fields = (
            'original',
        )

    def save(self, *args, **kwargs):
        instance = super(SourceImageForm, self).save(*args, **kwargs)
        return instance.create_normalize_image()
