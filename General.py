# Основные константы и исключения игры.

# Константа для обозначения мины.
MINE_SIGNATURE = 99


# Означает, что нет окна с игрой.
class NoGameError(Exception):
    pass


# Была открыта клетка с бомбой.
class BombOpened(Exception):
    pass
