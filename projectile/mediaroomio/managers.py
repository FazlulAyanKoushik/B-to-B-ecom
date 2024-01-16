

from django.db import models

from .choices import MediaImageKind


class MediaImageQuerySet(models.QuerySet):

    def get_kind_editable(self):
        kind = [
            MediaImageKind.IMAGE,
            MediaImageKind.VIDEO
        ]
        return self.filter(kind__in=kind)
