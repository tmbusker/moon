import pytest
from django.contrib.admin import AdminSite, ModelAdmin
from cmm.csv import download_csv, DOWNLOAD_CSV, download_excel, DOWNLOAD_EXCEL
from cmm.models.models import AuthUser
from cmm.tests.csv.model_admin import AuthUserModelAdmin


@pytest.fixture
def auth_user_admin() -> ModelAdmin:
    # Create an instance of the admin site
    site = AdminSite()

    # Create an instance of the model admin
    model_admin = AuthUserModelAdmin(AuthUser, site)

    return model_admin
