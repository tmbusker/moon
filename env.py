import os


def set_env():
    os.environ.setdefault('DEVELOPMENT', 'True')
    os.environ.setdefault('SECRET_KEY', 'django-insecure-%(dkfxmq46r$mryz#80q)i6&(r=e9w&4hk_lvy@416$7)hjl!1')

    # LDAP設定
    os.environ.setdefault('AUTH_LDAP_SERVER_URI', 'ldap://192.168.20.103:389/')
    os.environ.setdefault('AUTH_LDAP_BIND_DN', 'CN=Auth user,OU=tokyo,DC=tokyo,DC=scientia,DC=co,DC=jp')
    os.environ.setdefault('AUTH_LDAP_BIND_PASSWORD', 'p09olp09ol')


if __name__ == "__main__":
    set_env()
