# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from mozy.apps.mosaic import views


urlpatterns = patterns(
    '',
    url(
        r'^source-image/$', views.SourceImageListView.as_view(),
        name="sourceimage-list",
    ),
    url(
        r'^source-image/add-new-image/$', views.SourceImageCreateView.as_view(),
        name="sourceimage-create",
    ),
    url(
        r'^source-image/(?P<pk>\d+)/$', views.SourceImageDetailView.as_view(),
        name="sourceimage-detail",
    ),
    url(
        r'^source-image/(?P<pk>\d+)/create-mosaic-image/$',
        views.MosaicImageCreateView.as_view(),
        name="mosaicimage-create",
    ),
    url(
        r'^mosaic-image/(?P<pk>\d+)/$', views.MosaicImageDetailView.as_view(),
        name="mosaicimage-detail",
    ),
    url(
        r'^stock-image/$', views.StockImageListView.as_view(),
        name="stockimage-list",
    ),
    url(
        r'^stock-image/(?P<pk>\d+)/$', views.StockImageDetailView.as_view(),
        name="stockimage-detail",
    ),
)
