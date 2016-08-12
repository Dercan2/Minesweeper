import logging

# Основные константы и исключения игры.

# Константа для обозначения мины.
MINE_SIGNATURE = 99
# Константа для обозначения метки.
MARK_SIGNATURE = 98
# Константа для обозначения закрытой клетки без метки.
CLOSED_SIGNATURE = 10

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


class FailToDefineCell(Exception):
    pass