import pytest
from datetime import date
from django.contrib.admin import AdminSite, ModelAdmin
from django.utils.translation import gettext_lazy as _
from cmm.csv import CsvLog, CsvLogModelAdmin, CsvModelAdminDownloader, ExcelModelAdminDownloader
from cmm.tests.csv.models import QuerySet


@pytest.fixture
def csv_log_model_admin() -> ModelAdmin:
    admin_site = AdminSite()
    admin_site.register(CsvLog, CsvLogModelAdmin)
    return admin_site._registry.get(CsvLog)


@pytest.fixture
def csv_instance(csv_log_model_admin) -> CsvModelAdminDownloader:
    return CsvModelAdminDownloader(csv_log_model_admin)


@pytest.fixture
def excel_instance(csv_log_model_admin) -> ExcelModelAdminDownloader:
    return ExcelModelAdminDownloader(csv_log_model_admin)


@pytest.fixture
def queryset() -> QuerySet:
    return QuerySet([
        {'name': 'Alice', 'date_of_birth': date(1990, 1, 1)},
        {'name': 'Bob', 'date_of_birth': date(1995, 5, 5)},
    ])


def test_get_file_name(csv_instance):
    assert csv_instance.get_file_name() == _('csv logs') + '.csv'
    assert csv_instance.get_file_name() == 'CSVログ.csv'


def test_get_content_type(csv_instance):
    assert csv_instance.get_content_type() == 'text/csv; charset=utf8'


def test_csv_downloader_generateResponse(csv_instance, queryset):
    csv_instance.model_fields = ('name', 'date_of_birth')
    csv_instance.csv_headers = ('Name', 'Date of Birth')
    csv_response = csv_instance.generateResponse(queryset)

    assert csv_instance.get_file_name() == 'CSVログ.csv'
    assert csv_response.content == b'Name,Date of Birth\r\nAlice,1990/01/01\r\nBob,1995/05/05\r\n'
    assert csv_response.status_code == 200


def test_excel_downloader(excel_instance, queryset):
    excel_instance.model_fields = ('name', 'date_of_birth')
    excel_instance.csv_headers = ('Name', 'Date of Birth')
    excel_response = excel_instance.generateResponse(queryset)

    # assert excel_instance.get_file_name() == _('csv logs') + '.xlsx'
    assert excel_instance.get_file_name() == 'CSVログ.xlsx'
    assert excel_instance.get_content_type() == 'application/vnd.ms-excel'
    assert excel_response.status_code == 200
