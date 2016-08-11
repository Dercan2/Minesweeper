import logging

# Основные константы и исключения игры.

# Константа для обозначения мины.
MINE_SIGNATURE = 99

# Символы для обозначений объектов.
MARK_SYMBOL = 'M'
CLOSED_SYMBOL = '#'
CONSIDERED_SYMBOL = 'c'
MINE_SYMBOL = '*'


# Была открыта клетка с бомбой.
class MineOpened(Exception):
    pass


# Были определены все клетки.
class Victory(Exception):
    pass