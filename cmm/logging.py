from logging import Filter
import logging
import threading


local = threading.local()


class LoggingRequestAttributesMiddleware:
    """IPアドレスとログインユーザー名を取得する"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # username
        try:
            username = request.user.username if request.user else None
            setattr(local, 'log_username', username)
        except AttributeError:
            ...

        # remote ip address, reverse proxyが使用されている場合、REMOTE_ADDRはproxyサーバーのIPアドレスになる
        ip_address = request.META.get('REMOTE_ADDR')
        if request.META.get('HTTP_X_FORWARDED_FOR') is not None:
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR')[0]
        setattr(local, 'log_ip_address', ip_address)

        # session key
        try:
            setattr(local, 'log_session_key', request.session.session_key)
        except AttributeError:
            ...

        response = self.get_response(request)

        # clear attributes on response
        # setattr(local, 'log_username', None)
        # setattr(local, 'log_ip_address', None)
        # setattr(local, 'log_session_key', None)

        return response


class LoggingRequestAttributesFilter(Filter):
    """IPアドレスとログインユーザー名を取得する"""
    def filter(self, record):
        record.username = getattr(local, 'log_username', None)
        record.ip_address = getattr(local, 'log_ip_address', None)
        record.session_key = getattr(local, 'log_session_key', None)

        return True


def log_decorator(func):
    def wrapper(*args, **kwargs):
        logging.info(f'{func.__name__} was called with parameter {args}, {kwargs}')
        return func(*args, **kwargs)
    return wrapper
