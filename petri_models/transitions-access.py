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


class SolveTree:
    def __init__(self, state):
        self.root = SolveNode(None, state, None)
        self.seen_states = set()

    def __str__(self):
        return str(self.root)

    def add_node(self, parent: 'SolveNode', child: 'SolveNode'):
        parent.children.append(child)
        self.seen_states.add(tuple(child.state))


class SolveNode:
    def __init__(self, transition, state, parent):
        self.transition = transition
        self.state = state
        self.parent = parent

        self.children = []

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


def get_verbose(enable):
    def f(*args, **kwargs):
        if enable:
            print(*args, **kwargs)

    return f


def trace_path(petri_net, solve_tree: SolveTree, solve_node: SolveNode, transition, level=0, verbose=get_verbose(False), verbose_model=False):
    """
    Основной метод, рекурсивно перебираем все цепочки переходов и строим деерво допустимых.

    :param petri_net: Экземпляр сети Петри, на котором проводится испытание
    :param solve_tree: Дерево решений
    :param solve_node: Текущий узел в дереве решений
    :param transition: Переход, который мы попробуем выполнить
    :param level: глубина рекурсивного вызова, для принтов
    :param verbose: Фкнкция полученная от get_verbose, будет выводится лог действий от нас
    :param verbose_model: Если указано, будет выводится лог действий от модели
    """
    if transition is not None:
        petri_net.set_state(solve_node.state)  # вернем состояние как у предка
        success, state, path = petri_net.model([transition], verbose=False)

        if success:
            new_state = process_state(solve_node.state, state)  # обработаем состояние

            br = tuple(new_state) in solve_tree.seen_states

            verbose('{}{}  --{}-->  {} {}'.format('    ' * level, solve_node.state, transition, new_state, '!break: state already exist' if br else ''))

            if br:
                return

            new_solve_node = SolveNode(transition, state=new_state, parent=solve_node)
            solve_tree.add_node(solve_node, new_solve_node)

            for t in petri_net.transition_names:
                trace_path(petri_net, solve_tree, new_solve_node, t, verbose=verbose, verbose_model=verbose_model, level=level+1)
        else:
            verbose('{}transition {} failed'.format('    ' * level, transition))

    else:
        for t in petri_net.transition_names:
            trace_path(petri_net, solve_tree, solve_node, t, verbose=verbose, verbose_model=verbose_model, level=level + 1)


if __name__ == '__main__':
    verbose_trace = False
    verbose_model = False

    initial_state = [0, 0, 0, 0]
    t_names = ['T1', 'T2', 'T3', 'T4']
    pnet = PNet('Petri1',
                positions=[Position('P' + str(idx + 1), p) for idx, p in enumerate(initial_state)],
                transitions=[Transition(n) for n in t_names],
                rules=[
                    'T1 -> P1',
                    'P1 -> T2 T4',
                    'T2 -> 2*P1 P2',
                    'P2 -> T3 T4',
                    'T4 -> P3 P4'
                ])

    st = SolveTree(initial_state)

    trace_path(pnet, st, st.root, None, verbose=get_verbose(verbose_trace), verbose_model=verbose_model)

    print('\n\n\nДерево доступных переходов:\n', st)


    initial_state = [0, 0, 0]
    t_names = ['T1', 'T2', 'T3', 'T4']
    pnet = PNet('Petri2',
                positions=[Position('P' + str(idx + 1), p) for idx, p in enumerate(initial_state)],
                transitions=[Transition(n) for n in t_names],
                rules=[
                    'T1 -> P1',
                    'P1 -> T2',
                    'T2 -> P2',
                    'P2 -> T3',
                    'T3 -> P3',
                    'P3 -> T4'
                ])

    st = SolveTree(initial_state)

    trace_path(pnet, st, st.root, None, verbose=get_verbose(verbose_trace), verbose_model=verbose_model)

    print('\n\n\n2 Дерево доступных переходов:\n', st)


    initial_state = [0] * 5
    t_names = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']
    pnet = PNet('Petri3',
                positions=[Position('P' + str(idx + 1), p) for idx, p in enumerate(initial_state)],
                transitions=[Transition(n) for n in t_names],
                rules=[
                    'T1 -> P1',
                    'P1 -> T2 T3',
                    'T2 -> P2',
                    'P2 -> T4 T5',
                    'T4 -> P4',
                    'P4 -> T6 T7',
                    'T5 -> P5',
                    'T3 -> P3'
                ])

    st = SolveTree(initial_state)

    trace_path(pnet, st, st.root, None, verbose=get_verbose(verbose_trace), verbose_model=verbose_model)

    print('\n\n\n3 Дерево доступных переходов:\n', st)
