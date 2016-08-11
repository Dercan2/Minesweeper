# Файл игры содержит описание source класса - Combatant. Класс работает с действующей игрой.
import time
import logging
from ctypes import Structure, wintypes, byref, windll
from PIL import ImageGrab
from General import MINE_SIGNATURE
from Colors import Color
import Colors

# Основные константы для работы с окном игры; получены эмпирическим путем.
# Размер ячейки игрового поля.
CELL_SIZE = 16
# Смещение первой ячейки относительно начала окна.
GAME_FIELD_OFFSET_X = 15
GAME_FIELD_OFFSET_Y = 100
# Пространство, занимаемое не ячейками поля.
NON_GAME_REGION_WIDTH = 26
NON_GAME_REGION_HEIGHT = 111
# Задержка между командами (в секундах)
TIME_DELAY = 0.001


# Объект-источник, который получает информацию из Сапер.exe
class Combatant:
    def __init__(self):
        # Получение хэндла.
        self.handle = windll.user32.FindWindowW(0, 'Сапер')
        if self.handle == 0:
            raise RuntimeError('Не найдено окно с игрой.')
        # Получение параметров окна.
        self.window = RECT()
        self.window_update()
        # Выводит сапера на передний план.
        windll.user32.SetForegroundWindow(self.handle)
        # Делает снимок окна игры.
        screen_box = self.window.left, self.window.top, self.window.right, self.window.bottom
        image = ImageGrab.grab(screen_box)
        # Получает снимок в виде двумерного массива цветов.
        image_buffer = image.load()
        # Нахождение основных элементов окна.
        self.mines_counter_offset = self.calculate_mines_counter_position(image_buffer)
        self.game_field_offset = self.calculate_game_field_position(image_buffer)

    # Возращает смещение (относительно окна) счетчика мин.
    def calculate_mines_counter_position(self, buffer):
        # Проходит последовательно все клетки, пока не найдет красную.
        x = y = 0
        color = Colors.Black
        while color != Colors.Red and color != Colors.DarkRed:
            x += 1
            if x >= self.window.width:
                x = 0
                y += 1
                if y >= self.window.height:
                    raise RuntimeError('Счетчик мин не был найден.')
            color = Color(buffer[x, y])
        # Теперь идем вверх и влево до тех пор, пока не найдем последнюю черную клетку.
        good_colors = {Colors.Black, Colors.Red, Colors.DarkRed}
        while Color(buffer[x, y]) in good_colors:
            y -= 1
        while Color(buffer[x, y]) in good_colors:
            x -= 1
        logging.debug('Определены координаты счетчика мин: %d, %d' % (y, x))
        return y, x

    # Возвращает смещение игрового поля.
    def calculate_game_field_position(self, buffer):
        # От счетчика мин идем вниз до тех пор, пока не встретим переход от темно серых клеток к белыи.
        y, x = self.mines_counter_offset
        while not (Color(buffer[x, y-1]) == Colors.DarkGrey and Color(buffer[x, y]) == Colors.White):
            y += 1
            if y >= self.window.height:
                raise RuntimeError('Игровое поле не было найдено.')
        # Теперь, когда положение y найдено, идем влево, пока цвет не станет темно серым.
        while Color(buffer[x-1, y]) != Colors.DarkGrey:
            x -= 1
        logging.debug('Определены координаты игрового поля: %d, %d' % (y, x))
        return y, x

    # Обновляет положение окна, на случай, если оно было изменено.
    # Если не найдет окна с сапером - выбрасывает RuntimeError
    def window_update(self):
        if windll.user32.FindWindowW(0, 'Сапер') == 0:
            raise RuntimeError('Не найдено окно с игрой.')
        # Получение параметров окна.
        windll.user32.GetWindowRect(self.handle, byref(self.window))

    # Преобразует игровые координаты в координаты окна.
    def game_coordinates_to_screen(self, game_y, game_x):
        screen_y = game_y * CELL_SIZE + self.window.y + GAME_FIELD_OFFSET_Y
        screen_x = game_x * CELL_SIZE + self.window.x + GAME_FIELD_OFFSET_X
        return screen_y, screen_x

    # Преобразует координаты окна в игровые.
    def screen_coordinates_to_game(self, screen_y, screen_x):
        game_y = (screen_y - self.window.y - GAME_FIELD_OFFSET_Y) // CELL_SIZE
        game_x = (screen_x - self.window.x - GAME_FIELD_OFFSET_X) // CELL_SIZE
        return game_y, game_x

    # Возвращает высоту и ширину.
    def get_dimensions(self):
        rows = (self.window.height - NON_GAME_REGION_HEIGHT) // CELL_SIZE
        columns = (self.window.width - NON_GAME_REGION_WIDTH) // CELL_SIZE
        return rows, columns
    dimensions = property(get_dimensions)

    # Открывает клетку и возвращает либо число мин вокруг, либо MINE_SIGNATURE
    def open(self, y, x):
        self.window_update()
        y, x = self.game_coordinates_to_screen(y, x)
        windll.user32.SetCursorPos(x + CELL_SIZE // 2, y + CELL_SIZE // 2)
        # Выводит сапера на передний план.
        windll.user32.SetForegroundWindow(self.handle)
        time.sleep(TIME_DELAY)
        # Нажатие и отпускание левой кнопки мыши.
        windll.user32.mouse_event(2, 0, 0, 0,0)
        time.sleep(TIME_DELAY)
        windll.user32.mouse_event(4, 0, 0, 0,0)
        time.sleep(TIME_DELAY)
        box = x, y, x + CELL_SIZE, y + CELL_SIZE
        screen = ImageGrab.grab(box)
        return define_cell(screen)

    # Помечает клетку как содержащую мину.
    def mark(self, y, x):
        self.window_update()
        y, x = self.game_coordinates_to_screen(y, x)
        windll.user32.SetCursorPos(x + CELL_SIZE // 2, y + CELL_SIZE // 2)
        # Выводит сапера на передний план.
        windll.user32.SetForegroundWindow(self.handle)
        time.sleep(TIME_DELAY)
        # Нажатие и отпускание правой кнопки мыши.
        windll.user32.mouse_event(8, 0, 0, 0,0)
        time.sleep(TIME_DELAY)
        windll.user32.mouse_event(16, 0, 0, 0,0)
        time.sleep(TIME_DELAY)


# Класс, необходимый для получения данных об окне.
class RECT(Structure):
    _fields_ = [
      ('left',   wintypes.ULONG ),
      ('top',    wintypes.ULONG ),
      ('right',  wintypes.ULONG ),
      ('bottom', wintypes.ULONG )
    ]

    x = property(lambda self: self.left)
    y = property(lambda self: self.top)
    width = property(lambda self: self.right-self.left)
    height = property(lambda self: self.bottom-self.top)


# Распознает клетку по картинке 16х16. В случае бомбы возвращает MINE_SIGNATURE.
def define_cell(image):
    buffer = image.load()
    color = buffer[9, 12]
    extra_color = buffer[1, 1]
    if nearly(color, (0, 0, 255)):
        return 1
    elif nearly(color, (0, 123, 0)):
        return 2
    elif nearly(color, (255, 0, 0)):
        return 3
    elif nearly(color, (0, 0, 123)):
        return 4
    elif nearly(color, (123, 0, 0)):
        return 5
    elif nearly(color, (0, 123, 123)):
        return 6
    elif nearly(color, (0, 0, 0)) and not nearly(extra_color, (255, 0, 0)):
        return 7
    elif nearly(color, (123, 123, 123)):
        return 8
    elif nearly(color, (189, 189, 189)):
        return 0
    elif nearly(extra_color, (255, 0, 0)):
        return MINE_SIGNATURE
    else:
        raise RuntimeError('Не удалось распознать цвет.')