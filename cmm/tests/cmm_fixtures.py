import pytest
from pytz import timezone
from datetime import datetime
from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest
from django.test import RequestFactory
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from cmm.csv import (CsvDownloadMixin, ExcelDownloadMixin, CsvUploadMixin, CsvLog,
                     download_csv, DOWNLOAD_CSV, download_excel, DOWNLOAD_EXCEL)
from cmm.models import AuthUser

time_zone = timezone(settings.TIME_ZONE)
User = get_user_model()


class AuthUserAdmin(CsvDownloadMixin, ExcelDownloadMixin, CsvUploadMixin, UserAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    csv_headers = ('User Name', 'Password', 'Email', 'First Name', 'Last Name', 'Date Joined')

    def get_csv_field_names(self):
        return ("username", "password", "email", "first_name", "last_name", "date_joined")


class CsvLogAdmin(CsvDownloadMixin, ExcelDownloadMixin, CsvUploadMixin, UserAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    csv_headers = ('log_level', 'file_name', 'row_no')

    def get_csv_field_names(self):
        return ('log_level', 'file_name', 'row_no')


@pytest.fixture
def test_admin_site():
    return admin.AdminSite()


@pytest.fixture
def auth_user_admin(test_admin_site):
    test_admin_site.register(AuthUser, AuthUserAdmin)
    test_admin_site.add_action(download_csv, DOWNLOAD_CSV)
    test_admin_site.add_action(download_excel, DOWNLOAD_EXCEL)
    return test_admin_site._registry.get(AuthUser)


@pytest.fixture
def csv_log_admin(test_admin_site):
    test_admin_site.register(CsvLog, CsvLogAdmin)
    return test_admin_site._registry.get(CsvLog)


@pytest.fixture
def test_request() -> HttpRequest:
    factory = RequestFactory()
    request = factory.get('/admin/cmm/authuser/')
    user = AuthUser.objects.create_user(
        username='py_tester',
        password='your_password',
        email='your_email@example.com',
        first_name='First',
        last_name='Last',
    )

    content_type = ContentType.objects.get_for_model(User)
    download_csv_user_permission = Permission.objects.get(codename='download_csv_authuser', content_type=content_type)
    download_excel_user_permission = Permission.objects.get(codename='download_excel_authuser', content_type=content_type)  # noqa: E501
    upload_csv_user_permission = Permission.objects.get(codename='upload_csv_authuser', content_type=content_type)
    view_user_permission = Permission.objects.get(codename='view_authuser', content_type=content_type)
    user.user_permissions.add(download_csv_user_permission, download_excel_user_permission, upload_csv_user_permission, view_user_permission)  # noqa: E501
    user.save()
    request.user = user
    return request


@pytest.fixture
def query_set():
    # noqa
    data = [{'username': 'tester1', 'password': 'password', 'email': 'test1@test.com', 'first_name': 'first', 'last_name': 'last', 'date_joined': '2023-09-23 12:00:00+0900'},  # noqa: E501
            {'username': 'tester2', 'password': 'password', 'email': 'test2@test.com', 'first_name': 'first', 'last_name': 'last', 'date_joined': '2023-09-23 12:00:00+0900'},  # noqa: E501
            {'username': 'tester3', 'password': 'password', 'email': 'test3@test.com', 'first_name': 'first', 'last_name': 'last', 'date_joined': '2023-09-23 12:00:00+0900'},  # noqa: E501
            {'username': 'tester4', 'password': 'password', 'email': 'test4@test.com', 'first_name': 'first', 'last_name': 'last', 'date_joined': '2023-09-23 12:00:00+0900'},  # noqa: E501
            {'username': 'tester5', 'password': 'password', 'email': 'test5@test.com', 'first_name': 'first', 'last_name': 'last', 'date_joined': '2023-09-23 12:00:00+0900'}]  # noqa: E501
    last_login = time_zone.localize(datetime(2023, 9, 16, 12, 0, 0))
    for row in data:
        user = AuthUser.objects.create(**row)
        user.last_login = last_login
        user.save()
    return AuthUser.objects.filter(username__startswith='tester').order_by('username')
