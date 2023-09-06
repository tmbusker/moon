import copy
from typing import Any
from django.forms import ModelForm
import pytest
from io import StringIO, BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from cmm.csv import CsvUploader, CsvLog


@pytest.fixture
def csv_uploader(auth_user_admin):
    return CsvUploader(auth_user_admin)


def get_row_content(content: list[str]) -> dict[str, Any]:
    csv_headers = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    return dict(zip(csv_headers, content))


@pytest.fixture
def csv_log():
    return CsvLog(log_level=CsvLog.INFO,
                  log_type=CsvLog.UPLOAD,
                  edit_type=CsvLog.INSERT,
                  file_name='test.csv',
                  row_no=1,
                  row_content=get_row_content(['test', 'test@hotmail.com', 'Jenny', 'Black', 'True']),
                  message='',
                  creator='tester',
                  created_at=None,
                  lot_number=742483279723849)


@pytest.mark.django_db
def test_header_row_number(csv_uploader):
    assert csv_uploader.header_row_number == 1

    csv_uploader.header_row_number = 0

    assert csv_uploader.header_row_number == 0
    with pytest.raises(ValueError):
        csv_uploader.header_row_number = -1


@pytest.mark.django_db
def test_error_tolerance_rate(csv_uploader):
    assert csv_uploader.error_tolerance_rate == 10

    csv_uploader.error_tolerance_rate = 0
    assert csv_uploader.error_tolerance_rate == 0

    csv_uploader.error_tolerance_rate = 100
    assert csv_uploader.error_tolerance_rate == 100

    # test invalid value

    with pytest.raises(ValueError):
        csv_uploader.error_tolerance_rate = -1

    with pytest.raises(ValueError):
        csv_uploader.error_tolerance_rate = 101


@pytest.mark.django_db
def test_default_values(csv_uploader):
    assert csv_uploader.default_values == {}


@pytest.mark.django_db
def test_is_overwrite_existing(csv_uploader):
    assert csv_uploader.is_overwrite_existing is True


@pytest.mark.django_db
def test_unique_constraints(csv_uploader):
    assert ['username'] in csv_uploader.unique_constraints.values()


@pytest.mark.django_db
def test_csv2model(csv_uploader):
    assert csv_uploader.model_fields == ('id', 'username')

    csv_uploader.default_values = {'value': 'somevalue', 'another': 'another'}
    csv_data = {'username': 'John', 'age': '30'}
    expected_result = csv_uploader.default_values | {'username': 'John'}
    assert csv_uploader.csv2model(csv_data) == expected_result

    csv_data = {'name': 'John', 'age': '30'}
    assert csv_uploader.csv2model(csv_data) == csv_uploader.default_values

    csv_uploader.default_values = {}
    csv_data = {'username': 'John', 'age': '30'}
    assert csv_uploader.csv2model(csv_data) == {'username': 'John'}


@pytest.mark.django_db
def test_get_modelform_class(csv_uploader):
    model_form_class = csv_uploader._CsvUploader__get_modelform_class()
    assert issubclass(model_form_class, ModelForm)


@pytest.mark.django_db
def test_validate_by_modelform_valid(csv_uploader, csv_log):
    csv_uploader._CsvUploader__validate_by_modelform(csv_log)
    assert csv_log.log_level == CsvLog.INFO


@pytest.mark.django_db
def test_validate_by_modelform_invalid_unique_violation_overwrite(csv_uploader, csv_log):
    csv_uploader.is_overwrite_existing = True
    csv_log.row_content = get_row_content(['admin', 'test@hotmail.com', 'Jenny', 'Black', 'True'])
    csv_uploader._CsvUploader__validate_by_modelform(csv_log)

    assert csv_log.log_level == CsvLog.INFO
    assert csv_log.message == _("Update existing row.")


@pytest.mark.django_db
def test_validate_by_modelform_invalid_unique_violation_skip(csv_uploader, csv_log):
    csv_uploader.is_overwrite_existing = False
    csv_log.row_content = get_row_content(['admin', 'test@hotmail.com', 'Jenny', 'Black', 'True'])
    csv_uploader._CsvUploader__validate_by_modelform(csv_log)

    assert csv_log.log_level == CsvLog.WARN


@pytest.mark.django_db
def test_validate_by_modelform_invalid_none_unique_violation(csv_uploader, csv_log):
    csv_log.row_content = get_row_content(['', 'test@hotmail.com', 'Jenny', 'Black', 'True'])
    csv_uploader._CsvUploader__validate_by_modelform(csv_log)

    assert csv_log.log_level == CsvLog.ERROR


