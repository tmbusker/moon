import pytest
import copy
from datetime import datetime, date
from io import StringIO, BytesIO
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.test import Client
from cmm.csv import UploadMixin, CsvLog
from cmm.csv.csv_base import CsvBase
from cmm.models import AuthUser
from cmm.tests.cmm_fixtures import *
from cmm.tests.csv.csv_fixtures import *


@pytest.fixture
def auth_user_dict():
    return {'password': 'password',
            'username': 'tester1',
            'last_name': '姓',
            'first_name': '名',
            'email': 'tester@test.com',
            'is_superuser': False,
            'is_staff': False,
            'is_active': False,
            'date_joined': '2023/09/23 12:00:00'
            }


@pytest.fixture
def auth_user_csv_log(auth_user_dict):
    return CsvLog(file_name='test.csv', row_no=1, row_content=auth_user_dict)


@pytest.fixture
def csv_file():
    csv_data = "User Name,Password,Email,First Name,Last Name,Joined Date\n"
    csv_data += "test1,password,test1@hotmail.com,Jenny,Black,2023/09/23 12:00:00\n"
    csv_data += "test2,password,test2@hotmail.com,Jenny,Black,2023/09/23 12:00:00"
    csv_file = StringIO(csv_data)
    byte_buffer = BytesIO(csv_file.getvalue().encode())
    byte_buffer.name = 'test.csv'
    return byte_buffer


class TestUploadMixin:
    def test_initial_values(self, auth_user_admin):
        assert auth_user_admin.upload_template == 'cmm/csv_upload.html'

    @pytest.mark.django_db
    def test_has_upload_csv_permission(self, auth_user_admin, test_request):
        assert auth_user_admin.has_upload_csv_permission(test_request)

    @pytest.mark.django_db
    def test_changelist_view(self, auth_user_admin, test_request):
        view = auth_user_admin.changelist_view(test_request, None)
        assert view.status_code == 200

    def test_get_urls(self, auth_user_admin):
        urls = auth_user_admin.get_urls()
        assert urls[0].name == 'cmm_authuser_csv_upload'

    def test_abstract_read_csv_file(self, auth_user_admin, csv_file):
        with pytest.raises(NotImplementedError) as error:
            UploadMixin.read_csv_file(auth_user_admin, csv_file, 'py_tester')
            assert str(error.value) == "Subclasses must implement my_abstract_method"

    @pytest.mark.django_db
    def test_upload_action_without_permission(self, auth_user_admin, test_request):
        content_type = ContentType.objects.get_for_model(User)
        csv_permission = Permission.objects.get(codename='upload_csv_authuser', content_type=content_type)
        test_request.user.user_permissions.remove(csv_permission)

        with pytest.raises(PermissionDenied) as error:
            auth_user_admin.upload_action(test_request)
            assert str(error.value)

    @pytest.mark.django_db
    def test_upload_action_get(self, auth_user_admin, test_request):
        auth_user_admin.upload_action(test_request)
        assert True

    @pytest.mark.django_db
    def test_upload_action_post(self, auth_user_admin, test_request, csv_file):
        test_request.method = "POST"
        # The FILES attribute of a Django WSGIRequest object is read-only, so we cannot continue the pytest
        # test_request.FILES = {'upload_files': csv_file}
        auth_user_admin.upload_action(test_request)
        assert True

    @pytest.mark.django_db
    def test_upload_action_client(self, test_request, csv_file):
        """単体テストのcoverageに反映されない、upload_actionのカバー率は71%止まり"""
        client = Client()
        login_successful = client.login(username=test_request.user.username, password='your_password')
        assert login_successful
        response = client.post(reverse('admin:cmm_authuser_csv_upload'), {'upload_file': csv_file})

        # Check if the response is a redirect to the changelist page (successful upload)
        assert response.status_code == 302
        assert reverse('admin:cmm_authuser_changelist') in response.url


