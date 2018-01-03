from petri_models.petri_net import Position, Transition

from petri_models.petri_net import PNet


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

    success, state, result = pnet.model(path)

    print('Success' if success else 'Fail')
    if result:
        print('Executed transitions:', ' -> '.join(result))
    else:
        print('>>> None of transitions were executed')

    print('State AFTER last transition:', state)

    print('#' * 40)