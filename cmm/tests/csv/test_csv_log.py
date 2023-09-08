import pytest
import json
from django.contrib.admin import AdminSite
from django.test import RequestFactory
from cmm.csv import CsvLog, CsvLogModelAdmin


@pytest.fixture
def csv_log() -> CsvLog:
    return CsvLog()


def test_convert_content2json(csv_log):
    # Set up some test data
    test_data = {'key1': 'value1', 'key2': 'value2'}
    csv_log.row_content = test_data
    result = csv_log.convert_content2json().row_content

    # Verify that the result is a JSON string
    assert isinstance(result, str)

    # Verify that the JSON string can be converted back to the original data
    assert json.loads(result) == test_data


def test_convert_content2dict(csv_log):
    # Set up some test data
    test_data = {'key1': 'value1', 'key2': 'value2'}
    json_data = json.dumps(test_data)

    csv_log.row_content = json_data
    result = csv_log.convert_content2dict().row_content

    # Verify that the result is a dictionary
    assert isinstance(result, dict)

    # Verify that the dictionary is the same as the original data
    assert result == test_data


def test_convert_content2values(csv_log):
    # Set up some test data
    test_data = {'key1': 'value1', 'key2': 'value2'}
    json_data = json.dumps(test_data)

    csv_log.row_content = json_data
    result = csv_log.convert_content2values().row_content

    # Verify that the result is a list
    assert isinstance(result, list)

    # Verify that the list contains the expected values
    assert 'value1' in result
    assert 'value2' in result


def test_has_no_add_permission():
    admin_site = AdminSite()
    admin_site.register(CsvLog, CsvLogModelAdmin)
    csv_log_model_admin = admin_site._registry.get(CsvLog)

    request_factory = RequestFactory()
    request = request_factory.get('/')

    assert csv_log_model_admin.has_add_permission(request) is False
