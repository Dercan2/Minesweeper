import Bot
from GameField import GameField
from Blank import Blank
from Bot import Bot
from ActualGame import Combatant
from time import sleep

comb = Combatant()
field = GameField(comb)
bot = Bot(field)
count = 0
while count < 20:
    bot.action()
    sleep(1)
    count += 1