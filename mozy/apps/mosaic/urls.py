# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from mozy.apps.mosaic import views


urlpatterns = patterns(
    '',
    url(
        r'^source-image/$', views.SourceImageCreateView.as_view(),
        name="sourceimage-create",
    ),
    url(
        r'^source-image/(?P<pk>\d+)/$', views.SourceImageDetailView.as_view(),
        name="sourceimage-detail",
    ),
)
