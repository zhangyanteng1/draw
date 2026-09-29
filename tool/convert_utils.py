from typing import TypeVar, Type

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def orm_list_to_schema(orm_list: list, schema_cls: Type[T]) -> list[T]:
    return [schema_cls.model_validate(item) for item in orm_list]
