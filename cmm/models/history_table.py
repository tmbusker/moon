from datetime import datetime
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class HistoryTable(models.Model):
    """共通ベーステーブル"""
    history = HistoricalRecords(inherit=True, )
    __history_date: datetime = timezone.now()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self._history_date = timezone.now()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        self._history_date = timezone.now()
        super().delete(*args, **kwargs)

    @property
    def _history_date(self) -> datetime:
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value: datetime):
        self.__history_date = value
