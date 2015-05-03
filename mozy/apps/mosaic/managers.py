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
