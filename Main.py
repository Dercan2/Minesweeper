import Bot
from GameField import GameField
from Blank import Blank
from Bot import Bot

blank = Blank()
field = GameField(blank)
bot = Bot(field)
print(field)
while True:
    command = input()
    if command == 'r':
        bot.random_open()
    elif command == 's':
        while bot.smart_open() or bot.consider():
            pass
    else:
        print('unknown command')
        continue
    print(field)