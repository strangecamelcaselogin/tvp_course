import re
from pprint import pprint
from collections import namedtuple

from typing import List, Union, Any, Dict, Tuple, TypeVar


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

    def __init__(self, name: str, points: int):
        """
        :param name: имя точки
        :param points: количество фишек
        """
        super().__init__(name)
        self.name = name
        self.points = points

    def __str__(self):
        return '{}: {}'.format(self.name, self.points)

    def add_points(self, count: int):
        self.points += count

    def sub_points(self, count: int):
        self.points = self.points - count
        if self.points < 0:
            raise EntityError("Attempt to sub {} points from '{}' point violates zero points constraint".format(count, self.name))


class Transition(Entity):
    """
    :param name: имя перехода
    """
    _FIELDS = ['name']
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name


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


class Parser:
    _Rule = namedtuple('Rule', ['l', 'r'])  # l - откуда связь, r - куда
    _PART_SPLITTER = re.compile(r'(\w+)\s*->\s*(.*)')  # для разделения правил на части
    _QUANTIFIER_SPLITTER = re.compile(r'(?:(\d+)\s*\*\s*)?(\w+\d+)')  # для обработки правой части правил (2*P1 3*P2 P4)

    @staticmethod
    def _fetch_positions(t: Transition, rules: List[_Rule]) -> Tuple[List[Any], List[Any]]:
        """
        Вычислить позиции входящих и выходящих точек из перехода
        rules:
            [Rule(l=Entity(name='T1'), r=[Entity(name='P1', points='0')]),
             Rule(l=Entity(name='P1', points='0'), r=[Entity(name='T2'), Entity(name='T4')]),
             Rule(l=Entity(name='T2'), r=[Entity(name='P1', points='0'), Entity(name='P1', points='0'), Entity(name='P2', points='0')]),
             Rule(l=Entity(name='P2', points='0'), r=[Entity(name='T3'), Entity(name='T4')]),
             Rule(l=Entity(name='T4'), r=[Entity(name='P3', points='0'), Entity(name='P4', points='0')])]
        """
        t_name = t.name.lower()  # имя перехода
        input_positions = []  # позиции, куда ведет переход
        output_positions = []  # позиции откуда исходит переход

        for l, r in rules:
            if l.name.lower() == t_name:  # если слева искомое имя перехода
                input_positions.extend(r)
            else:  # иначе посмотрим есть ли справа искомое имя перехода
                for r_ in r:
                    if r_.name.lower() == t_name:
                        output_positions.append(l)  # и если есть, то добавим

        return output_positions, input_positions

    def parse_rules(self, positions: List[Position], transitions: List[Transition], rules: List[Union[str, tuple]]) -> Dict[Transition, Tuple[List[Position], List[Position]]]:
        """
        Обработать входные правила

        transitions_to_positions:

          {Entity(name='T1'): ([], [Entity(name='P1', points='0')]),
           Entity(name='T2'): ([Entity(name='P1', points='0')],
                               [Entity(name='P1', points='0'),
                                Entity(name='P1', points='0'),
                                Entity(name='P2', points='0')]),
           Entity(name='T3'): ([Entity(name='P2', points='0')], []),
           Entity(name='T4'): ([Entity(name='P1', points='0'),
                                Entity(name='P2', points='0')],
                               [Entity(name='P3', points='0'),
                                Entity(name='P4', points='0')])}
        """
        transitions_to_positions = {}
        prepared_rules = []
        all_entities = positions + transitions

        for rule in rules:
            from_part, to_part = re.match(self._PART_SPLITTER, rule).groups()

            from_part = find_entity_by_name(all_entities, from_part)
            to_part = re.findall(self._QUANTIFIER_SPLITTER, to_part)

            processed_r = []
            for quantifier, entity_name in to_part:  # elem = ('2', 'P1)  # 2 * P1
                for _ in range(int(quantifier) if quantifier else 1):
                    processed_r.append(find_entity_by_name(all_entities, entity_name))

            prepared_rules.append(self._Rule(from_part, processed_r))  # прим. Rule(l='T2', r=('P1',)

        for t in transitions:  # доделаем, получим словарь соответсвия позиций переходам
            transitions_to_positions[t] = self._fetch_positions(t, prepared_rules)

        return transitions_to_positions


class PNet:
    def __init__(self, name: str, positions: List[Position], transitions: List[Transition], rules):
        self.name = name  # имя сети
        self.positions = positions
        self.transitions = transitions
        self.rules = Parser().parse_rules(positions, transitions, rules)

    def model(self, transition_chain: List[str]) -> List:
        """
        :param transition_chain: ['T1', 'T2]
        :return: bool
        """
        def print_state(msg):
            print(msg)
            for p in self.positions:
                print(p)
            print()

        results = []
        try:
            for idx, t_name in enumerate(transition_chain):
                print("\nStep {} - '{}'".format(idx + 1, t_name))

                transition = find_entity_by_name(self.transitions, t_name)
                from_positions, to_positions = self.rules[transition]

                for p in from_positions:
                    p.sub_points(1)  # Бросит исклбючение

                for p in to_positions:
                    p.add_points(1)

                results.append(t_name)
                print_state('State after step:')

        except EntityError as e:
            print_state('>>> Break: ' + str(e))

        return results

    def print(self):
        pprint({
            'name': self.name,
            'positions': self.positions,
            'transitions': self.transitions,
            'rules': self.rules
        })
        print('\n' * 3)


if __name__ == '__main__':
    pnet = PNet('Petri1',
                positions=[
                    Position('P1', 0),
                    Position('P2', 0),
                    Position('P3', 0),
                    Position('P4', 0)
                ],
                transitions=[
                    Transition('T1'),
                    Transition('T2'),
                    Transition('T3'),
                    Transition('T4'),
                ],
                rules=[
                    'T1 -> P1',
                    'P1 -> T2 T4',
                    'T2 -> 2*P1 P2',
                    'P2 -> T3 T4',
                    'T4 -> P3 P4'
                ])

    pnet.print()

    path = ['T1', 'T2', 'T2', 'T2']
    print('Target path: ', path)

    result = pnet.model(path)

    if result:
        print('Executed transitions: ', ' -> '.join(result))
    else:
        print('>>> None of transitions were executed')
