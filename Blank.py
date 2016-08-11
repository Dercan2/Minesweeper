import random
from General import MINE_SIGNATURE
from General import MINE_SIGNATURE, CLOSED_SYMBOL, MINE_SYMBOL, MARK_SYMBOL


# Класс-источник заранее сгенерированного поля. Предназначен для тестов.
class Blank:
    # Конструктор. По аргументам определяет, какой функцией создать объект.
    def __init__(self, *args):
        if len(args) == 1 and type(args[0]) is str:
            self.create_specific_field(args[0])
        else:
            self.create_random_field(*args)

    # Создает поле на основе строкового представления.
    def create_specific_field(self, field_str):
        pass

    # Создает случайное поле с заданным числом клеток и мин.
    def create_random_field(self, height=16, width=30, mines=99):
        self.width = width
        self.height = height
        self.mines = mines
        # Булевский двумерный массив. True - есть бомба.
        self.sheet = [ [bool(False) for j in range(width)] for i in range(height) ]
        mines = self.mines
        # Случайным образом расставляет мины.
        random.seed()
        while mines != 0:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.sheet[y][x] is False:
                self.sheet[y][x] = True
                mines -= 1

    # Возвращает высоту и ширину.
    def get_dimensions(self):
        return self.height, self.width

    # Открывает клетку и возвращает либо число мин вокруг, либо MINE_SIGNATURE
    def open(self, y, x):
        value = self.sheet[y][x]
        if value:
            return MINE_SIGNATURE
        else:
            return self.calculate_mines_around(y, x)

    # Помечает клетку как содержащую мину.
    def mark(self, y, x):
        pass

    # Возвращает количество мин вокруг данной клетки.
    def calculate_mines_around(self, y, x):
        result = 0
        for offset_y in (-1, 0, 1):
            for offset_x in (-1, 0, 1):
                if offset_y == 0 and offset_x == 0:
                    continue
                shifted_y = y + offset_y
                shifted_x = x + offset_x
                # Проверка границ поля и наличия мины.
                if shifted_y in range(self.height) and shifted_x in range(self.width) and\
                        self.sheet[shifted_y][shifted_x]:
                    result += 1
        return result