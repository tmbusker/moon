import pytest
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from cmm.csv import CsvModelAdmin
from cmm.models.models import AuthUser
from cmm.tests.csv.model_admin import AnotherAuthUserModelAdmin


@pytest.fixture
def instance(auth_user_admin) -> CsvModelAdmin:
    return CsvModelAdmin(auth_user_admin)


@pytest.fixture
def another_instance() -> CsvModelAdmin:
    admin_site = AdminSite()
    admin_site.register(AuthUser, AnotherAuthUserModelAdmin)
    another_auth_user_admin = admin_site._registry.get(AuthUser)
    return CsvModelAdmin(another_auth_user_admin)


@pytest.fixture
def fields():
    return ('logentry', 'id', 'password', 'last_login', 'is_superuser', 'username', 'first_name', 'last_name',
            'email', 'is_staff', 'is_active', 'date_joined', 'groups', 'user_permissions')


@pytest.mark.django_db
def test_model_admin(auth_user_admin, instance):
    assert instance.model_admin == auth_user_admin


def test_model_name(instance, another_instance):
    assert instance.model_name == _("authorization users")
    assert another_instance.model_name == _("authorization users")


def test_model_fields(instance, another_instance, fields):
    assert instance.model_fields == ('id', 'username')
    assert another_instance.model_fields == fields

    instance.model_fields = ('username', 'any')
    assert instance.model_fields == ('username', 'any')


def test_csv_headers(instance, another_instance, fields):
    assert instance.csv_headers == ('id', 'username')
    assert another_instance.csv_headers == fields

    instance.csv_headers = ('username', 'any', 'another')
    assert instance.csv_headers == ('username', 'any', 'another')
