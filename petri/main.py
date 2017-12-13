from pprint import pprint

from typing import List

from entities import Position, Transition, EntityError
from parser import Parser
from utils import find_entity_by_name


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
