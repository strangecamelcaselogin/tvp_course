from typing import TypeVar, List

from entities import Position,  Transition

class EntitySearchError(Exception):
    """
    Возникает, если сущность с указанным имененм не существует
    """
    pass


T = TypeVar('T', Position, Transition)
def find_entity_by_name(entities: List[T], name: str) -> T:
    for e in entities:
        if e.name == name:
            return e

    raise EntitySearchError("Can not find Entity: '{}'".format(name))