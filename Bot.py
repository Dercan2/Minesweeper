import random


class Bot:
    # Клетки, которые надо изучить.
    to_consider = set()
    # Клетки, которые надо открыть.
    to_open = set()

    def __init__(self, game_field):
        self.field = game_field

    # Открывает случайную клетку.
    def random_open(self):
        while True:
            x = random.randint(0, self.field.width - 1)
            y = random.randint(0, self.field.height - 1)
            cell = self.field[y, x]
            if not cell.opened:
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
                self.to_consider |= cell.cells_around(opened=False, considered=False)
            self.to_open -= {cell}
        return True

    # Рассматривает клетки. amount - сколько клеток надо рассмотреть; 0 - все.
    # True - есть новые клетки, которые надо открыть.
    # False - таких нет.
    # Если не удалось рассмотреть нужное число клеток - выбрасывает NothingToConsider.
    def consider(self, amount=0, raise_exception=True):
        # Содержит ли to_consider хотя бы один элемент.
        if not self.to_consider:
            if raise_exception:
                raise NothingToConsider
            else:
                return False
        considered = 0
        # Перебирание amount элементов.
        while self.to_consider:
            cell = next(iter(self.to_consider))
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
            self.to_consider -= {cell}
            if amount != 0:
                considered += 1
                if considered == amount:
                    return True
        if amount != 0 and considered != amount:
            if raise_exception:
                raise NothingToConsider
            else:
                return False
        return True

    # Заново составляет список клеток, которые надо рассмотреть.
    # Также заново назначает considered.
    def zero_kara(self):
        self.to_consider = set()
        for cell in self.field:
            # Закрытые клетки пропускаются, т.к. они уже considered.
            if not cell.opened:
                continue
            # Если вокруг нет закрытых непомеченных клеток - значит данная клетка уже бесполезна.
            if len(cell.cells_around(opened=False, marked=False)) == 0:
                cell.considered = True
            else:
                cell.considered = False
                self.to_consider |= {cell}

    def action(self):
        while self.smart_open() or self.consider(1, False):
            pass
        self.random_open()


class NothingToConsider(Exception):
    pass
