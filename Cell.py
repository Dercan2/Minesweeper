import logging
from General import MineOpened, MINE_SIGNATURE, MARK_SYMBOL, MARK_SIGNATURE, CLOSED_SIGNATURE
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
        # Получение информации о клетке.
        outcome = self.field.source.open(self.y, self.x)
        self.opened = True
        if outcome == MINE_SIGNATURE:
            self.mines_around = MINE_SIGNATURE
            raise MineOpened
        self.mines_around = outcome
        self.check_considered()
        self.unsubscribe_tokens()
        self.tokenize()
        self.field.blanks_amount -= 1

    def open_around(self):
        if not self.opened:
            raise ValueError('Попытка открыть вокруг клетки %d, %d, которая сама не открыта.' % (self.x+1, self.y+1))
        if self.considered:
            logging.debug('Попытка открыть клетки вокруг %d, %d, но она уже considered.' % (self.x+1, self.y+1))
            return
        logging.debug('Открываются клетки вокруг %d, %d.' % (self.x+1, self.y+1))

        # Если клетка нулевая, то и открывать ее не надо.
        if self.mines_around != 0:
            self.field.source.open_around(self.y, self.x)
        cells = self.cells_around(opened=False, marked=False)
        if not cells:
            logging.debug('Попытка открыть клетки вокруг %s, но все клетки открыты и она не considered.' % str(self))
            return
        for cell in cells:
            outcome = cell.field.source.check(cell.y, cell.x)
            if outcome == MARK_SIGNATURE or outcome == CLOSED_SIGNATURE:
                raise RuntimeError('Проблема при открытии %s.' % str(cell))
            cell.opened = True
            cell.mines_around = outcome
            if outcome == MINE_SIGNATURE:
                raise MineOpened
        for cell in cells:
            cell.check_considered()
            cell.unsubscribe_tokens()
            cell.tokenize()
        self.field.blanks_amount -= len(cells)

    # Помечает клетку как содержащую мину.
    def mark(self):
        if self.marked:
            return
        logging.debug('Помечается миной {}, {}.'.format(self.x+1, self.y+1))
        self.considered = self.marked = True
        self.field.source.mark(self.y, self.x)
        self.check_considered()
        self.unsubscribe_tokens()
        self.field.mines_amount -= 1

    # Обновляет значение considered у себя и у соседей.
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
        return MineToken(mines_amount, cells, self)

    # Отписывает все токены от этой клетки.
    def unsubscribe_tokens(self):
        for token in list(self.tokens):
            token.discard(self)
        self.tokens = set()

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

    # Представляет клетку как кортеж координат (первый х).
    def __str__(self):
        return str((self.x+1, self.y+1))


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