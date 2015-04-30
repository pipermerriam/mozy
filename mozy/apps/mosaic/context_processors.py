from django.db.models import Q
from django.core.cache import cache

from mozy.apps.mosaic.models import SourceImageTile


def tile_metadata(request):
    last_updated = SourceImageTile.objects.order_by('updated_at').last()
    cache_key = "PENDING_TILE_COUNT_{0}".format(last_updated.updated_at.isoformat())
    value = cache.get(cache_key)
    if value is None:
        value = {
            'PENDING_TILE_COUNT': SourceImageTile.objects.filter(
                Q(status=SourceImageTile.STATUS_PENDING) |
                Q(status=SourceImageTile.STATUS_QUEUED) |
                Q(status=SourceImageTile.STATUS_MATCHING)
            ).count()
        }
        cache.set(cache_key, value)
    return value
