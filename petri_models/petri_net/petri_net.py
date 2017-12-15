from pprint import pprint

from typing import List

from petri_models.petri_net.entities import Position, Transition, EntityError

from petri_models.petri_net.parser import Parser
from petri_models.petri_net.utils import find_entity_by_name


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

    def save(self):
        pass

    @classmethod
    def from_file(cls):
        pass
