import random
import logging
from MineToken import pick_out_tokens
from General import Victory
from Cell import open_cells, mark_cells


class Bot:
    def __init__(self, game_field):
        self.field = game_field

    tokens = property(lambda self: self.field.tokens)

    # Открывает случайную клетку.
    def random_open(self):
        if self.field.unclear_cells_counter == 0:
            raise Victory
        while True:
            x = random.randint(0, self.field.width - 1)
            y = random.randint(0, self.field.height - 1)
            cell = self.field[y, x]
            if not cell.opened and not cell.marked:
                logging.debug('Великий рандом открыл {}, {}.'.format(x+1, y+1))
                cell.open()
                break

    # ПЫТАЕТСЯ открыть клетку, исходя из того, что имеет.
    # True - была открыта по крайней мере одна клетка.
    def smart_open(self):
        if not self.to_open:
            return False
        while self.to_open:
            cell = next(iter(self.to_open))
            cell.open()
            if cell.mines_around == 0:
                cell.considered = True
                self.to_open |= cell.cells_around(opened=False)
            else:
                self.to_consider |= {cell}
                self.to_consider |= cell.cells_around(opened=True, considered=False)
            self.to_open -= {cell}
        return True

    # Рассматривает клетки и пытается найти мины / открыть новые.
    # Возвращает True, если удалось найти новую клетку, которую надо открыть.
    def consider(self):
        # Перебор элементов.
        while self.to_consider:
            cell = next(iter(self.to_consider))
            self.to_consider -= {cell}
            # Если вокруг столько же закрытых клеток, сколько и бомб.
            if cell.mines_around == len(cell.cells_around(opened=False)):
                cell.considered = True
                for suspect in cell.cells_around(opened=False):
                    suspect.mark()
                    self.to_consider |= suspect.cells_around(opened=True, considered=False)
            # Если вокруг достаточно отмеченных ячеек.
            elif cell.mines_around == len(cell.cells_around(marked=True)):
                cell.considered = True
                self.to_open |= cell.cells_around(marked=False, opened=False)
                return True
        return False

    # Рассматривает клетки с помощью токенов.
    def consider_tokens(self):
        logging.debug('Начало использования токенов.')
        # Стирание старых токенов
        for cell in self.field:
            cell.tokens = set()
        # Расстановка новых токенов и создание множества рассматриваемых клеток.
        for cell in self.field:
            if cell.opened and not cell.considered:
                cell.tokenize()
                self.to_consider |= {cell}
        # Перебор клеток.
        result = False
        while self.to_consider:
            cell = next(iter(self.to_consider))
            mines_left = cell.mines_around - len(cell.cells_around(marked=True))
            # log
            log_msg = 'Рассматривается клетка {}, {} с {} неизвестными минами.'
            logging.debug(log_msg.format(cell.x+1, cell.y+1, mines_left))
            # Выделение целых токенов.
            tokens = pick_out_tokens(cell.cells_around(opened=False, marked=False))
            log_msg = '  Токенов: {}'
            logging.debug(log_msg.format(len(tokens)))
            # Начинаются размышления.
            for token in tokens:
                cells_without_this_token = cell.cells_around(opened=False, marked=False) - token.cells
                print('cells without token', len(cells_without_this_token))
                # Если удается найти клетки без бомб.
                if mines_left == token.mines_amount:
                    self.to_open |= cells_without_this_token
                    result = True
                    # DEBUG
                    print('SUCCESS: cells without bombs:')
                    for ce in cells_without_this_token:
                        print('   ', ce.y+1, ce.x+1)
                    # DEBUG END
                # Если удается найти бомбы.
                elif mines_left - token.mines_amount == len(cells_without_this_token):
                    for suspect in cells_without_this_token:
                        suspect.mark()
                        self.to_consider |= suspect.cells_around(opened=True, considered=False)
                    # DEBUG
                    print('SUCCESS: cells with bombs')
                    for ce in cells_without_this_token:
                        print('   ', ce.y+1, ce.x+1)
                    # DEBUG END
                    result = True
            self.to_consider -= {cell}
        #self.zero_kara()
        logging.debug('Завершение токенов с результатом {}.'.format(result))
        return result

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

    def action(self):
        if self.field.unclear_cells_counter == 0:
            raise Victory
        while self.consider_tokens_by_one():
            pass
        if self.field.unclear_cells_counter == 0:
            raise Victory
        self.random_open()
        if self.field.unclear_cells_counter == 0:
            raise Victory

    # Рассматривает токены по одному и пытается разрешить статусы клеток.
    # True - если удалось разрешить хотя бы одну клетку.
    def consider_tokens_by_one(self):
        result = False
        tokens_to_consider = list(self.tokens)
        for token in tokens_to_consider:
            result |= check_token(token)
        return result


# Проверяет токен, чтобы найти клетки, которые можно открыть / отметить.
# True - удалось найти такие клетки.
def check_token(token):
    # Проверка на случай, если этот токен перестал существовать, пока рассматривались остальные.
    if not token:
        return False
    # Нераскрытых клеток столько же, сколько и мин.
    if len(token.cells) == token.mines_amount:
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