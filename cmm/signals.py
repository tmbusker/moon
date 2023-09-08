from django.dispatch import receiver
from django_auth_ldap.backend import populate_user, LDAPBackend
from django.contrib.auth.signals import user_logged_in
import logging
from cmm.models import AuthUser


@receiver(populate_user, sender=LDAPBackend)
def ldap_auth_handler(user, ldap_user, **kwargs):
    """
    Implicitly connect signal handlers decorated with @receiver.
    LDAP連携情報に基づいて職員情報を更新する
    """
    email = ldap_user.attrs._data.get('email')[0]
    name = ldap_user.attrs._data.get('name')[0]
    auth_user, created = AuthUser.objects.get_or_create(email=email)
    if created:
        auth_user.name = name


def log_user_login(sender, user, request, **kwargs):
    """ユーザーのログインを記録する"""
    logging.info(f'User {user.username} logged in')


user_logged_in.connect(log_user_login)
