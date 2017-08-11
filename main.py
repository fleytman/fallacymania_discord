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
client = discord.Client()
server = discord.Server
# ------------------------------------------------------------------------------
paused = False
started = False
channel = False
debaters_list = []
debater_names = []
guesser_attempts = []
guessers_list = []
guesser_names = []
guesser_points = []
discard = []


async def end_game():
    global started
    global guesser_points
    global channel

    started = False

    max_points = 0
    winners = []
    score = ""
    for guesser in guesser_points:
        score += "У отгадчика **{0}** {1} очков\n".format(guesser.name, guesser_points[guesser])
        if guesser_points[guesser] > max_points:
            max_points = guesser_points[guesser]
            winner = guesser
            winners = [winner.name]
        elif guesser_points[guesser] == max_points:
            winners.append(guesser.name)
    await client.send_message(channel, score)

    if len(guesser_points) < 2:
        await client.send_message(channel, "Победитель **{}**".format(guesser.name))
    elif len(winners) < 2:
        await client.send_message(channel, "Победитель **{}**".format(winner.name))
    elif len(winners) > 1:
        await client.send_message(channel, "Победители **{}**".format(", ".join(winners)))

    print("Игра закончилась")
    await client.send_message(channel, "Игра закончилась")


def end():
    client.loop.create_task(end_game())

t = 1200
game_timer = GameTimer.RenewableTimer(t, end)


@client.event
async def on_ready():

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)

    print('------')


