import re
from collections import namedtuple

from typing import List, Union, Any, Dict, Tuple

from entities import Position, Transition
from utils import find_entity_by_name


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