import discord
from discord.ext import commands
import GameTimer
import random
from copy import deepcopy

import logging

f = open(file="token.txt", mode="r")
token = " ".join(f.readline().split())
f.close()

f = open(file="fallacies.txt", mode="r")
fallacies = f.readlines()

# ------------------------------------------------------------------------------
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
# ------------------------------------------------------------------------------
description = '''Чат-бот для игры в fallacymania'''
bot = commands.Bot(command_prefix='?', description=description)
client = discord.Client()
server = discord.Server
# ------------------------------------------------------------------------------
paused = False
started = False
debaters_list = []
guessers_list = []
discard = []


async def end_game():
    print("2Игра закончилась2")
    global started
    started = False
    await bot.say("Игра закончилась")


def end():
    print("Игра закончилась")
    bot.loop.create_task(end_game())

game_timer = GameTimer.RenewableTimer(120, end)


@bot.event
async def on_ready():

    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)

    print('------')

@bot.command()
async def старт():
    """Начать игру"""
    bot.say()
    global game_timer
    global started
    global paused
    global debaters_list
    global guessers_list
    global fallacies
    global pack
    global debater_cards

    # Если таймер не запущен и игра не на паузе, есть как минимум 2 спорщика и 1 отгадчик
    if not (game_timer.timer.isAlive() or paused) and len(debaters_list) > 1 and len(guessers_list) > 0:
        game_timer = GameTimer.RenewableTimer(120, end)
        debater_cards = {}
        pack = deepcopy(fallacies)
        # Перемешаить колоду
        random.shuffle(pack)
        # Раздать карты спорщикам
        for debater in debaters_list:
            ch = await bot.start_private_message(debater)
            i = 0
            card_list = []
            while i < 5:
                card = pack.pop()
                card_list.append(card)
                await bot.send_message(ch, card)
                i += 1
            debater_cards.update({debater: card_list})

        game_timer.start()
        await bot.say("Игра началась")
        started = True
    # Если таймер запущен
    elif game_timer.timer.isAlive():
        await bot.say("Таймер уже запущен")
        game_timer.pause()
        s = int(game_timer.get_actual_time())
        m = int(s/60)
        await bot.say("Осталось {0}м {1}с".format(m, s))
        game_timer.resume()
    elif paused:
        game_timer.resume()
        await bot.say("Игра продолжается")
    elif len(debaters_list) < 2:
        await bot.say("Нужно указать как минимум 2 спорщиков")
    elif len(guessers_list) < 1:
        await bot.say("Нужно указать как минимум 1 отгкадчика")



@bot.command()
async def пауза():
    """приостановить таймер"""
    global game_timer
    global paused
    global started
    if started:
        game_timer.pause()
        game_timer.get_actual_time()
        paused = True
        await bot.say("Пауза")
        s = int(game_timer.get_actual_time())
        m = int(s/60)
        await bot.say("Осталось {0}м {1}с".format(m, s))
    else:
        await bot.say("Игра ещё не запущена")


@bot.command()
async def спорщики(*args: discord.Member):
    """Спорщики"""
    global debaters_list
    debaters_list=[]

    debaters = ""
    for i in args:
        if i.name not in debaters_list:
            debaters_list.append(i)
            debaters += "**{}**, ".format(i.name)

    await bot.say('{0} в команде спорщиков \nВсего в команде спорщиков {1} игроков'.format(debaters[:-2],
                                                                                           len(debaters_list)))

@bot.command()
async def отгадчики(*args: discord.Member):
    """Отгадчики"""
    global guessers_list
    guessers_list=[]
    guessers = ""
    for i in args:
        if i.name not in guessers_list:
            guessers_list.append(i)
            guessers += "**{}**, ".format(i.name)
    #global guessers_list
    await bot.say('{0} в команде отгадчиков \nВсего в команде отгадчиков {1} игроков'.format(guessers[:-2],
                                                                                             len(guessers_list)))

