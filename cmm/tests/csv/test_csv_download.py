import pytest
from django.utils.translation import gettext_lazy as _
from cmm.csv import download_csv, DOWNLOAD_CSV, download_excel, DOWNLOAD_EXCEL
from cmm.tests.cmm_fixtures import *


class TestCsvDownloadMixin:
    @pytest.mark.django_db
    def test_get_actions(self, auth_user_admin, test_request):
        assert DOWNLOAD_CSV in auth_user_admin.get_actions(test_request)

    @pytest.mark.django_db
    def test_get_actions_without_permissions(self, auth_user_admin, test_request):
        content_type = ContentType.objects.get_for_model(User)
        csv_permission = Permission.objects.get(codename='download_csv_authuser', content_type=content_type)
        test_request.user.user_permissions.remove(csv_permission)
        assert DOWNLOAD_CSV not in auth_user_admin.get_actions(test_request)

    @pytest.mark.django_db
    def test_generate_csv_response(self, auth_user_admin, query_set):
        download_response = auth_user_admin.generate_csv_response(query_set)

        csv_content = b'User Name,Password,Email,First Name,Last Name,Date Joined\r\n'
        csv_content += b'tester1,password,test1@test.com,first,last,2023/09/23 03:00:00\r\n'
        csv_content += b'tester2,password,test2@test.com,first,last,2023/09/23 03:00:00\r\n'
        csv_content += b'tester3,password,test3@test.com,first,last,2023/09/23 03:00:00\r\n'
        csv_content += b'tester4,password,test4@test.com,first,last,2023/09/23 03:00:00\r\n'
        csv_content += b'tester5,password,test5@test.com,first,last,2023/09/23 03:00:00\r\n'
        assert download_response.content == csv_content
        assert download_response.status_code == 200


@pytest.mark.django_db
def test_download_csv(auth_user_admin, test_request, query_set):
    download_response = download_csv(auth_user_admin, test_request, query_set)

    csv_content = b'User Name,Password,Email,First Name,Last Name,Date Joined\r\n'
    csv_content += b'tester1,password,test1@test.com,first,last,2023/09/23 03:00:00\r\n'
    csv_content += b'tester2,password,test2@test.com,first,last,2023/09/23 03:00:00\r\n'
    csv_content += b'tester3,password,test3@test.com,first,last,2023/09/23 03:00:00\r\n'
    csv_content += b'tester4,password,test4@test.com,first,last,2023/09/23 03:00:00\r\n'
    csv_content += b'tester5,password,test5@test.com,first,last,2023/09/23 03:00:00\r\n'
    assert download_response.content == csv_content
    assert download_response.status_code == 200


class TestExcelDownloadMixin:
    @pytest.mark.django_db
    def test_get_actions(self, auth_user_admin, test_request):
        assert DOWNLOAD_EXCEL in auth_user_admin.get_actions(test_request)

    @pytest.mark.django_db
    def test_get_actions_without_permissions(self, auth_user_admin, test_request):
        content_type = ContentType.objects.get_for_model(User)
        excel_permission = Permission.objects.get(codename='download_excel_authuser', content_type=content_type)
        test_request.user.user_permissions.remove(excel_permission)
        assert DOWNLOAD_EXCEL not in auth_user_admin.get_actions(test_request)

    @pytest.mark.django_db
    def test_generate_excel_response(self, auth_user_admin, query_set):
        download_response = auth_user_admin.generate_excel_response(query_set)
        assert download_response.status_code == 200


@pytest.mark.django_db
def test_download_excel(auth_user_admin, test_request, query_set):
    download_response = download_excel(auth_user_admin, test_request, query_set)
    assert download_response.status_code == 200
