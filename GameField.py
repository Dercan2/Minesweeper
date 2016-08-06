from Cell import Cell


# Абстрактное игровое поле. Отображает знания бота о текущей игре.
class GameField:
    # Создает абстрактное игровое поле с указанными параметрами.
    # source - объект, у которого будут узнаваться подробности игры.
    # То есть именно этот объект отвечает за связь бота и внешней игры.
    def __init__(self, source):
        self.source = source
        # Узнаем размер игрового поля.
        self.height, self.width = source.get_dimensions()
        # Двумерный массив клеток.
        self.sheet = [ [Cell(self, i, j) for j in range(self.width)] for i in range(self.height) ]

    # Доступ к клеткам.
    def __getitem__(self, key):
        return self.sheet[key[0]][key[1]]

    # Представляет игровое поле в тектовом виде.
    def __str__(self, show_considered = False):
        MARK_SYMBOL = 'M'
        CLOSED_SYMBOL = '#'
        CONSIDERED_SYMBOL = 'c'
        symbols_in_row = self.width + 1
        symbols_amount = symbols_in_row * self.height - 1
        list_of_symbols = ['\n' for i in range(symbols_amount)]
        for y in range(self.height):
            for x in range(self.width):
                cell = self[y, x]
                symbol = CLOSED_SYMBOL
                if show_considered and cell.opened and cell.considered:
                    symbol = CONSIDERED_SYMBOL
                elif cell.opened:
                    symbol = str(cell.mines_around)
                elif cell.marked:
                    symbol = MARK_SYMBOL
                index = symbols_in_row * y + x
                list_of_symbols[index] = symbol
        return ''.join(list_of_symbols)

    # Для итераций по клеткам игрового поля.
    class Iterator:
        def __init__(self, field):
            self.field = field
            self.x = self.y = 0

        def __next__(self):
            if self.y == self.field.height:
                raise StopIteration
            result = self.field[self.y, self.x]
            self.x += 1
            if self.x == self.field.width:
                self.x = 0
                self.y += 1
            return result

    def __iter__(self):
        return GameField.Iterator(self)