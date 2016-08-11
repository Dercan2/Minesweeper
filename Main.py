#!/usr/local/bin/python
# -*- coding: UTF-8 -*-
import logging
import General
from time import sleep
from GameField import GameField
from Blank import Blank
from Bot import Bot
from ActualGame import Combatant

LOG_FILE_NAME = 'Minesweeper.log'
#logging.basicConfig(filename='Minesweeper.log', level=logging.DEBUG)
logging.info('Начало новой игры.')
comb = Combatant()
field = GameField(comb)
bot = Bot(field)
try:
    while True:
        bot.action()
except General.MineOpened:
    logging.debug('Поле:\n' + str(field))
    print('Oops, a mine was opened =(')
    logging.info('Проигрыш.')
except General.Victory:
    print('Victory!')
    logging.info('Победа.')
finally:
    logging.info('Завершение.\n')