import uuid

from PIL import Image

from django.shortcuts import redirect
from django.core.urlresolvers import (
    reverse,
)
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
)

from django_tables2 import (
    SingleTableMixin,
)

from mozy.apps.mosaic.models import (
    SourceImage,
    MosaicImage,
    NormalizedStockImage,
)
from mozy.apps.mosaic.utils import (
    convert_image_to_django_file,
    normalize_an_image,
)
from mozy.apps.mosaic.forms import (
    SourceImageForm,
    MosaicImageForm,
)
from mozy.apps.mosaic.tables import (
    StockImageTable,
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
        with instance.source_image.original.file as fp:
            o_im = Image.open(fp)
            normalized_image = normalize_an_image(o_im)
            instance.image.save(
                "{0}.png".format(str(uuid.uuid4())),
                convert_image_to_django_file(normalized_image),
                save=True,
            )

        return redirect(reverse('mosaicimage-detail', kwargs={'pk': instance.pk}))


class MosaicImageDetailView(DetailView):
    model = MosaicImage
    template_name = 'mosaic/mosaicimage_detail.html'
    context_object_name = 'mosaic_image'


class StockImageListView(SingleTableMixin, ListView):
    model = NormalizedStockImage
    template_name = 'mosaic/stockimage_list.html'
    context_object_name = 'stock_images'
    table_class = StockImageTable
    table_pagination = {'per_page': 50}


class StockImageDetailView(DetailView):
    model = NormalizedStockImage
    template_name = 'mosaic/stockimage_detail.html'
    context_object_name = 'stock_image'
