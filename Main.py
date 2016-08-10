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
bot = Bot(field)
try:
    while True:
        bot.action()
except General.MineOpened:
    logging.debug(field)
    print('Oops, a mine was opened =(')
    logging.debug('Проигрыш.')
except General.Victory:
    print('Victory!')
    logging.debug('Победа.')