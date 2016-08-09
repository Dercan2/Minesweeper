import logging


# Токен мины. Это значит, что среди всех клеток, к котороым обращается токен, есть мина(ы).
class MineToken:
    def __init__(self, mines_amount, cells):
        if not cells:
            raise ValueError('Попытка создать токен на пустом множестве клеток.')
        self.mines_amount = mines_amount
        self.cells = cells
        for cell in cells:
            cell.tokens |= {self}
        # Запоминает поле, на котором создан, и добавляет себя в базу токенов этого поля.
        self.field = next(iter(self.cells)).field
        logging.debug('Новосозданный токен нашел поле {}'.format(id(self.field)))
        self.field.tokens |= {self}
        logging.debug('token with {} cells'.format(len(self.cells)))

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

    def __str__(self):
        line1 = 'Токен, мин: {}'.format(self.mines_amount)
        cells_info = [str(cell.x+1) + ', ' + str(cell.y+1) for cell in self.cells]
        cells_info = '; '.join(cells_info)
        line2 = '   Клетки: ' + cells_info
        return line1 + '\n' + line2


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
