# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from mozy.apps.mosaic import views


urlpatterns = patterns(
    '',
    url(
        r'^$', views.MosaicImageListView.as_view(),
        name="mosaicimage-list",
    ),
    url(
        r'^images/$', views.NormalizedSourceImageListView.as_view(),
        name="image-list",
    ),
    url(
        r'^images/add-new-image/$', views.SourceImageCreateView.as_view(),
        name="image-create",
    ),
    url(
        r'^images/(?P<pk>\d+)/$', views.NormalizedSourceImageDetailView.as_view(),
        name="image-detail",
    ),
    url(
        r'^mosaics/(?P<pk>\d+)/$', views.MosaicImageDetailView.as_view(),
        name="mosaicimage-detail",
    ),
    url(
        r'^mosaics/(?P<pk>\d+)/app/$', views.MosaicApplicationView.as_view(),
        name="mosaicimage-detail-app",
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
