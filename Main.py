#!/usr/local/bin/python
# -*- coding: UTF-8 -*-
import logging
import General
from time import sleep
from GameField import GameField
from Blank import Blank
from Bot import Bot
from ActualGame import Combatant

logging.basicConfig(filename='Minesweeper.log', level=logging.DEBUG)
logging.info('Начало новой игры.')
comb = Combatant()
field = GameField(comb)
logging.debug('Id игрового поля: {}'.format(id(field)))
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
except General.Victory:
    print('Victory!')