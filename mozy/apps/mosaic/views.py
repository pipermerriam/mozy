from django.core.urlresolvers import (
    reverse,
)
from django.views.generic import (
    CreateView,
    DetailView,
)

from mozy.apps.mosaic.models import SourceImage
from mozy.apps.mosaic.forms import (
    SourceImageForm,
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
