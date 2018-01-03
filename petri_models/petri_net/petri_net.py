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

    def model(self, transition_chain: List[str]):
        """
        :param transition_chain: ['T1', 'T2]
        :return: bool
        """
        def get_state():
            return [p.points for p in self.positions]

        def print_state(msg):
            print(msg)
            for p in self.positions:
                print(p)
            print()

        success = True
        path = []
        try:
            for idx, t_name in enumerate(transition_chain):
                print("\nStep {} - '{}'".format(idx + 1, t_name))

                transition = find_entity_by_name(self.transitions, t_name)
                from_positions, to_positions = self.rules[transition]

                for p in from_positions:
                    p.points -= 1  # Бросит исклбючение

                for p in to_positions:
                    p.points += 1

                path.append(t_name)
                print_state('State after step:')

        except EntityError as e:
            success = False
            print_state('>>> Break: ' + str(e))

        return success, get_state(), path

    def set_points(self, points_vector):
        for pos, points in zip(self.positions, points_vector):
            pos.points = points

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
