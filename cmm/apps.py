from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CmmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cmm'
    verbose_name = _('cmm')

    def ready(self):
        from .signals import ldap_auth_handler
        from django_auth_ldap.backend import populate_user
        # Explicitly connect a signal handler.
        populate_user.connect(ldap_auth_handler)
