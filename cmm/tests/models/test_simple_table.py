import pytest
from django.utils import timezone
from cmm.csv import CsvLog


@pytest.mark.django_db
def test_save():
    csv_log = CsvLog(valid_flag=True, log_level='info', log_type='upload', edit_type='insert', updater='pytest')  # noqa
    csv_log.save()
    assert csv_log.creator == csv_log.updater
    assert csv_log.created_at.date() == timezone.now().date()
    assert csv_log.updated_at.date() == timezone.now().date()
