from typing import Optional, Type
from django.db.models import Model
from django.db import connection


UNIQUE_CONSTRAINT = 'unique constraint'


def get_unique_constrains(model: Type[Model]) -> dict[str, list[str]]:
    unique_constraints = {}
    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, table_name=model._meta.db_table)
        for name, params in constraints.items():
            if params.get('unique') and not params.get('primary_key'):
                unique_constraints[name] = params.get('columns')
        return unique_constraints


def retrieve_by_unique_key(model_instance: Model, unique_fields: tuple[str, ...]) -> \
        Optional[Model]:
    """Uniqueキーで検索した結果"""
    return model_instance.__class__.objects.filter(**{k: getattr(model_instance, k)
                                                      for k in unique_fields}).first()  # type: ignore


def get_field_names(model_instance: Model) -> tuple[str, ...]:
    return tuple(field.name for field in model_instance._meta.get_fields())


def get_unique_constraint_name(error_message: str) -> Optional[str]:
    start_index = error_message.find(UNIQUE_CONSTRAINT)
    if start_index > -1:
        start_index = error_message.index('"', start_index + len(UNIQUE_CONSTRAINT)) + 1
        end_index = error_message.index('"', start_index)
        return error_message[start_index:end_index]
    else:
        return None
