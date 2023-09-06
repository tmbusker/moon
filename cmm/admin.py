from wsgiref.simple_server import WSGIRequestHandler
from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CmmAdminSiteMixin:
    """AdminSiteのカスタマイズ"""
    enable_nav_sidebar = True
    _empty_value_display = '-'

    def get_app_list(self, request: WSGIRequestHandler, app_label=None):
        """Sidebarに表示する内容をカスタマイズ"""
        applist = super().get_app_list(request, app_label)      # type: ignore

        return applist


class SuperUserAuthenticationForm(AdminAuthenticationForm):
    """Only superuser is available."""
    error_messages = {
        **AdminAuthenticationForm.error_messages,
        'invalid_login': _(
            "Please enter the correct %(username)s and password for a superuser "
            "account. Note that both fields may be case-sensitive."
        ),
    }
    required_css_class = 'required'

    def confirm_login_allowed(self, user):
        """Override AuthenticationForm.confirm_login_allowed to only allow superuser to login."""
        if not user.is_superuser:
            raise ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )
        super().confirm_login_allowed(user)


class SuperUserAdminSite(CmmAdminSiteMixin, admin.AdminSite):
    """Only superuser is available."""
    login_form = SuperUserAuthenticationForm

    def has_permission(self, request):
        """Give permission to superuser only."""
        return request.user.is_superuser


class ActiveUserAdminSite(CmmAdminSiteMixin, admin.AdminSite):
    """All active users are available."""

    login_form = AuthenticationForm

    def has_permission(self, request):
        """Give permission to any active user."""
        return request.user.is_active