class TestCsvUploadMixin:
    def test_initial_values(self, auth_user_admin):
        assert auth_user_admin.header_row_number == 1
        assert auth_user_admin.error_tolerance_rate == 10
        assert auth_user_admin.is_overwrite_existing

    def test_get_default_values(self, auth_user_admin):
        assert auth_user_admin.get_default_values() == {}

    @pytest.mark.django_db
    def test_csv2model_auth_user(self, auth_user_admin, auth_user_dict):
        auth_user_dict['last_login'] = '2023/09/23 12:00:00'
        auth_user_dict['unrelated'] = 'item name which not in the model fields'
        model_dict = auth_user_admin.csv2model(auth_user_dict)
        assert model_dict['password'] == auth_user_dict['password']
        assert model_dict['username'] == auth_user_dict['username']
        assert model_dict['is_superuser'] == auth_user_dict['is_superuser']
        assert model_dict['last_login'] == datetime.strptime(auth_user_dict['last_login'], auth_user_admin.datetime_format)
        assert 'unrelated' not in model_dict.keys()
        assert 'updater' not in model_dict.keys()

    def test_csv2model_csv_log(self, csv_log_admin):
        csv_dict = {'log_level': 'info', 'file_name': 'test.csv', 'row_no': 1}
        csv_dict['unrelated'] = 'item name which not in the model fields'
        csv_log_admin.user_name = 'py_tester'
        model_dict = csv_log_admin.csv2model(csv_dict)
        assert model_dict['log_level'] == csv_dict['log_level']
        assert model_dict['file_name'] == csv_dict['file_name']
        assert model_dict['row_no'] == csv_dict['row_no']
        assert 'unrelated' not in model_dict.keys()
        assert model_dict['updater'] == 'py_tester'

    def test_csv2model_date_field(self, csv_log_admin):
        def get_model_fields_modified(self):
            dict = {}
            dict['log_level'] = 'CharField'
            dict['row_no'] = 'IntegerField'
            dict['recorded'] = 'DateField'
            return dict

        csv_log_admin.get_model_fields = get_model_fields_modified.__get__(csv_log_admin, CsvBase)

        csv_dict = {'log_level': 'info', 'file_name': 'test.csv', 'row_no': 1}
        csv_dict['recorded'] = '2023/09/23'
        csv_log_admin.user_name = 'py_tester'
        model_dict = csv_log_admin.csv2model(csv_dict)
        assert model_dict['log_level'] == csv_dict['log_level']
        assert model_dict['row_no'] == csv_dict['row_no']
        assert model_dict['recorded'] == date(2023, 9, 23)
        assert 'file_name' not in model_dict.keys()
        assert model_dict['updater'] == 'py_tester'

    def test_get_modelform_class(self, auth_user_admin):
        model_form_class = auth_user_admin._CsvUploadMixin__get_modelform_class()
        assert issubclass(model_form_class, ModelForm)

    @pytest.mark.django_db
    def test_validate_by_modelform_valid(self, auth_user_admin, auth_user_csv_log):
        auth_user_admin._CsvUploadMixin__validate_by_modelform(auth_user_csv_log)
        assert auth_user_csv_log.log_level == CsvLog.INFO
        assert auth_user_csv_log.modelform.cleaned_data
        assert auth_user_csv_log.message == _('Newly imported row.')

    @pytest.mark.django_db
    def test_validate_by_modelform_invalid_unique_violation_overwrite(self, auth_user_admin, auth_user_csv_log):
        auth_user_content = auth_user_csv_log.row_content.copy()
        auth_user_content['date_joined'] = datetime(2023, 9, 23, 12, 0, 0)
        auth_user = AuthUser.objects.create_user(**auth_user_content)
        auth_user.save()

        auth_user_admin.is_overwrite_existing = True
        auth_user_admin._CsvUploadMixin__validate_by_modelform(auth_user_csv_log)
        assert auth_user_csv_log.log_level == CsvLog.INFO
        assert auth_user_csv_log.message == _("Update existing row.")

    @pytest.mark.django_db
    def test_validate_by_modelform_invalid_unique_violation_skip(self, auth_user_admin, auth_user_csv_log):
        auth_user_content = auth_user_csv_log.row_content.copy()
        auth_user_content['date_joined'] = datetime(2023, 9, 23, 12, 0, 0)
        auth_user = AuthUser.objects.create_user(**auth_user_content)
        auth_user.save()

        auth_user_admin.is_overwrite_existing = False
        auth_user_admin._CsvUploadMixin__validate_by_modelform(auth_user_csv_log)

        assert auth_user_csv_log.log_level == CsvLog.WARN

    @pytest.mark.django_db
    def test_validate_by_modelform_invalid_none_unique_violation(self, auth_user_admin, auth_user_csv_log):
        auth_user_csv_log.row_content = {'username': '', 'email': 'test@hotmail.com'}
        auth_user_admin._CsvUploadMixin__validate_by_modelform(auth_user_csv_log)
        assert auth_user_csv_log.log_level == CsvLog.ERROR

    @pytest.mark.django_db
    def test_has_too_many_errors(self, auth_user_admin):
        assert auth_user_admin.chunk_size == 1000
        assert auth_user_admin.error_tolerance_rate == 10
        assert auth_user_admin._CsvUploadMixin__has_too_many_errors(101)
        assert not auth_user_admin._CsvUploadMixin__has_too_many_errors(100)

    @pytest.mark.django_db
    def test_save_valid(self, auth_user_admin, auth_user_csv_log):
        chunk = []
        auth_user_admin._CsvUploadMixin__validate_by_modelform(auth_user_csv_log)
        chunk.append(auth_user_csv_log)
        assert auth_user_admin._CsvUploadMixin__save(chunk) == 1

    @pytest.mark.django_db
    def test_save_invalid(self, auth_user_admin, auth_user_csv_log):
        chunk = []
        auth_user_csv_log.row_content = {'username': '', 'email': 'test@hotmail.com'}
        auth_user_admin._CsvUploadMixin__validate_by_modelform(auth_user_csv_log)
        chunk.append(auth_user_csv_log)
        assert auth_user_admin._CsvUploadMixin__save(chunk) == 0

    @pytest.mark.django_db
    def test_save_update_database(self, auth_user_admin, auth_user_csv_log):
        auth_user_content = auth_user_csv_log.row_content.copy()
        auth_user_content['date_joined'] = datetime(2023, 9, 23, 12, 0, 0)
        auth_user = AuthUser.objects.create(**auth_user_content)
        auth_user.save()

        auth_user_admin.is_overwrite_existing = True
        chunk = []
        auth_user_admin._CsvUploadMixin__validate_by_modelform(auth_user_csv_log)
        chunk.append(auth_user_csv_log)

        assert auth_user_csv_log.log_level == CsvLog.INFO
        assert auth_user_csv_log.message == _("Update existing row.")
        assert auth_user_admin._CsvUploadMixin__save(chunk) == 1
        assert auth_user_csv_log.log_level == CsvLog.INFO

    @pytest.mark.django_db
    def test_save_skip_to_update_database(self, auth_user_admin, auth_user_csv_log):
        auth_user_content = auth_user_csv_log.row_content.copy()
        auth_user_content['date_joined'] = datetime(2023, 9, 23, 12, 0, 0)
        auth_user = AuthUser.objects.create_user(**auth_user_content)
        auth_user.save()

        auth_user_admin.is_overwrite_existing = False
        chunk = []
        auth_user_admin._CsvUploadMixin__validate_by_modelform(auth_user_csv_log)
        chunk.append(auth_user_csv_log)

        assert auth_user_csv_log.log_level == CsvLog.WARN
        assert auth_user_admin._CsvUploadMixin__save(chunk) == 0
        assert auth_user_csv_log.log_level == CsvLog.WARN

    @pytest.mark.django_db
    def test_save_update_duplicated_inside_chunk(self, auth_user_admin, auth_user_csv_log):
        auth_user_admin.is_overwrite_existing = True
        chunk = []

        auth_user_admin._CsvUploadMixin__validate_by_modelform(auth_user_csv_log)
        chunk.append(auth_user_csv_log)
        copied = copy.deepcopy(auth_user_csv_log)
        copied.row_no = auth_user_csv_log.row_no + 1
        auth_user_admin._CsvUploadMixin__validate_by_modelform(copied)
        chunk.append(copied)

        assert auth_user_admin._CsvUploadMixin__save(chunk) == 2

    @pytest.mark.django_db
    def test_save_skip_duplicated_inside_chunk(self, auth_user_admin, auth_user_csv_log):
        auth_user_admin.is_overwrite_existing = False
        chunk = []

        auth_user_admin._CsvUploadMixin__validate_by_modelform(auth_user_csv_log)
        chunk.append(auth_user_csv_log)
        copied = copy.deepcopy(auth_user_csv_log)
        copied.row_no = auth_user_csv_log.row_no + 1
        auth_user_admin._CsvUploadMixin__validate_by_modelform(copied)
        chunk.append(copied)

        assert auth_user_admin._CsvUploadMixin__save(chunk) == 1

    @pytest.mark.django_db
    def test_read_csv_file(self, auth_user_admin, csv_file):
        auth_user_admin.csv_file = csv_file
        auth_user_admin.user_name = 'login_user'
        auth_user_admin.lot_number = 'test_lot_number'
        row_no = auth_user_admin.read_csv_file()

        assert row_no == 3

    @pytest.mark.django_db
    def test_read_csv_file_chunk_size(self, auth_user_admin, csv_file):
        auth_user_admin.chunk_size = 1

        auth_user_admin.csv_file = csv_file
        auth_user_admin.user_name = 'login_user'
        auth_user_admin.lot_number = 'test_lot_number'
        row_no = auth_user_admin.read_csv_file()

        assert row_no == 3

    @pytest.mark.django_db
    def test_read_csv_file_has_too_many_errors(self, auth_user_admin):
        auth_user_admin.chunk_size = 10

        assert not auth_user_admin._CsvUploadMixin__has_too_many_errors(1)
        assert auth_user_admin._CsvUploadMixin__has_too_many_errors(2)

    @pytest.mark.django_db
    def test_read_csv_file_error_break(self, auth_user_admin):
        auth_user_admin.chunk_size = 1
        csv_data = "User Name,Password,Email,First Name,Last Name,Joined Date\n"
        csv_data += ",password,test1@hotmail.com,Jenny,Black,2023/09/23 12:00:00\n"
        csv_data += ",password,test2@hotmail.com,Jenny,Black,2023/09/23 12:00:00"
        csv_file = StringIO(csv_data)
        byte_buffer = BytesIO(csv_file.getvalue().encode())
        byte_buffer.name = 'test.csv'

        auth_user_admin.csv_file = byte_buffer
        auth_user_admin.user_name = 'login_user'
        auth_user_admin.lot_number = 'test_lot_number'
        row_no = auth_user_admin.read_csv_file()

        assert row_no == 2