@pytest.mark.django_db
def test_has_too_many_errors(csv_uploader):
    assert csv_uploader.chunk_size == 1000
    assert csv_uploader.error_tolerance_rate == 10
    assert csv_uploader._CsvUploader__has_too_many_errors(101)
    assert not csv_uploader._CsvUploader__has_too_many_errors(100)


@pytest.mark.django_db
def test_save_valid(csv_uploader, csv_log):
    chunk = []
    csv_uploader._CsvUploader__validate_by_modelform(csv_log)
    chunk.append(csv_log)
    assert csv_uploader._CsvUploader__save(chunk) == 1


@pytest.mark.django_db
def test_save_invalid(csv_uploader, csv_log):
    chunk = []
    csv_log.row_content = get_row_content(['', 'test@hotmail.com', 'Jenny', 'Black', 'True'])
    csv_uploader._CsvUploader__validate_by_modelform(csv_log)
    chunk.append(csv_log)
    assert csv_uploader._CsvUploader__save(chunk) == 0


@pytest.mark.django_db
def test_save_update_database(csv_uploader, csv_log):
    csv_uploader.is_overwrite_existing = True
    chunk = []
    csv_log.row_content = get_row_content(['admin', 'test@hotmail.com', 'Jenny', 'Black', 'True'])
    csv_uploader._CsvUploader__validate_by_modelform(csv_log)
    chunk.append(csv_log)

    assert csv_uploader._CsvUploader__save(chunk) == 1


@pytest.mark.django_db
def test_save_skip_to_update_database(csv_uploader, csv_log):
    csv_uploader.is_overwrite_existing = False
    chunk = []
    csv_log.row_content = get_row_content(['admin', 'test@hotmail.com', 'Jenny', 'Black', 'True'])
    csv_uploader._CsvUploader__validate_by_modelform(csv_log)
    chunk.append(csv_log)

    assert csv_uploader._CsvUploader__save(chunk) == 0


@pytest.mark.django_db
def test_save_update_duplicated_inside_chunk(csv_uploader, csv_log):
    csv_uploader.is_overwrite_existing = True
    chunk = []

    csv_uploader._CsvUploader__validate_by_modelform(csv_log)
    chunk.append(csv_log)
    copied = copy.deepcopy(csv_log)
    csv_uploader._CsvUploader__validate_by_modelform(copied)
    chunk.append(copied)

    assert csv_uploader._CsvUploader__save(chunk) == 2


@pytest.mark.django_db
def test_save_skip_duplicated_inside_chunk(csv_uploader, csv_log):
    csv_uploader.is_overwrite_existing = False
    chunk = []

    csv_uploader._CsvUploader__validate_by_modelform(csv_log)
    chunk.append(csv_log)
    copied = copy.deepcopy(csv_log)
    csv_uploader._CsvUploader__validate_by_modelform(copied)
    chunk.append(copied)

    assert csv_uploader._CsvUploader__save(chunk) == 1


@pytest.mark.django_db
def test_read_csv_file(csv_uploader):
    csv_uploader.csv_headers = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    csv_data = "username,email,first_name,last_name,is_staff,\ntest,test@hotmail.com,Jenny,Black,True"
    csv_file = StringIO(csv_data)
    byte_buffer = BytesIO(csv_file.getvalue().encode())
    byte_buffer.name = 'test.csv'
    row_no, lot_number = csv_uploader.read_csv_file(byte_buffer, 'test')

    assert row_no == 2


@pytest.mark.django_db
def test_read_csv_file_chunk_size(csv_uploader):
    csv_uploader.chunk_size = 1
    csv_uploader.csv_headers = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    csv_data = "username,email,first_name,last_name,is_staff,\ntest,test@hotmail.com,Jenny,Black,True"
    csv_file = StringIO(csv_data)
    byte_buffer = BytesIO(csv_file.getvalue().encode())
    byte_buffer.name = 'test.csv'
    row_no, lot_number = csv_uploader.read_csv_file(byte_buffer, 'test')

    assert row_no == 2


@pytest.mark.django_db
def test_read_csv_file_has_too_many_errors(csv_uploader):
    csv_uploader.chunk_size = 1
    csv_uploader.csv_headers = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    csv_data = "username,email,first_name,last_name,is_staff,\n,test@hotmail.com,Jenny,Black,True"
    csv_file = StringIO(csv_data)
    byte_buffer = BytesIO(csv_file.getvalue().encode())
    byte_buffer.name = 'test.csv'
    row_no, lot_number = csv_uploader.read_csv_file(byte_buffer, 'test')

    assert csv_uploader._CsvUploader__has_too_many_errors


def test_none():
    pass
