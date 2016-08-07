MINE_SIGNATURE = 99


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
    # Токены бомб, обращающиеся к этой клетке.
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
        if outcome != MINE_SIGNATURE:
            self.mines_around = outcome
        else:
            self.marked = self.considered = True

    # Помечает клетку как содержащую мину.
    def mark(self):
        if not self.marked:
            self.considered = self.marked = True
            self.field.source.mark(self.y, self.x)

    # Возвращает множество клеток вокруг текущей.
    # Можно задать дополнительные условия ждя отсева.
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