@bot.command()
async def софизм(sophism):
    """"С помощью ?софзизм %номер_софизма% карта уходит в сброс, а спорщик, у которого сбросилась карта получает
    новую """
    global started
    global paused
    global debaters_list
    global guessers_list
    global fallacies
    global pack
    global debater_cards
    global discard

    if not started:
        return await bot.say("Сначала следует начать игру")
    if sophism.isdigit():
        if len(fallacies) <= int(sophism):
            return await bot.say("Номер карточки должен быть не больше {}".format(len(fallacies) - 1))

        so = fallacies[int(sophism)]
        check_card = False
        for debater in debater_cards:
            card_list = debater_cards.get(debater)
            if card_list.count(so) > 0:
                check_card = True
                card_list.remove(so)
                card = pack.pop()
                card_list.append(card)
                discard.append(card)
                ch = await bot.start_private_message(debater)
                await bot.send_message(ch, card)

        if not check_card:
            return await bot.say("Ни у одного из спорщиков нет карточки номер {}".format(sophism))

        # Если колода закончилась, то сброшенные карты перемешиваются и становятся колодой
        if not pack:
            pack = deepcopy(discard)
            random.shuffle(pack)
            discard = []
    else:
        await bot.say("Команда ?софзизм должна принимать номер указанный на карточке с софизмом")


@bot.command()
async def правила():
    """Показать правила игры"""
    await bot.say('''
    **Fallacymania — правила игры**
    Оригинальные правила - http://gdurl.com/z6s0A/download

    Для игры нужно 3–20 игроков (рекомендуется 4–12). Игроки разбиваются на 2 группы: спорщики (2–10 игроков) и отгадчики (1–10 игроков). Ведущий может играть в любой из этих ролей.

**Подготовка к игре**
    Некоторые (или все) спорщики определяют для себя тезисы, которые они будут отстаивать с использованием софизмов.
    Задача спорщиков — проталкивать собственные тезисы, а также комментировать (поддерживать или опровергать) сказанное другими спорщиками, но с использованием софизмов со своих карт
    Примеры тезисов:
        Инопланетных цивилизаций не существует;
        Никого невозможно в чём-то убедить при помощи софизмов;
        Зелёный цвет красивее, чем красный.
    Спорщики могут объединяться в группы, когда несколько человек отстаивают один и тот же тезис. Те спорщики, которые не взяли себе никакой тезис, используют софизмы только для ответов на сказанное другими.
''')

    await bot.say('''**Ход игры**
    1. Игра идёт в реальном времени. Спорщики говорят фразы в поддержку своего тезиса, а также поддерживают или опровергают тезисы других спорщиков.
    Но всё это должно делаться с использованием софизмов, которые есть у спорщиков на картах.
    2. У спорщиков нет условий победы и поражения; их цель — попрактиковаться использовать софизмы так, чтобы аргументы звучали убедительно.
    3. Спорщики могут говорить в любом порядке; могут как отвечать на реплики других игроков, так и высказывать новые суждения относительно своего тезиса.
    4. Отгадчики смотрят дебаты и пытаются угадать, какие софизмы используют спорщики. Отгадчики соревнуются между собой, кто наберёт больше очков за угаданные софизмы.
    5. Любой из отгадчиков может в любой момент пытаться угадывать софизмы, которые используют спорщики. Для этого отгадчик громко говорит имя спорщика и название софизма, который, как ему кажется, употребил этот спорщик. Спорщик отвечает отгадчику, правильная была догадка или нет.
    6. Отгадчик может пытаться угадать софизмы __только из последней реплики__, сказанной спорщиком.
    Если спорщик уже начал говорить следующую реплику, предыдущие софизмы угадывать нельзя. Тем не менее, можно пытаться угадать последние сказанные софизмы других спорщиков, пока они не начали говорить.
''')
    await bot.say('''
    7. Спорщик может использовать в одной реплике несколько софизмов одновременно из тех, которые есть у него на картах. Отгадчики тоже могут пытаться найти несколько софизмов в одной реплике спорщика.
    8. За каждый угаданный софизм отгадчик получает __1 очко__ , а спорщик откладывает угаданную карту софизма в сброс и берёт себе новую из колоды. Если колода заканчивается, то сброс перетасовывается и становится новой колодой.
    9. Спорщик больше не может использовать тот софизм, который ушёл в сброс, но может пользоваться новым полученным софизмом.
    10. Если отгадчик называет не тот софизм, который использовал спорщик, то он теряет 1 карту попытки . Когда карты попыток у отгадчика заканчиваются, __он начинает терять по 1 очку__ за каждую неправильную попытку.
    11. Игра продолжается __20 минут__. В конце игры среди отгадчиков определяется победитель по количеству набранных очков.''')

bot.run(token)
