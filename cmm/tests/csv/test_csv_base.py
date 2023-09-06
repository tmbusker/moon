import pytest
import csv
from cmm.csv import CsvBase, CsvEncoding, LogLocation


@pytest.fixture
def instance() -> CsvBase:
    return CsvBase()


def test_encoding(instance: CsvBase):
    assert instance.encoding == CsvEncoding.UTF8

    instance.encoding = CsvEncoding.SJIS
    assert instance.encoding == CsvEncoding.SJIS


def test_dialect(instance: CsvBase):
    assert instance.dialect == csv.excel

    instance.dialect = csv.excel_tab
    assert instance.dialect == csv.excel_tab


def test_file_extension(instance: CsvBase):
    assert instance.file_extension == '.csv'

    instance.file_extension = '.txt'


def test_date_format(instance: CsvBase):
    assert instance.date_format == '%Y/%m/%d'

    instance.date_format = '%Y-%m-%d'
    assert instance.date_format == '%Y-%m-%d'


def test_log_location(instance: CsvBase):
    assert instance.log_location == LogLocation.FILE

    instance.log_location = LogLocation.CONSOLE
    assert instance.log_location == LogLocation.CONSOLE


def test_chunk_size(instance: CsvBase):
    assert instance.chunk_size == 1000

    instance.chunk_size = 2000
    assert instance.chunk_size == 2000


def test_data_type(instance):
    assert instance.encoding == CsvEncoding.UTF8


def test_chunk_size_negative(instance):
    with pytest.raises(ValueError):
        instance.chunk_size = -10
