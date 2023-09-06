import logging
from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _
from cmm.models import VersionedTable


_logger = logging.getLogger(__name__)


class SimpleTable(VersionedTable, models.Model):
    """作成日付、作成者、更新日時と更新者をもつテーブルのベースクラス"""
    created_at = models.DateTimeField(_('create time'), blank=True, null=True, editable=False)
    creator = models.CharField(_('creator'), max_length=120, blank=True, editable=False, null=True)
    updated_at = models.DateTimeField(_('update time'), blank=True, null=True, editable=False)
    updater = models.CharField(_('updater'), max_length=120, blank=True, editable=False, null=True)
    valid_flag = models.BooleanField(_('valid'), blank=False, null=False, default=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.updated_at is None:
            self.updated_at = timezone.now()
        if not self.creator:
            self.creator = self.updater
        if self.created_at is None:
            self.created_at = self.updated_at

        super().save(*args, **kwargs)