@client.event
async def on_message(message):
    global game_timer
    global started
    global paused
    global debaters_list
    global debaters
    global guessers_list
    global guessers
    global fallacies
    global pack
    global debater_cards
    global guesser_points
    global guesser_attempts
    # global channel
    global t

    member = message.author
    channel = message.channel

    # we do not want the client to reply to itself
    if member == client.user:
        return

    if message.content == "!спорщик":
        ch = await client.start_private_message(member)
        if member not in debaters_list:
            debaters_list.append(member)
            debater_names.append(member.name)
            debaters = "**"+"**, **".join(debater_names) + "**"

            for debater in debaters_list:
                ch = await client.start_private_message(debater)
                if debater != member:
                    await client.send_message(ch,
                                              "Игрок {0} добавлен в группу спорщиков\n"
                                              "Группа спорщиков: {1}\n"
                                              "Общее количество спорщиков: **{2}**".format(debater.name, debaters,
                                                                                           len(debaters_list)))
                else:
                    await client.send_message(ch,
                                              "Вы добавлены в группу спорщиков\n"
                                              "Группа спорщиков: {1}\n"
                                              "Общее количество спорщиков: **{2}**".format(debater.name, debaters,
                                                                                           len(debaters_list)))
        elif member in debaters_list:
            await client.send_message(ch,
                                      'Вы уже в группе спорщиков \nГруппа спорщиков: {0}\nОбщее количество '
                                      'спорщиков: **{1}**'.format(debaters, len(debaters_list)))
        if member in guessers_list:
            guessers_list.remove(member)
            guesser_names.remove(member.name)
            guessers = "**"+"**, **".join(guesser_names) + "**"
            ch = await client.start_private_message(member)
            await client.send_message(ch,
                                      "Вы удалены из группы олтгадчиков\n"
                                      "Группа отгадчиков: {0}\n"
                                      "Общее количество отгадчиков: **{1}**".format(guessers, len(guessers_list)))
            for guesser in guessers_list:
                ch = await client.start_private_message(guesser)
                await client.send_message(ch,
                                          "Игрок {0} удалён из группы олтгадчиков\n"
                                          "Группа отгадчиков: {1}\n"
                                          "Общее количество отгадчиков: **{2}**".format(member.name, guessers, len(guessers_list)))

    if message.content == "!отгадчик":
        ch = await client.start_private_message(member)
        if member not in guessers_list:
            guessers_list.append(member)
            guesser_names.append(member.name)
            guessers = "**"+"**, **".join(guesser_names) + "**"

            for guesser in guessers_list:
                ch = await client.start_private_message(guesser)
                if guesser != member:
                    await client.send_message(ch,
                                              "Игрок {0} добавлен в группу отгадчиков\n"
                                              "Группа отгадчиков: {1}\n"
                                              "Общее количество отгадчиков: **{2}**".format(guesser.name, guessers,
                                                                                           len(guessers_list)))
                else:
                    await client.send_message(ch,
                                              "Вы добавлены в группу отгадчиков\n"
                                              "Группа отгадчиков: {1}\n"
                                              "Общее количество отгадчиков: **{2}**".format(guesser.name, guessers,
                                                                                           len(guessers_list)))
        elif member in guessers_list:
            await client.send_message(ch,
                                      'Вы уже в группе отгадчиков \nГруппа отгадчиков: {0}\nОбщее количество '
                                      'отгадчиков: **{1}**'.format(guessers, len(guessers_list)))
        if member in debaters_list:
            debaters_list.remove(member)
            debater_names.remove(member.name)
            debaters = "**"+"**, **".join(debater_names) + "**"
            ch = await client.start_private_message(member)
            await client.send_message(ch,
                                      "Вы удалены из группы спорщиков\n"
                                      "Группа спорщиков: {0}\n"
                                      "Общее количество спорщиков: **{1}**".format(debaters, len(debaters_list)))
            for debater in debaters_list:
                ch = await client.start_private_message(debater)
                await client.send_message(ch,
                                          "Игрок {0} удалён из группы спорщиков\n"
                                          "Группа отгадчиков: {1}\n"
                                          "Общее количество спорщиков: **{2}**".format(member.name, debaters, len(debaters_list)))
    # Старт игры
    if message.content == '!s':
        # Если таймер не запущен и игра не на паузе, есть как минимум 2 спорщика и 1 отгадчик
        if not (game_timer.timer.isAlive() or paused) and len(debaters_list) > 1 and len(guessers_list) > 0:
            game_timer = GameTimer.RenewableTimer(t, end)
            debater_cards = {}
            pack = deepcopy(fallacies)
            # Перемешаить колоду
            random.shuffle(pack)
            # Раздать карты спорщикам
            for debater in debaters_list:
                ch = await client.start_private_message(debater)
                i = 0
                card_list = []
                cards = ""
                while i < 5:
                    card = pack.pop()
                    cards += card
                    card_list.append(card)
                    i += 1
                await client.send_message(ch, cards)
                debater_cards.update({debater: card_list})

            guesser_points = {}
            guesser_attempts = {}

            # • если отгадчиков 1-2, каждый берёт по 15 карт попыток;
            # • если отгадчиков 3-4, каждый берёт по 10 карт попыток;
            # • если отгадчиков 5-6, каждый берёт по 8 карт попыток;
            # • если отгадчиков больше 6, то 50 карт попыток делятся поровну между отгадчиками, а остаток убирается обратно
            #  в коробку.
            if len(guessers_list) < 3:
                number_attempts = 15
            elif len(guessers_list) < 5:
                number_attempts = 10
            elif len(guessers_list) < 7:
                number_attempts = 8
            elif len(guessers_list) > 6:
                number_attempts = int(50 / len(guessers_list))

            for guesser in guessers_list:
                # Раздать лист с софизмами отгадчикам
                ch = await client.start_private_message(guesser)
                await client.send_message(ch, "http://i.imgur.com/YhxwU5M.png")
                # Установить начальное количество попыток и очков для отгадчиков
                guesser_points.update({guesser: 0})
                guesser_attempts.update({guesser: number_attempts})

            game_timer.start()
            await client.send_message(channel, "Игра началась")
            started = True
        # Если таймер запущен
        elif game_timer.timer.isAlive():
            await client.send_message(channel, "Таймер уже запущен")
            game_timer.pause()
            s = int(game_timer.get_actual_time())
            m = int(s/60)
            await client.send_message(channel, "Осталось {0}м {1}с".format(m, s))
            game_timer.resume()
        elif paused:
            game_timer.resume()
            await client.send_message(channel, "Игра продолжается")
        elif len(debaters_list) < 2:
            await client.send_message(channel, "Нужно указать как минимум 2 спорщиков")
        elif len(guessers_list) < 1:
            await client.send_message(channel, "Нужно указать как минимум 1 отгкадчика")

    # Начиление очков
    if message.content == '+' or message.content == '-':
        if member not in guesser_points:
            ch = await client.start_private_message(member)
            return await client.send_message(ch, """'+' или '-' отправленное отгадчиком даёт или отнимает очко у 
            этого отгадчика. **{0}** - не отгадчик""".format(member))

        if message.content == "+":
            guesser_points[member] = guesser_points[member] + 1
            msg = "Игрок **{0}** получил 1 очко.".format(member.name)
        elif message.content == "-":
            guesser_points[member] = guesser_points[member] - 1
            msg = "Игрок **{0}** потерял 1 очко.".format(member.name)

        for guesser in guesser_points:
            ch = await client.start_private_message(guesser)
            await client.send_message(ch, "{0} {1}".format(msg, current_score(guesser_points, guesser_attempts)))

    # Начисление попыток
    if message.content == '.+' or message.content == '.-':
        if member not in guesser_points:
            ch = await client.start_private_message(member)
            return await client.send_message(ch, """'.+' или '.-' отправленное отгадчиком даёт или отнимает попытку у 
                    этого отгадчика. **{0}** - не отгадчик""".format(member))

        if message.content == ".+":
            guesser_attempts[member] = guesser_attempts[member] + 1
            msg = "Игрок **{0}** получил 1 попытку.".format(member.name)
        elif message.content == ".-":
            if guesser_attempts[member] < 1:
                guesser_points[member] = guesser_points[member] - 1
                msg = "Попыток у игрока **{0}** нет, он потеряет 1 очко.".format(member.name)
            guesser_attempts[member] = guesser_attempts[member] - 1
            msg = "Игрок **{0}** потерял 1 попытку.".format(member.name)

        for guesser in guesser_points:
            ch = await client.start_private_message(guesser)
            await client.send_message(ch, "{0} {1}".format(msg, current_score(guesser_points, guesser_attempts)))

    if message.content.isdigit() and len(message.content) < 2:
        pass


    if message.content[:1] == "!":
        if message.content[1:] == "!":
            msg = 'Hello {0.author.mention}'.format(message)
            await client.send_message(message.channel, msg)
    if message.content.startswith('!!'):
        msg = '! {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)


def current_score(guesser_points, guesser_attempts):
    msg = "Общий счёт (Игрок: очки | попытки):\n"
    for guesser in guesser_points:
        msg += "**{0}**: {1} | {2} \n".format(guesser.name, guesser_points[guesser], guesser_attempts[guesser])
    return msg


client.run(token)
