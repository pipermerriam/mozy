# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from mozy.apps.mosaic import views


urlpatterns = patterns(
    '',
    url(
        r'^source-images/$', views.SourceImageListView.as_view(),
        name="sourceimage-list",
    ),
    url(
        r'^source-images/add-new-image/$', views.SourceImageCreateView.as_view(),
        name="sourceimage-create",
    ),
    url(
        r'^source-images/(?P<pk>\d+)/$', views.SourceImageDetailView.as_view(),
        name="sourceimage-detail",
    ),
    url(
        r'^source-images/(?P<pk>\d+)/create-mosaic/$',
        views.NormalizedSourceImageCreateView.as_view(),
        name="normalizedsourceimage-create",
    ),
    url(
        r'^mosaic-images/(?P<pk>\d+)/$', views.MosaicImageDetailView.as_view(),
        name="mosaicimage-detail",
    ),
    url(
        r'^mosaic-images/(?P<pk>\d+)/create-mosaic/$', views.MosaicImageCreateView.as_view(),
        name="mosaicimage-create",
    ),
    url(
        r'^stock-images/$', views.StockImageListView.as_view(),
        name="stockimage-list",
    ),
    url(
        r'^stock-images/(?P<pk>\d+)/$', views.StockImageDetailView.as_view(),
        name="stockimage-detail",
    ),
)
