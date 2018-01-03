class EntityError(Exception):
    """
    Возникает, когда количество фишек у позиции меньше 0.
      Сигнализирует о невозможности перехода
    """
    pass


class Entity:
    _FIELDS = []

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return '{}({})'.format(__class__.__name__,
                                ', '.join("{}='{}'".format(name, getattr(self, name)) for name in self._FIELDS))

    __str__ =  __repr__

class Position(Entity):
    _FIELDS = ['name', 'points']

    def __init__(self, name: str, points: int = 0):
        """
        :param name: имя точки
        :param points: количество фишек
        """
        super().__init__(name)
        self._points = points

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, count):
        self._points = count
        if count < 0:
            raise EntityError("Attempt to sub {} points from '{}' point violates zero points constraint".format(count, self.name))

    def __str__(self):
        return '{}: {}'.format(self.name, self.points)


class Transition(Entity):
    """
    :param name: имя перехода
    """
    _FIELDS = ['name']

    def __init__(self, name: str):
        super().__init__(name)
