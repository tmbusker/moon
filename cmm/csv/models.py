import json
from typing import Any, List
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from cmm.models import SimpleTable


class CsvLog(SimpleTable):
    """
    CSVアップロード、ダウンロードログのデータ定義
    """

    INFO = 'info'           # 正常インポート
    WARN = 'warn'           # 読み飛ばし
    ERROR = 'error'         # 読み込みエラー

    LEVEL_CHOICES = [
        (INFO, _('Information')),
        (WARN, _('Warning')),
        (ERROR, _('Error')),
    ]

    UPLOAD = 'upload'
    DOWNLOAD = 'download'

    TYPE_CHOICES = [
        (UPLOAD, _('Csv Upload')),
        (DOWNLOAD, _('Csv Download')),
    ]

    INSERT = 'insert'
    UPDATE = 'update'

    EDIT_CHOICES = [
        (INSERT, _('insert')),
        (UPDATE, _('update')),
    ]

    """CSV upload, downloadのログ情報"""
    log_level = models.CharField(_('csv log level'), max_length=5, choices=LEVEL_CHOICES, blank=False, default=INFO)
    log_type = models.CharField(_('csv log type'), max_length=12, choices=TYPE_CHOICES, blank=False, default=UPLOAD)
    edit_type = models.CharField(_('csv edit type'), max_length=12, choices=EDIT_CHOICES, blank=False, default=INSERT)
    file_name = models.CharField(_('file name'), max_length=120, blank=True, null=True)
    row_no = models.IntegerField(_('row no'), blank=True, null=True)
    row_content = models.TextField(_('row content'), blank=True, null=True)
    message = models.CharField(_('message'), max_length=2048, blank=True, null=True)
    creator = models.CharField(_('creator'), max_length=120, blank=True, null=True)
    created_at = models.DateTimeField(_('create time'), blank=True, null=True, default=timezone.now)
    lot_number = models.CharField(_('lot number'), max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'cmm_csv_log'
        verbose_name = _('csv log')
        verbose_name_plural = _('csv logs')
        default_permissions: List[str] = []

        ordering = ['-created_at']

    def convert_content2json(self) -> str:
        """json型に変換する"""
        self.row_content = json.dumps(self.row_content, ensure_ascii=False)
        return self

    def convert_content2dict(self) -> dict[str, Any]:
        """dict型に変換する"""
        self.row_content = json.loads(self.row_content)
        return self

    def convert_content2values(self) -> list[Any]:
        """dict型に変換する"""
        self.row_content = list(json.loads(self.row_content).values())
        return self
