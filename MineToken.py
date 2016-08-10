import logging


# Токен мины. Это значит, что среди всех клеток, к котороым обращается токен, есть мина(ы).
class MineToken:
    def __init__(self, mines_amount, cells, cell_creator=None):
        if not cells:
            raise ValueError('Попытка создать токен на пустом множестве клеток.')
        # Запоминает создателя. Полезно для отладки.
        self.creator = cell_creator
        # Заполнение остальных полей.
        self.mines_amount = mines_amount
        self.cells = cells
        # Запоминает поле, на котором создан.
        self.field = next(iter(self.cells)).field
        # Теперь имея creator и cells токен можно хешировать.
        for cell in cells:
            cell.tokens |= {self}
        # Добавляет себя в базу токенов поля.
        self.field.tokens |= {self}

    # Число незаминированных клеток.
    blanks_amount = property(lambda self: len(self.cells) - self.mines_amount)

    # Перестает обращаться к клетке.
    def discard(self, cell):
        if not self:
            return
        if cell not in self.cells:
            logging.debug('У клетки {}, {} не удалось отписаться от {}'.format(cell.x+1, cell.y+1, self))
            raise ValueError('Клетка, которую необходимо отписать от токена, не принадлежит этому токену.')
        self.cells -= {cell}
        if cell.marked:
            self.mines_amount -= 1
        # Если у токена не осталось клеток, его следует удалить.
        if not self.cells:
            self.delete()

    # Удаляет токен.
    def delete(self):
        # Удаляет токен из общей базы.
        self.field.tokens -= {self}
        # Отписывает каждую клетку.
        for cell in self.cells:
            cell.tokens -= {self}
        # Обозначим токен как удаленный.
        self.cells = set()
        self.mines_amount = 0

    # True - токен считается существующим.
    def __bool__(self):
        return bool(self.cells)

    # Информация о токене.
    def __str__(self):
        line1 = 'Токен, мин: {}'.format(self.mines_amount)
        cells_info = [str(cell.x+1) + ', ' + str(cell.y+1) for cell in self.cells]
        cells_info = '; '.join(cells_info)
        line2 = '   Клетки: ' + cells_info
        return line1 + '\n' + line2

    # Методы сравнения.
    # ==
    def __eq__(self, other):
        return self.mines_amount == other.mines_amount and self.cells == other.cells

    # !=
    def __ne__(self, other):
        return self.mines_amount != other.mines_amount or self.cells != other.cells

    # <
    # А если точнее, то принадлежит ли один токен другому.
    def __lt__(self, other):
        return self.mines_amount == other.mines_amount and self.cells < other.cells

    # >
    def __gt__(self, other):
        return self.mines_amount == other.mines_amount and self.cells > other.cells

    # <=
    def __le__(self, other):
        return self.mines_amount == other.mines_amount and self.cells <= other.cells

    # >=
    def __ge__(self, other):
        return self.mines_amount == other.mines_amount and self.cells >= other.cells

    def __hash__(self):
        return self.creator.y * self.field.width + self.creator.x


# Возвращает множество токенов, обращающихся только к данным клеткам, но не ко всем из данных. Если таковые найдутся.
def pick_out_tokens(cells):
    # Создание множества всех токенов, встречающихся среди данных ячеек.
    tokens = set()
    for cell in cells:
        tokens |= cell.tokens
    print('tokens before sift', len(tokens))
    # Отсев неполных токенов.
    tokens = {token for token in tokens if token.cells < cells}
    return tokens
