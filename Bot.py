import random
import logging
from itertools import combinations
from MineToken import pick_out_tokens
from General import Victory
from Cell import open_cells, mark_cells


class Bot:
    def __init__(self, game_field):
        self.field = game_field

    tokens = property(lambda self: self.field.tokens)

    # Открывает случайную клетку.
    def random_open(self):
        if self.field.free_cells_amount == 0 and self.field.mines_amount == 0:
            raise Victory
        while True:
            x = random.randint(0, self.field.width - 1)
            y = random.randint(0, self.field.height - 1)
            cell = self.field[y, x]
            if not cell.opened and not cell.marked:
                logging.debug('Великий рандом открыл {}, {}.'.format(x+1, y+1))
                cell.open()
                break

    # Заново составляет список клеток, которые надо рассмотреть.
    # Также заново назначает considered.
    def zero_kara(self):
        self.to_consider = set()
        for cell in self.field:
            # Закрытые клетки пропускаются
            if not cell.opened:
                continue
            # Если вокруг нет закрытых непомеченных клеток - значит данная клетка уже бесполезна.
            if len(cell.cells_around(opened=False, marked=False)) == 0:
                cell.considered = True
            else:
                cell.considered = False
                self.to_consider |= {cell}

    def solve(self):
        while self.field.mines_amount != 0 and self.field.free_cells_amount != 0:
            while self.consider_tokens_by_one() or self.consider_tokens_by_two():
                pass
            self.random_open()
        else:
            raise Victory

    # Рассматривает токены по одному и пытается разрешить статусы клеток.
    # True - если удалось разрешить хотя бы одну клетку.
    def consider_tokens_by_one(self):
        result = False
        tokens_to_consider = list(self.tokens)
        for token in tokens_to_consider:
            result |= check_token(token)
        return result

    def consider_tokens_by_two(self):
        result = False
        tokens_to_consider = frozenset(self.tokens)
        for token_pair in combinations(tokens_to_consider, 2):
            result |= check_2_tokens(*token_pair)
        return result


# Проверяет токен, чтобы найти клетки, которые можно открыть / отметить.
# True - удалось найти такие клетки.
def check_token(token):
    # Проверка на случай, если этот токен перестал существовать, пока рассматривались остальные.
    if not token:
        return False
    # Нет клеток без мин.
    if token.blanks_amount == 0:
        mark_cells(token.cells)
    # Не осталось мин.
    elif token.mines_amount == 0:
        open_cells(token.cells)
    # Проверка данного токена ничего не дала.
    else:
        return False
    # Сработала одна из двух предыдущих проверок.
    token.delete()
    return True


# Рассматривает 2 токена и пытается определить клетки.
def check_2_tokens(token1, token2):
    # Токены должны существовать и пересекаться.
    if not token1 or not token2 or not (token1.cells & token2.cells):
        return False
    # Если токены оказались равны, один из них надо удалить.
    if token1 == token2:
        token2.delete()
        return False
    # Результат функции. Возвращается в конце.
    result = False
    # Сортировка токенов по числу мин.
    token_more_mines, token_less_mines = token1, token2
    if token_more_mines.mines_amount < token_less_mines.mines_amount:
        token_more_mines, token_less_mines = token_less_mines, token_more_mines
    # Случай, когда в token_more_mines так много мин, что даже если все мины token_less_mines лежат в пересечении,
    # что остальные клетки token_more_mines необходимо заполнить минами.
    difference = token_more_mines.cells - token_less_mines.cells
    if len(difference) == token_more_mines.mines_amount - token_less_mines.mines_amount != 0:
        mark_cells(difference)
        result = True
        logging.debug('При рассмотрении двух токенов нашлись мины.')
    del token_more_mines, token_less_mines
    # Сортировка токенов по числу пустых клеток.
    token_more_blanks, token_less_blanks = token1, token2
    if token_more_blanks.blanks_amount < token_less_blanks.blanks_amount:
        token_more_blanks, token_less_blanks = token_less_blanks, token_more_blanks
    # Аналогично для пустых клеток.
    difference = token_more_blanks.cells - token_less_blanks.cells
    if len(difference) == token_more_blanks.blanks_amount - token_less_blanks.blanks_amount != 0:
        open_cells(difference)
        result = True
        logging.debug('При рассмотрении двух токенов нашлись свободные клетки.')
    return result
