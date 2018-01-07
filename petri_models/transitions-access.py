from petri_models.petri_net import Position, Transition
from petri_models.petri_net import PNet


class _Omega(float):
    """
    Вся магия Омеги происходит от того, что это float NaN,
    Т.к Омега по свойствам идентична NaN, остается только красиво вывести ее в консоль.
    """
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, 'NaN')

    def __repr__(self):
        return 'Ω'

    __str__ = __repr__


Omega = _Omega()  # создадим единственный объект Омеги


class OmegaPosition(Position):
    def __init__(self, name, points):
        super().__init__(name, points)

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, count):
        if self._points is not Omega:  # запишем в фишки все что угодно, если там не Омега
            super(OmegaPosition, self.__class__).points.fset(self, count)


class SolveTree:
    def __init__(self, state):
        self.root = SolveNode(None, state, None)

    def __str__(self):
        return str(self.root)


class SolveNode:
    def __init__(self, transition, state, parent):
        self.transition = transition
        self.state = state
        self.parent = parent

        self.children = []

    def add_node(self, new_node):
        self.children.append(new_node)

    def __str__(self, level=0):
        print_state = '({})'.format(' '.join(map(str, self.state)))

        if self.parent is None:
            res = '{} \n'.format(print_state)
        else:
            res = '{} --{}--> {} \n'.format(" " * 4 * level, self.transition, print_state)

        for child in self.children:
            res += child.__str__(level + 1)

        return res


def process_state(old_state, new_state):
    """
    Заменим в стейте элементы, которые отличаются от предыдущего стейта больше чем на 1, на Omega
      иначе оставим как есть
    :return Новый стейт
    """
    return [n if n - o < 1 else Omega for o, n in zip(old_state, new_state)]


def trace_path(petri_net, solve_tree: SolveTree, solve_node: SolveNode, transition, verbose=False):
    """
    Основной метод, рекурсивно перебираем все цепочки переходов и строим деерво допустимых.

    :param petri_net: Экземпляр сети Петри, на котором проводится испытание
    :param solve_tree: Дерево решений
    :param solve_node: Текущий узел в дереве решений
    :param transition: Переход, который мы попробуем выполнить
    :param verbose: Если указано, будет выводится лог действий, как от сети, так и от нас
    """

    petri_net.set_points(solve_node.state)  # вернем состояние как у предка
    success, state, path = petri_net.model(transition, verbose=verbose)

    if success:
        new_state = process_state(solve_node.state, state)  # обработаем состояние
        if new_state == solve_node.state:
            if verbose:
                print('tree break: old state {} != new state {} '.format(new_state, state))
            return

        new_solve_node = SolveNode(transition, state=new_state, parent=solve_node)  # todo разобраться с переходом и массивом из одного перехода
        solve_node.add_node(new_solve_node)

        for new_transition in petri_net.transition_names:
            trace_path(petri_net, solve_tree, new_solve_node, [new_transition])


if __name__ == '__main__':
    initial_state = [0, 0, 0, 0]
    t_names = ['T1', 'T2', 'T3', 'T4']

    pnet = PNet('Petri1',
                positions=[OmegaPosition('P' + str(idx + 1), p) for idx, p in enumerate(initial_state)],
                transitions=[Transition(n) for n in t_names],
                rules=[
                    'T1 -> P1',
                    'P1 -> T2 T4',
                    'T2 -> 2*P1 P2',
                    'P2 -> T3 T4',
                    'T4 -> P3 P4'
                ])

    st = SolveTree(initial_state)

    trace_path(pnet, st, st.root, ['T1'])

    print('Дерево доступных переходов:\n', st)
