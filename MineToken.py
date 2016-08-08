# Токен мины. Это значит, что среди всех клеток, к котороым обращается токен, есть мина(ы).
class MineToken:
    def __init__(self, mines_amount, cells):
        self.mines_amount = mines_amount
        self.cells = cells
        for cell in cells:
            cell.tokens |= {self}


# Возвращает множество токенов, обращающихся к данным клеткам. Если таковые найдутся.
def pick_out_tokens(cells):
    # Создание множества всех токенов, встречающихся среди данных ячеек.
    tokens = set()
    for cell in cells:
        tokens |= cell.tokens
    # Отсев неполных токенов.
    tokens = {token for token in tokens if token.cells in cells}
    return tokens
