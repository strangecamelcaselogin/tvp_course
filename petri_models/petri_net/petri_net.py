from pprint import pprint

from typing import List

from petri_models.petri_net.entities import Position, Transition, EntityError

from petri_models.petri_net.parser import Parser
from petri_models.petri_net.utils import find_entity_by_name


def test():
    test_pass = '>>>>>> Test pass <<<<<<<<'
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

    path = []
    success, state, result = pnet.model(path)
    assert success == True
    assert state == [0, 0, 0, 0]
    assert result == []
    print(test_pass)
    pnet.set_state([0, 0, 0, 0])

    path = ['T1', 'T2', 'T2', 'T2']
    success, state, result = pnet.model(path)
    assert success == True
    assert state == [4, 3, 0, 0]
    assert result == path
    print(test_pass)
    pnet.set_state([0, 0, 0, 0])

    path = ['T2']
    success, state, result = pnet.model(path)
    assert success == False
    assert state == [-1, 0, 0, 0]
    assert result == []
    print(test_pass)
    pnet.set_state([0, 0, 0, 0])

    path = ['T1', 'T2', 'T3', 'T4']
    success, state, result = pnet.model(path)
    assert success == False
    assert state == [1, -1, 0, 0]
    assert result == ['T1', 'T2', 'T3']
    print(test_pass)
    pnet.set_state([0, 0, 0, 0])


class PNet:
    def __init__(self, name: str, positions: List[Position], transitions: List[Transition], rules):
        self.name = name  # имя сети
        self.positions = positions
        self.transitions = transitions
        self.transition_names = [t.name for t in transitions]
        self.rules = Parser().parse_rules(positions, transitions, rules)

    def model(self, transition_chain: List[str], verbose=True):
        """
        :param transition_chain: ['T1', 'T2]
        :return: bool
        :param verbose:
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
                if verbose:
                    print("\nStep {} - '{}'".format(idx + 1, t_name))

                transition = find_entity_by_name(self.transitions, t_name)
                from_positions, to_positions = self.rules[transition]

                for p in from_positions:
                    p.points -= 1  # Бросит исклбючение

                for p in to_positions:
                    p.points += 1

                path.append(t_name)

                if verbose:
                    print_state('State after step:')

        except EntityError as e:
            success = False
            if verbose:
                print_state('>>> Break: ' + str(e))

        return success, get_state(), path

    def set_state(self, points_vector):
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


if __name__ == '__main__':
    test()
