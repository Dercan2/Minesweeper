import logging
from General import MineOpened, MINE_SIGNATURE, CLOSED_SYMBOL, MINE_SYMBOL, MARK_SYMBOL
from MineToken import MineToken


# Ячейка игрового поля.
class Cell:
    # Сколько мин рядом.
    mines_around = None
    # Открыта ли.
    opened = False
    # Метка наличия мины.
    marked = False
    # Клетка полностью изучена. То есть известны все соседние клетки. Также True, если помечена миной.
    considered = False

    # Создает клетку.
    # field - поле, которому эта клетка принадлежит.
    # y, x - координаты.
    def __init__(self, field, y, x):
        self.field = field
        self.y = y
        self.x = x
        self.tokens = set()

    # Открывает клетку.
    def open(self):
        if self.opened:
            return
        logging.debug('Открывается клетка {}, {}.'.format(self.x+1, self.y+1))
        self.opened = True
        # Получение информации о клетке.
        outcome = self.field.source.open(self.y, self.x)
        if outcome == MINE_SIGNATURE:
            self.mines_around = MINE_SIGNATURE
            raise MineOpened
        self.mines_around = outcome
        self.check_considered()
        self.unsubscribe_tokens()
        self.tokenize()
        self.field.unclear_cells_counter -= 1

    # Помечает клетку как содержащую мину.
    def mark(self):
        if self.marked:
            return
        logging.debug('Помечается миной {}, {}.'.format(self.x+1, self.y+1))
        self.considered = self.marked = True
        self.field.source.mark(self.y, self.x)
        self.check_considered()
        self.unsubscribe_tokens()
        self.field.unclear_cells_counter -= 1

    # Обновляет значение considered у себя и соседей.
    def check_considered(self):
        # На всякий случай. Не предполагается вызывать эту функцию на закрытых клетках.
        if not self.opened:
            return
        # Проверка собственного состояния.
        if len(self.cells_around(opened=False, marked=False)) == 0:
            self.considered = True
        # Обход соседей.
        for cell in self.cells_around(opened=True, considered=False):
            if len(cell.cells_around(opened=False, marked=False)) == 0:
                cell.considered = True

    # Создает токен мины, основываясь на данной клетке.
    def tokenize(self):
        if not self.opened or self.considered:
            return
        mines_amount = self.mines_around - len(self.cells_around(marked=True))
        cells = self.cells_around(opened=False, marked=False)
        return MineToken(mines_amount, cells)

    # Отписывает все токены от этой клетки.
    def unsubscribe_tokens(self):
        for token in list(self.tokens):
            token.discard(self)

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

    def field_piece(self):
        pass


# Проходит простым циклом по каждой клетке и вызывает open()
# Устойчив к изменению элементов в переданном контейнере.
def open_cells(cells):
    cells_to_open = list(cells)
    for cell in cells_to_open:
        cell.open()


# Проходит простым циклом по каждой клетке и вызывает mark()
# Устойчив к изменению элементов в переданном контейнере.
def mark_cells(cells):
    cells_to_mark = list(cells)
    for cell in cells_to_mark:
        cell.mark()