import re
from pprint import pprint
from collections import namedtuple

from typing import List, Union, Any, Dict, Tuple, TypeVar

# l - откуда связь, куда, кратность дуги
Rule = namedtuple('Rule', ['l', 'r', 'q'])


class PointError(Exception):
    """
    Возникает, когда количество фишек у позиции меньше 0.
      Сигнализирует о невозможности перехода
    """
    pass


class EntityError(Exception):
    """

    """
    pass


class Entity:
    def __init__(self, name: str):
        self.name = name


class Position(Entity):
    def __init__(self, name: str, points: int):
        """
        :param name: имя точки
        :param points: количество фишек
        """
        super().__init__(name)
        self.name = name
        self.points = points

    def add_points(self, count: int):
        self.points += count

    def sub_points(self, count: int):
        self.points = self.points - count
        if self.points < 0:
            raise PointError()

    def __str__(self):
        return '{}(name={}, points={})'.format(__class__.__name__, self.name, self.points)

    def __repr__(self):
        return '{}(name={}, points={})'.format(__class__.__name__, self.name, self.points)


class Transition(Entity):
    """
    :param name: имя перехода
    """
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name

    def __str__(self):
        return '{}(name={})'.format(__class__.__name__, self.name)

    def __repr__(self):
        return '{}(name={})'.format(__class__.__name__, self.name)


T = TypeVar('T', Position, Transition)
def find_entity_by_name(entities: List[T], name: str) -> T:
    for e in entities:
        if e.name == name:
            return e

    raise EntityError()


def fetch_positions(t: Transition, rules: List[Rule]) -> Tuple[List[Any], List[Any]]:
    """
    Вычислить позиции входящих и выходящих точек из перехода
    rules:
        [Rule(l='P1', r=('T1',), q=1),
         Rule(l='T1', r=('P2', 'P3'), q=1),
         Rule(l='P2', r=('T2',), q=1),
         Rule(l='P3', r=('T2',), q=1),
         Rule(l='T2', r=('P4',), q=1),
         Rule(l='T2', r=('P1',), q=1)]
    """
    t_name = t.name.lower()  # имя перехода
    input_positions = []  # позиции, куда ведет переход
    output_positions = []  # позиции откуда исходит переход

    for l, r, _ in rules:
        if l.name.lower() == t_name:  # если слева искомое имя перехода
            input_positions.extend(r)
        else:  # иначе посмотрим есть ли справа искомое имя перехода
            for r_ in r:
                if r_.name.lower() == t_name:
                    output_positions.append(l)  # и если есть, то добавим

    return output_positions, input_positions


def parse_rules(positions: List[Position], transitions: List[Transition], rules: List[Union[str, tuple]]) -> Dict[Transition, Tuple[List[Position], List[Position]]]:
    """
    Обработать входные правила

    res:
        {'T1': (['P2', 'P3'], ['P1']),
         'T2': (['P4', 'P1'], ['P2', 'P3'])}
    """
    transitions_to_positions = {}
    prepared_rules = []

    splitter = re.compile(r'(\w+)\s*->\s*(.*)')
    quantifier_parser = re.compile(r'(?:(\d+)\s*\*\s*)?(\w+\d+)')

    for rule in rules:
        quantifier = 1

        left, right = re.match(splitter, rule).groups()

        left = find_entity_by_name(positions + transitions, left)

        right = re.findall(quantifier_parser, right)

        processed_r = []
        for elem in right:  # elem = ('2', 'P1)  # 2 * P1
            if elem[0]:
                quantifier = int(elem[0])  # todo wrong

            processed_r.append((find_entity_by_name(transitions + positions, elem[1]), quantifier))  # todo split by different Rule


        prepared_rules.append(Rule(left, processed_r, int(quantifier)))  # прим. Rule(l='T2', r=('P1',), q=1)

    # (?) todo squash rules

    for t in transitions:  # доделаем, получим словарь соответсвия позиций переходам
        transitions_to_positions[t] = fetch_positions(t, prepared_rules)

    return transitions_to_positions


class PNet:
    def __init__(self, name: str, positions: List[Position], transitions: List[Transition], rules):
        self.name = name  # имя сети
        self.positions = positions
        self.transitions = transitions
        self.rules = parse_rules(positions, transitions, rules)

    def model(self, transition_chain: List[str]) -> List:
        """
        :param transition_chain: ['T1', 'T2]
        :return: bool
        """
        results = []

        for t_name in transition_chain:
            transition = find_entity_by_name(self.transitions, t_name)
            from_positions, to_positions = self.rules[transition]

            for p in from_positions:
                try:
                    p.sub_points(1)
                except PointError:
                    return results

            for p in to_positions:
                p.add_points(1)

            results.append(t_name)
            pprint(self.positions)

        return results

    def print(self):
        pprint({
            'name': self.name,
            'positions': self.positions,
            'transitions': self.transitions,
            'rules': self.rules
        })


if __name__ == '__main__':
    # pnet = PNet('Petri1',
    #             positions=[
    #                 Position('P1', 1),
    #                 Position('P2', 0),
    #                 Position('P3', 2),
    #                 Position('P4', 1)
    #             ],
    #             transitions=[
    #                 Transition('T1'),
    #                 Transition('T2')
    #             ],
    #             rules=[
    #                 'P1 -> T1',
    #                 'P1 -> T1',
    #                 'T1 -> P2 P3',
    #                 'P2 -> T2',
    #                 'P3 -> T2',
    #                 'T2 -> P4',
    #                 'T2 -> P1'
    #             ])

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
                    Transition('T4'),  # todo exception if entity does not exist
                ],
                rules=[
                    #'T1 -> P1',
                    'T1 -> 2*P1 P2',
                    'P1 -> T2 T4',
                    'T2 -> 2*P1 P2',
                    'P2 -> T3 T4',
                    'T4 -> P3 P4'
                ])

    pnet.print()

    result = pnet.model(['T1', 'T2'])
    print(result)
