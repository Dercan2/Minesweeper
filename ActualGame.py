# Файл игры содержит описание source класса - Combatant. Класс работает с действующей игрой.
import time
import logging
from ctypes import Structure, wintypes, byref, windll
from PIL import ImageGrab
from General import MINE_SIGNATURE, MARK_SIGNATURE, CLOSED_SIGNATURE
from Colors import Color
import Colors

# Размер ячейки игрового поля.
CELL_SIZE = 16
# Размеры ячейки табло.
BOARD_CELL_WIDTH = 13
BOARD_CELL_HEIGHT = 23
# Высота бан региона. То есть в верхней полосе такой ширины ничего не надо искать.
BAN_REGION_HEIGHT = 25
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
        time.sleep(TIME_DELAY)
        # Делает снимок окна игры.
        screen_box = self.window.left, self.window.top, self.window.right, self.window.bottom
        image = ImageGrab.grab(screen_box)
        # Нахождение основных элементов окна.
        self.mines_counter_offset = self.calculate_mines_counter_position(image)
        self.game_field_offset = self.calculate_game_field_position(image)

    # Возращает смещение (относительно окна) счетчика мин.
    def calculate_mines_counter_position(self, image):
        buffer = image.load()
        # Проходит последовательно все клетки, пока не найдет красную.
        x = 0
        y = BAN_REGION_HEIGHT
        color = Colors.Black
        while color != Colors.Red and color != Colors.DarkRed:
            x += 1
            if x >= self.window.width:
                x = 0
                y += 1
                if y >= self.window.height:
                    image.save('Mines counter not found.png')
                    raise RuntimeError('Счетчик мин не был найден.')
            color = Color(buffer[x, y])
        # Теперь идем вверх и влево до тех пор, пока не найдем последнюю черную клетку.
        good_colors = {Colors.Black, Colors.Red, Colors.DarkRed}
        while Color(buffer[x, y-1]) in good_colors:
            y -= 1
        while Color(buffer[x-1, y]) in good_colors:
            x -= 1
        logging.debug('Определены координаты счетчика мин: %d, %d' % (y, x))
        return y, x

    # Возвращает смещение игрового поля.
    def calculate_game_field_position(self, image):
        buffer = image.load()
        # От счетчика мин идем вниз до тех пор, пока не встретим переход от темно серых клеток к белыи.
        y, x = self.mines_counter_offset
        while not (Color(buffer[x, y-1]) == Colors.DarkGrey and Color(buffer[x, y]) == Colors.White):
            y += 1
            if y >= self.window.height:
                image.save('Game field not found.png')
                raise RuntimeError('Игровое поле не было найдено на стадии y.')
        # Теперь, когда положение y найдено, идем влево, пока цвет не станет темно серым.
        while Color(buffer[x-1, y]) != Colors.DarkGrey:
            x -= 1
            if x <= 0:
                raise RuntimeError('Игровое поле не было найдено на стадии x.')
        logging.debug('Определены координаты игрового поля: %d, %d' % (y, x))
        return y, x

    # Обновляет положение окна; на случай, если оно было изменено.
    # Если не найдет окна с сапером - выбрасывает RuntimeError
    def window_update(self):
        if windll.user32.FindWindowW(0, 'Сапер') == 0:
            raise RuntimeError('Не найдено окно с игрой.')
        # Получение параметров окна.
        windll.user32.GetWindowRect(self.handle, byref(self.window))

    # Преобразует игровые координаты в координаты окна.
    def game_coordinates_to_screen(self, game_y, game_x):
        screen_y = game_y * CELL_SIZE + self.window.y + self.game_field_offset[0]
        screen_x = game_x * CELL_SIZE + self.window.x + self.game_field_offset[1]
        return screen_y, screen_x

    # Преобразует координаты окна в игровые.
    def screen_coordinates_to_game(self, screen_y, screen_x):
        game_y = (screen_y - self.window.y - self.game_field_offset[0]) // CELL_SIZE
        game_x = (screen_x - self.window.x - self.game_field_offset[1]) // CELL_SIZE
        return game_y, game_x

    # Возвращает высоту и ширину (в клетках) игрового поля.
    def get_game_field_dimensions(self):
        rows = (self.window.height - self.game_field_offset[0]) // CELL_SIZE
        columns = (self.window.width - self.game_field_offset[1]) // CELL_SIZE
        logging.debug('Определены расмеры игрового поля: %d x %d.' % (columns, rows))
        return rows, columns
    dimensions = property(get_game_field_dimensions)

    # Возвращает текущее число мин.
    def get_current_mines_amount(self):
        offset_x = self.window.x + self.mines_counter_offset[1]
        offset_y = self.window.y + self.mines_counter_offset[0]
        region = offset_x, offset_y, offset_x + BOARD_CELL_WIDTH * 3, offset_y + BOARD_CELL_HEIGHT
        image = ImageGrab.grab(region)
        return define_mines_amount(image)
    mines_amount = property(get_current_mines_amount)

    # Открывает клетку.
    def open(self, game_y, game_x):
        self.window_update()
        y, x = self.game_coordinates_to_screen(game_y, game_x)
        # Выводит сапера на передний план.
        windll.user32.SetForegroundWindow(self.handle)

        # Установка курсора приблизительно посередине клетки.
        windll.user32.SetCursorPos(x + CELL_SIZE // 2, y + CELL_SIZE // 2)
        time.sleep(TIME_DELAY)
        # Нажатие и отпускание левой кнопки мыши.
        windll.user32.mouse_event(2, 0, 0, 0,0)
        time.sleep(TIME_DELAY)
        windll.user32.mouse_event(4, 0, 0, 0,0)
        time.sleep(TIME_DELAY)

        # Изучаем клетку.
        result = self.check(game_y, game_x)
        # Если мина - это проблема бота, клетка была открыта.
        # А вот если она не открыта - это проблема данного класса.
        if result == CLOSED_SIGNATURE:
            raise RuntimeError('Не удалось открыть клетку %d, %d' % (game_x+1, game_y+1))
        elif result == MARK_SIGNATURE:
            raise RuntimeError('Не удалось открыть клетку %d, %d, т.к. она помечена миной.' % (game_x+1, game_y+1))
        else:
            return result

    def open_around(self, game_y, game_x):
        self.window_update()
        y, x = self.game_coordinates_to_screen(game_y, game_x)
        # Выводит сапера на передний план.
        windll.user32.SetForegroundWindow(self.handle)

        # Установка курсора приблизительно посередине клетки.
        windll.user32.SetCursorPos(x + CELL_SIZE // 2, y + CELL_SIZE // 2)
        time.sleep(TIME_DELAY)
        # Нажатие и отпускание обоих кнопок мыши.
        windll.user32.mouse_event(2, 0, 0, 0,0)
        windll.user32.mouse_event(8, 0, 0, 0,0)
        time.sleep(TIME_DELAY)
        windll.user32.mouse_event(4, 0, 0, 0,0)
        windll.user32.mouse_event(16, 0, 0, 0,0)
        time.sleep(TIME_DELAY)

        # Как-то так. Не знаю, писать ли здесь проверку, если она есть в Cell.open_around

    # Помечает клетку как содержащую мину.
    def mark(self, game_y, game_x):
        self.window_update()
        y, x = self.game_coordinates_to_screen(game_y, game_x)
        # Выводит сапера на передний план.
        windll.user32.SetForegroundWindow(self.handle)

        # Установка курсора приблизительно посередине клетки.
        windll.user32.SetCursorPos(x + CELL_SIZE // 2, y + CELL_SIZE // 2)
        time.sleep(TIME_DELAY)
        # Нажатие и отпускание правой кнопки мыши.
        windll.user32.mouse_event(8, 0, 0, 0,0)
        time.sleep(TIME_DELAY)
        windll.user32.mouse_event(16, 0, 0, 0,0)
        time.sleep(TIME_DELAY)

        # Проверка.
        if self.check(game_y, game_x) == MARK_SIGNATURE:
            # Клетка была успешно помечена.
            return True
        else:
            raise RuntimeError('Не удалось пометить клетку %d, %d.' % (game_x+1, game_y+1))

    # Возвращает то, что находится в данной клетке.
    def check(self, game_y, game_x):
        y, x = self.game_coordinates_to_screen(game_y, game_x)
        # Снимок клетки для проверки.
        box = x, y, x + CELL_SIZE, y + CELL_SIZE
        cell_image = ImageGrab.grab(box)
        return define_cell(cell_image)


# Вспомогательный класс, необходимый для получения данных об окне.
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
    # Проверка на мину.
    color = Color(buffer[1, 1])
    if color == Colors.Red:
        return MINE_SIGNATURE

    # Проверка на не открытие клетки.
    color = Color(buffer[0, 0])
    if color == Colors.White:
        # Клетка не открыта. Осталось проверить наличие метки на ней.
        extra_color = Color(buffer[8, 6])
        if extra_color == Colors.Red:
            return MARK_SIGNATURE
        elif extra_color == Colors.Grey:
            return CLOSED_SIGNATURE
        else:
            image.save('Fail to define cell.png')
            raise RuntimeError('Клетка закрыта и не удалось распознать ее.')

    # Клетка открыта, определяем цифру на ней.
    # 9, 12 - особая точка, с помощью которой можно определить цифру от 0 до 8
    color = Color(buffer[9, 12])
    if color in Colors.ColorToDigitMap:
        return Colors.ColorToDigitMap[color]
    else:
        image.save('Fail to define cell.png')
        raise RuntimeError('Клетка открыта, но не удалось распознать ее.')


def define_mines_amount(image):
    # Разрежем на три цифры.
    images = []
    for i in range(3):
        crop_region = i * BOARD_CELL_WIDTH, 0, (i+1) * BOARD_CELL_WIDTH, BOARD_CELL_HEIGHT
        images += [image.crop(crop_region)]

    result = 0
    # Изучение каждой по отдельности.
    for i in range(3):
        buffer = images[i].load()
        draft = set()
        # Теперь проверка на каждую черту.
        for line in LineCoordinatesMap:
            # Сюда будут записываться те отрезки, которые зажжены.
            color = Color(buffer[LineCoordinatesMap[line]])
            if color == Colors.Red:
                # Отрезон зажжен, отмечаем это в draft
                draft |= {line}
            elif color == Colors.DarkRed:
                # Отрезок не зажжен, но это нормально.
                pass
            else:
                images[i].save('Board definition fail.png')
                raise RuntimeError('Не удалось отпределить отрезок %s на табло.' % line)
        # Теперь draft заполнен. Определяем цифру.
        for j in range(len(Board)):
            if draft == Board[j]:
                result = result * 10 + j
                break
        else:
            images[i].save('Board wrong definition.png')
            raise RuntimeError('Была получена странная цифра: %s' % str(draft))
    return result


# Код для определения чисел на табло. Не хотелось выделять в отдельный файл.
# Присутствуют те черточки, которые зажжены на табло при соответствующей цифре.
Board = [None for i in range(10)]
Board[1] = {'top right', 'low right'}
Board[7] = Board[1] | {'top'}
Board[3] = Board[7] | {'middle', 'low'}
Board[0] = Board[7] | {'top left', 'low left', 'low'}
Board[8] = Board[0] | {'middle'}
Board[2] = {'top', 'top right', 'middle', 'low left', 'low'}
Board[4] = {'top left', 'top right', 'middle', 'low right'}
Board[5] = {'top', 'top left', 'middle', 'low right', 'low'}
Board[6] = Board[5] | {'low left'}
Board[9] = Board[8] - {'low left'}

# Соответсвие отрезков и координат.
LineCoordinatesMap = {'top': (6, 2), 'top left': (2, 7), 'top right': (10, 7), 'middle': (6, 10),\
                      'low left': (2, 17), 'low right': (10, 17), 'low': (6, 20)}