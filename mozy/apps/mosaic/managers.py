from django.utils import timezone
from django.db.models import Q
from django.db.models.query import QuerySet


MAX_TILE_PROCESSING_TIME = timezone.timedelta(minutes=10)


class SourceTileQuerySet(QuerySet):
    MAX_TILE_PROCESSING_TIME = MAX_TILE_PROCESSING_TIME

    @classmethod
    def get_timout(cls):
        return timezone.now() - cls.MAX_TILE_PROCESSING_TIME

    def processing(self):
        return self.filter(
            stock_tile_match__isnull=True,
            task_lock__isnull=False,
            updated_at__gt=self.get_timout(),
        )

    def unmatched(self):
        """
        - task_lock is None
          stock_tile_match is None
        - task_lock is not None
          stock_tile_match is None
          updated_at less than (10 minutes ago)
        """
        timeout = timezone.now() - MAX_TILE_PROCESSING_TIME
        return self.filter(
            Q(
                stock_tile_match__isnull=True,
                task_lock__isnull=True
            ) | Q(
                stock_tile_match__isnull=True,
                task_lock__isnull=False,
                updated_at__lte=timeout,
            )
        )


MAX_MOSAIC_COMPOSITION_TIME = timezone.timedelta(minutes=30)


class NormalizedSourceImageQuerySet(QuerySet):
    MAX_MOSAIC_COMPOSITION_TIME = MAX_MOSAIC_COMPOSITION_TIME

    @classmethod
    def get_timeout(cls):
        return timezone.now() - cls.MAX_MOSAIC_COMPOSITION_TIME

    def composing(self):
        timeout = self.get_timeout()
        return self.exclude(
            mosaic_images__isnull=False,
        ).filter(
            task_lock__isnull=False,
            updated_at__gt=timeout,
        )

    def without_mosaic(self):
        return self.filter(
            mosaic_images__isnull=True,
        ).exclude(
            tiles__stock_tile_match__isnull=True,
        )

    def ready_for_mosaic(self):
        """
        - has no mosaic
          all tiles are matched
          not locked
        """
        timeout = self.get_timeout()
        return self.filter(
            Q(
                task_lock__isnull=True
            ) | Q(
                task_lock__isnull=False,
                updated_at__lte=timeout,
            ),
            Q(mosaic_images__isnull=True),
        ).exclude(
            tiles__stock_tile_match__isnull=True,
        )
