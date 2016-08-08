#!/usr/local/bin/python
# -*- coding: UTF-8 -*-
from General import BombOpened, MINE_SIGNATURE
from MineToken import MineToken


# Ячейка игрового поля.
class Cell:
    # Сколько мин рядом.
    mines_around = None
    # Открыта ли.
    opened = False
    # Метка наличия бомбы.
    marked = False
    # Полностью изучен. То есть известны все соседние клетки. Также True, если помечена бомбой.
    considered = False
    # Токены бомб, обращающихся к этой клетке.
    tokens = set()

    # Создает клетку.
    # field - поле, которому эта клетка принадлежит.
    # y, x - координаты.
    def __init__(self, field, y, x):
        self.field = field
        self.y = y
        self.x = x

    # Открывает клетку.
    def open(self):
        self.opened = True
        outcome = self.field.source.open(self.y, self.x)
        if outcome == MINE_SIGNATURE:
            self.mines_around = MINE_SIGNATURE
            raise BombOpened
        self.mines_around = outcome
        # Все токены, обращающиеся к данной клетке, должны быть соответственно изменены.
        for token in self.tokens:
            token.cells -= {self}
        self.field.unclear_cells_counter -= 1

    # Помечает клетку как содержащую мину.
    def mark(self):
        if self.marked:
            return
        self.considered = self.marked = True
        self.field.source.mark(self.y, self.x)
        # Все токены, обращающиеся к данной клетке, должны быть соответственно изменены.
        for token in list(self.tokens):
            token.mines_amount -= 1
            token.cells -= {self}
            if token.mines_amount == 0:
                for cell in token.cells:
                    cell.tokens -= {token}
        self.field.unclear_cells_counter -= 1

    # Создает токен мины, основываясь на данной клетке.
    def tokenize(self):
        if not self.opened or self.considered:
            return
        mines_amount = self.mines_around - len(self.cells_around(marked=True))
        cells = self.cells_around(opened=False, marked=False)
        return MineToken(mines_amount, cells)

    # Возвращает множество клеток вокруг текущей.
    # Можно задать дополнительные условия для отсева.
    def cells_around(self, opened=None, marked=None, considered=None):
        result = set()
        for offset_y in (-1, 0, 1):
            for offset_x in (-1, 0, 1):
                if offset_y == 0 and offset_x == 0:
                    continue
                y = self.y + offset_y
                x = self.x + offset_x
                # Проверка на выход за границы поля.
                if y not in range(self.field.height) or x not in range(self.field.width):
                    continue
                cell = self.field[y, x]
                # Проверка на дополнительные условия.
                if opened is not None and cell.opened != opened or\
                   marked is not None and cell.marked != marked or\
                   considered is not None and cell.considered != considered:
                    pass
                else:
                    result |= {cell}
        return result
