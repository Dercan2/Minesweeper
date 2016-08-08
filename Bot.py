import random
from MineToken import pick_out_tokens


class Bot:
    # Клетки, которые надо изучить.
    to_consider = set()
    # Клетки, которые надо открыть.
    to_open = set()

    def __init__(self, game_field):
        self.field = game_field

    # Открывает случайную клетку.
    def random_open(self):
        if self.field.unclear_cells_counter == 0:
            return
        print('random open')
        while True:
            x = random.randint(0, self.field.width - 1)
            y = random.randint(0, self.field.height - 1)
            cell = self.field[y, x]
            if not cell.opened and not cell.marked:
                cell.open()
                self.to_consider |= {cell}
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
        print('consider_tokens called.')
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
            print('new cell', cell.y, cell.x)
            mines_left = cell.mines_around - len(cell.cells_around(marked=True))
            print('mines left =', mines_left)
            # Выделение целых токенов.
            tokens = pick_out_tokens(cell.cells_around(opened=False, marked=False))
            print('tokens', len(tokens))
            # Начинаются размышления.
            for token in tokens:
                print('watch another token')
                cells_without_this_token = cell.cells_around(opened=False, marked=False) - token.cells
                # Если попался токен, который обращается ко всем рассматриваемым клеткам.
                if len(cells_without_this_token) == 0:
                    continue
                print('cells without token', len(cells_without_this_token))
                # Если удается найти клетки без бомб.
                if mines_left == token.mines_amount:
                    self.to_open |= cells_without_this_token
                    result = True
                    print('SUCCESS: cells without bombs')
                # Если удается найти бомбы.
                elif mines_left - token.mines_amount == len(cells_without_this_token):
                    for suspect in cells_without_this_token:
                        suspect.mark()
                        self.to_consider |= suspect.cells_around(opened=True, considered=False)
                    print('SUCCESS: cells with bombs')
                    result = True
            self.to_consider -= {cell}
        self.zero_kara()
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
        while self.smart_open() or self.consider() or self.consider_tokens():
            pass
        self.random_open()


class NothingToConsider(Exception):
    pass
