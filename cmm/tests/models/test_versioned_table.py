import pytest
import copy
from django.utils import timezone
from django.core.exceptions import ValidationError
from cmm.csv import CsvLog


@pytest.mark.django_db
def test_save():
    csv_log = CsvLog(valid_flag=True, log_level='info', log_type='upload', edit_type='insert', updater='pytest')  # noqa
    csv_log.save()
    assert csv_log.version == 1
    csv_log.save()
    assert csv_log.version == 2


@pytest.mark.django_db
def test_save_race_condition():
    """楽観排他"""
    csv_log = CsvLog(valid_flag=True, log_level='info', log_type='upload', edit_type='insert', updater='pytest')  # noqa
    csv_log.save()
    copied = copy.deepcopy(csv_log)
    csv_log.save()
    with pytest.raises(ValidationError) as error:
        copied.save()
        assert error.code == 'race_condition'
