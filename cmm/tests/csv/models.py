from typing import Any


class QuerySet:
    def __init__(self, data: list[dict[str, Any]]):
        self.data = data

    def values(self, *fields):
        result = []
        for item in self.data:
            row = {}
            for field in fields:
                row[field] = item.get(field)
            result.append(row)
        return result

    def values_list(self, *fields):
        result = []
        for item in self.data:
            result.append(item.values())
        return result
