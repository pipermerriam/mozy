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
    NormalizedSourceImage,
    MosaicImage,
    NormalizedStockImage,
)
from mozy.apps.mosaic.forms import (
    SourceImageForm,
)
from mozy.apps.mosaic.tables import (
    StockImageTable,
)


class NormalizedSourceImageListView(ListView):
    template_name = 'mosaic/image_list.html'
    model = NormalizedSourceImage
    form_class = SourceImageForm
    context_object_name = 'images'
    paginate_by = 36


class SourceImageCreateView(CreateView):
    template_name = 'mosaic/image_create.html'
    model = SourceImage
    form_class = SourceImageForm

    def get_success_url(self):
        return reverse('image-detail', kwargs={'pk': self.object.pk})


class NormalizedSourceImageDetailView(DetailView):
    template_name = 'mosaic/image_detail.html'
    model = NormalizedSourceImage
    context_object_name = 'image'


class MosaicImageDetailView(DetailView):
    model = MosaicImage
    template_name = 'mosaic/mosaic_detail.html'
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
