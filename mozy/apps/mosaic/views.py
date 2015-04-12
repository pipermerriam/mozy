from PIL import Image

from django.shortcuts import redirect
from django.core.urlresolvers import (
    reverse,
)
from django.views.generic import (
    CreateView,
    DetailView,
)

from mozy.apps.mosaic.models import (
    SourceImage,
    MosaicImage,
    MosaicTile,
)
from mozy.apps.mosaic.utils import (
    decompose_an_image,
    normalize_an_image,
)
from mozy.apps.mosaic.forms import (
    SourceImageForm,
    MosaicImageForm,
)


class SourceImageCreateView(CreateView):
    template_name = 'mosaic/sourceimage_create.html'
    model = SourceImage
    form_class = SourceImageForm

    def get_success_url(self):
        return reverse('sourceimage-detail', kwargs={'pk': self.object.pk})


class SourceImageDetailView(DetailView):
    template_name = 'mosaic/sourceimage_detail.html'
    model = SourceImage
    context_object_name = 'source_image'


class MosaicImageCreateView(CreateView):
    model = MosaicImage
    template_name = 'mosaic/mosaicimage_create.html'
    form_class = MosaicImageForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.source_image = SourceImage.objects.get(**self.kwargs)
        normalized_image = normalize_an_image(Image.open(instance.source_image.original.file))
        instance.populate_image(normalized_image)
        instance.save()

        tile_data = decompose_an_image(
            Image.open(instance.image.file),
            tile_size=instance.tile_size,
        )

        for box_coords, tile_image in tile_data.items():
            tile = MosaicTile(
                main_image=instance,
                upper_left_x=box_coords[0],
                upper_left_y=box_coords[1],
            )
            tile.populate_tile(tile_image)
            tile.save()
        return redirect(reverse('mosaicimage-detail', kwargs={'pk': instance.pk}))


class MosaicImageDetailView(DetailView):
    model = MosaicImage
    template_name = 'mosaic/mosaicimage_detail.html'
    context_object_name = 'mosaic_image'
