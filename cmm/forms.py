from typing import Dict, Set
from django.forms import ModelForm
from django.contrib.admin.utils import flatten


def get_modelform_error_codes(modelform: ModelForm) -> Set[str]:
    """ModelFormのエラーコード一覧"""
    return {e.code for errorlist in modelform.errors.values() for e in errorlist.as_data()}


def get_modelform_error_messages(modelform: ModelForm) -> Dict[str, list[str]]:
    """ModelFormのエラーメッセージ一覧"""
    return {field: flatten([e.messages for e in errorlist.as_data()]) for field, errorlist in modelform.errors.items()}


def get_modelform_non_unique_error_codes(modelform: ModelForm) -> Set[str]:
    """Unique constraint違反以外のModelFormのエラーコード"""
    return get_modelform_error_codes(modelform).difference({'unique', 'unique_together'})
