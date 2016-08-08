import logging
import General
from time import sleep
from GameField import GameField
from Blank import Blank
from Bot import Bot
from ActualGame import Combatant

comb = Combatant()
field = GameField(comb)
bot = Bot(field)
count = 0
try:
    while count < 20:
        bot.action()
        if field.unclear_cells_counter == 0:
            print('VICTORY')
            break
        sleep(1)
        count += 1
except General.BombOpened:
    print(field)