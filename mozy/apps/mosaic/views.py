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
    normalize_source_image,
)
from mozy.apps.mosaic.forms import (
    SourceImageForm,
    MosaicImageForm,
)
from mozy.apps.mosaic.tables import (
    StockImageTable,
    SourceImageTable,
)


class SourceImageListView(SingleTableMixin, ListView):
    template_name = 'mosaic/sourceimage_create.html'
    model = SourceImage
    form_class = SourceImageForm
    table_class = SourceImageTable
    table_pagination = {'per_page': 10}

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
        source_image = SourceImage.objects.get(**self.kwargs)
        instance = source_image.create_mosaic_image(**form.cleaned_data)

        url = redirect(reverse('mosaicimage-detail', kwargs={'pk': instance.pk}))
        import ipdb; ipdb.set_trace()
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
