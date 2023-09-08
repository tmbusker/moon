from typing import Optional, Type, Tuple
from django.db.models import Model
from django.db import connection


UNIQUE_CONSTRAINT = 'unique constraint'


def get_unique_constraint(model: Type[Model]) -> dict[str, list[str]]:
    unique_constraints = {}
    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, table_name=model._meta.db_table)
        for name, params in constraints.items():
            if params.get('unique') and not params.get('primary_key'):
                unique_constraints[name] = params.get('columns')
        return unique_constraints


def retrieve_by_unique_key(model_instance: Model, unique_fields: Optional[Tuple[str, ...]] = None) -> \
        Optional[Model]:
    """Uniqueキーで検索した結果"""
    if not unique_fields:
        unique_constraints = get_unique_constraint(model_instance.__class__)
        if len(unique_constraints) > 0:
            (_, unique_fields), *_ = unique_constraints.items()
        else:
            return None     # pragma: no cover
    return model_instance.__class__.objects.filter(**{k: getattr(model_instance, k)
                                                      for k in unique_fields}).first()  # type: ignore
