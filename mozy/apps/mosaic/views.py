from django.shortcuts import (
    redirect,
    get_object_or_404,
)
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
    NormalizedSourceImageForm,
)
from mozy.apps.mosaic.tables import (
    StockImageTable,
)


class SourceImageListView(ListView):
    template_name = 'mosaic/sourceimage_list.html'
    model = SourceImage
    form_class = SourceImageForm
    context_object_name = 'source_images'
    paginate_by = 36


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


class NormalizedSourceImageCreateView(CreateView):
    model = NormalizedSourceImage
    template_name = 'mosaic/normalizedsourceimage_create.html'
    form_class = NormalizedSourceImageForm

    def get_source_image(self):
        return get_object_or_404(SourceImage, **self.kwargs)

    def get_context_data(self, **kwargs):
        context = super(NormalizedSourceImageCreateView, self).get_context_data(**kwargs)
        context['source_image'] = self.get_source_image()
        return context

    def form_valid(self, form):
        source_image = self.get_source_image()
        instance = source_image.create_normalize_image(**form.cleaned_data)
        # TODO: this cannot happen like this.  it's slow
        from mozy.apps.mosaic import matcher
        matcher.create_mosaic(instance)

        return redirect(reverse('normalizedsourceimage-detail', kwargs={'pk': instance.pk}))


class NormalizedSourceImageDetailView(DetailView):
    model = NormalizedSourceImage
    template_name = 'mosaic/normalizedsourceimage_detail.html'
    context_object_name = 'normalized_source_image'


class MosaicImageCreateView(CreateView):
    model = MosaicImage
    template_name = 'mosaic/mosaicimage_create.html'
    context_object_name = 'mosaic_image'


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
