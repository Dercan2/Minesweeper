# Максимальная разница компонент цветов, при которой все еще считается, что цвета одинаковые.
COMPONENT_MAX_DIFFERENCE = 10
COMPONENT_MAX_VALUE = 255


# Целый класс для цвета, чтобы в дальнейшем не заморачиваться.
class Color:
    def __init__(self, *args):
        if len(args) == 1:
            self.r, self.g, self.b = args[0]
        else:
            self.r, self.g, self.b = args

    def __eq__(self, other):
        if abs(self.r - other.r) <= COMPONENT_MAX_DIFFERENCE and\
           abs(self.g - other.g) <= COMPONENT_MAX_DIFFERENCE and\
           abs(self.b - other.b) <= COMPONENT_MAX_DIFFERENCE:
            return True
        else:
            return False

    def __hash__(self):
        result = self.r
        result += self.g * COMPONENT_MAX_VALUE
        result += self.b * COMPONENT_MAX_VALUE ** 2
        return result

    def get_tuple(self):
        return self.r, self.g, self.b


# Некоторые используемые цвета.
LightGrey = Color(192, 192, 192)
DarkGrey = Color(128, 128, 128)
Red = Color(255, 0, 0)
DarkRed = Color(128, 0, 0)
White = Color(255, 255, 255)
Black = Color(0, 0, 0)
Blue = Color(0, 0, 255)
Green = Color(128, 0, 0)
DarkBlue = Color(0, 0, 128)
Teal = Color(0, 128, 128)
# Соответствие цифры и цвета.
DigitToColorMap = {1:Blue, 2:Green, 3:Red, 4:DarkBlue, 5:DarkRed, 6:Teal, 7:Black, 8:DarkGrey}
ColorToDigitMap = {DigitToColorMap[key]:key for key in DigitToColorMap}