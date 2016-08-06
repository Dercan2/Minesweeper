import random


class Bot:
    # Клетки, которые надо изучить.
    to_consider = set()
    # Клетки, которые надо открыть.
    to_open = set()

    def __init__(self, game_field):
        self.field = game_field

    # Открывает случайную клетку.
    def open_random_cell(self):
        x = random.randint(0, self.field.width - 1)
        y = random.randint(0, self.field.height - 1)
        cell = self.field[y, x]
        cell.open()
        self.to_consider |= {cell}