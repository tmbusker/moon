import pytest
import csv
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from cmm.csv import CsvBase, CsvEncoding, CsvLogOutput, CsvLog
from cmm.tests.cmm_fixtures import *


class CsvBaseTestAdmin(CsvBase, admin.ModelAdmin):
    """for test"""


@pytest.fixture
def csv_base(test_admin_site) -> CsvBase:
    test_admin_site.register(CsvLog, CsvBaseTestAdmin)
    return test_admin_site._registry.get(CsvLog)


def test_initial_values(csv_base: CsvBase):
    assert CsvBase.chunk_size == 1000
    assert CsvBase.encoding == CsvEncoding.UTF8
    assert CsvBase.dialect == csv.excel
    assert CsvBase.csv_extension == '.csv'
    assert CsvBase.excel_extension == '.xlsx'
    assert CsvBase.date_format == '%Y/%m/%d'
    assert CsvBase.log_output == CsvLogOutput.DATABASE

    assert csv_base.chunk_size == 1000
    assert csv_base.chunk_size == 1000
    assert csv_base.chunk_size == 1000
    assert csv_base.encoding == CsvEncoding.UTF8
    assert csv_base.dialect == csv.excel
    assert csv_base.csv_extension == '.csv'
    assert csv_base.excel_extension == '.xlsx'
    assert csv_base.date_format == '%Y/%m/%d'
    assert csv_base.log_output == CsvLogOutput.DATABASE


def test_model_name(csv_base: CsvBase):
    assert _('csv logs') == csv_base.model_name


def test_csv_file_name(csv_base: CsvBase):
    assert csv_base.get_csv_file_name() == _('csv logs') + '.csv'


def test_excel_file_name(csv_base: CsvBase):
    assert csv_base.get_excel_file_name() == _('csv logs') + '.xlsx'


def test_csv_content_type(csv_base: CsvBase):
    assert csv_base.get_csv_content_type() == 'text/csv; charset=utf8'


def test_model_fields(csv_base: CsvBase):
    field_names = [f for f in csv_base.get_model_fields().keys()]
    field_types = [f for f in csv_base.get_model_fields().values()]
    assert field_names == ['id', 'version', 'created_at', 'creator', 'updated_at', 'updater', 'valid_flag',
                           'log_level', 'log_type', 'edit_type', 'file_name', 'row_no', 'row_content', 'message',
                           'lot_number']
    assert field_types == ['BigAutoField', 'IntegerField', 'DateTimeField', 'CharField', 'DateTimeField', 'CharField',
                           'BooleanField', 'CharField', 'CharField', 'CharField', 'CharField', 'IntegerField',
                           'TextField', 'CharField', 'CharField']


def test_csv_field_names(csv_base: CsvBase):
    assert csv_base.get_csv_field_names() == ['log_level', 'log_type', 'edit_type', 'file_name', 'row_no',
                                              'row_content', 'message', 'lot_number']


def test_csv_headers(csv_base: CsvBase):
    assert csv_base.get_csv_headers() == ['log_level', 'log_type', 'edit_type', 'file_name', 'row_no',
                                          'row_content', 'message', 'lot_number']

    csv_base.csv_headers = ['log_level', 'log_type', 'edit_type', 'file_name', 'row_no']
    assert csv_base.get_csv_headers() == ['log_level', 'log_type', 'edit_type', 'file_name', 'row_no']


@pytest.mark.django_db
def test_generate_csv_data(auth_user_admin, query_set):
    auth_user_admin.chunk_size = 2
    csv_data = list(auth_user_admin.generate_csv_data(query_set))
    assert len(csv_data) == 5
    for row in csv_data:
        assert row[5] == '2023/09/23 03:00:00'
