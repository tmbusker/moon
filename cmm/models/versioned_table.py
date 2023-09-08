from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from cmm.models import retrieve_by_unique_key


class VersionedTable(models.Model):
    """楽観的排他用のversionカラムを持つテーブル"""
    version = models.IntegerField(_("version"), blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Unique keyがない場合は排他処理を行わない"""
        if not self.version:
            self.version = 1
        else:
            current_db_record = retrieve_by_unique_key(self)
            if current_db_record and current_db_record.version:
                if self.version == current_db_record.version:
                    self.version += 1
                else:
                    raise ValidationError(
                        _('Race condition was detected. Confirm the content and try again later.'),
                        code='race_condition',
                        params=None
                    )
            else:
                self.version = 1        # pragma: no cover

        super().save(*args, **kwargs)
