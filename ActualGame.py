# Файл игры содержит описание source класса - Combatant. Класс работает с действующей игрой.
from ctypes import Structure, wintypes, byref, windll

CELL_SIZE = 16
GAME_FIELD_OFFSET_X = 20
GAME_FIELD_OFFSET_Y = 105


# Объект-источник, который получает информацию из Сапер.exe
class Combatant:
    def __init__(self):
        # Получение хэндла.
        handle = windll.user32.FindWindowW(0, 'Сапер')
        if handle == 0:
            raise RuntimeError('Не удалось найти окно сапера.')
        # Получение параметров окна.
        self.window = RECT()
        windll.user32.GetWindowRect(handle, byref(self.window))

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