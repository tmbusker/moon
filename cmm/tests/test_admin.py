from django.contrib import admin
from django.forms import ValidationError
from cmm.admin import ActiveUserAdminSite, CmmAdminSiteMixin, SuperUserAdminSite, SuperUserAuthenticationForm
from cmm.tests.cmm_fixtures import *


class CustomAdminSite(CmmAdminSiteMixin, admin.AdminSite):
    pass


class TestCmmAdminSiteMixin:
    @pytest.mark.django_db
    def test_get_app_list(self, test_request):
        custom_admin_site = CustomAdminSite()
        custom_admin_site.register(AuthUser, AuthUserAdmin)
        applist = custom_admin_site.get_app_list(test_request)
        assert applist


class TestSuperUserAdminSite:
    @pytest.mark.django_db
    def test_get_app_list(self, test_request):
        custom_admin_site = SuperUserAdminSite()
        custom_admin_site.register(AuthUser, AuthUserAdmin)
        assert not custom_admin_site.has_permission(test_request)


class TestSuperUserAuthenticationForm:
    @pytest.mark.django_db
    def test_confirm_login_allowed(self):
        superuser = User.objects.create_superuser('testuser', 'test@example.com', 'testpassword')
        form = SuperUserAuthenticationForm()
        form.confirm_login_allowed(superuser)
        assert True

    @pytest.mark.django_db
    def test_confirm_login_allowed_non_super_user(self):
        regular_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        form = SuperUserAuthenticationForm()
        with pytest.raises(ValidationError) as excinfo:
            form.confirm_login_allowed(regular_user)

        # Confirm that the ValidationError was raised with the expected message
        assert str(excinfo.value)


class TestActiveUserAdminSite:
    @pytest.mark.django_db
    def test_get_app_list(self, test_request):
        custom_admin_site = ActiveUserAdminSite()
        custom_admin_site.register(AuthUser, AuthUserAdmin)
        assert custom_admin_site.has_permission(test_request)
