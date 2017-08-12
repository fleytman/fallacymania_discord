import discord
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
    # global channel

    started = False

    max_points = 0
    winners = []
    # Определяет отгадчика с максимальным количеством очков
    for guesser in guesser_points:
        if guesser_points[guesser] > max_points:
            max_points = guesser_points[guesser]
            winner = guesser
            winners = [winner.name]
        elif guesser_points[guesser] == max_points:
            winners.append(guesser.name)

    if len(guesser_points) < 2:
        msg = "Победитель **{}**".format(guesser.name)
    elif len(winners) < 2:
        msg = "Победитель **{}**".format(winner.name)
    elif len(winners) > 1:
        msg = "Победители **{}**".format("**" + "**, **".join(winners) + "**")

    score = current_score(guesser_points, guesser_attempts)

    for user in guessers_list + debaters_list:
        ch = await client.start_private_message(user)
        await client.send_message(ch, "{0}\n{1}\nИгра закончилась".format(score, msg))
    print("Игра закончилась")


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


async def add_guesser(member, guessers_list):
    ch = await client.start_private_message(member)
    if member not in guessers_list:
        guessers_list.append(member)
        guesser_names.append(member.name)
        guessers = "**" + "**, **".join(guesser_names) + "**"

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
        guessers = "**" + "**, **".join(guesser_names) + "**"
        await client.send_message(ch,
                                  'Вы уже в группе отгадчиков \nГруппа отгадчиков: {0}\nОбщее количество '
                                  'отгадчиков: **{1}**'.format(guessers, len(guessers_list)))

async def remove_guesser(member, guessers_list):
    if member in guessers_list:
        guessers_list.remove(member)
        guesser_names.remove(member.name)
        guessers = "**" + "**, **".join(guesser_names) + "**"
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
                                      "Общее количество отгадчиков: **{2}**".format(member.name, guessers,
                                                                                    len(guessers_list)))

async def add_debater(member, debaters_list):
    ch = await client.start_private_message(member)
    if member not in debaters_list:
        debaters_list.append(member)
        debater_names.append(member.name)
        debaters = "**" + "**, **".join(debater_names) + "**"

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
        debaters = "**" + "**, **".join(debater_names) + "**"
        await client.send_message(ch,
                                  'Вы уже в группе спорщиков \nГруппа спорщиков: {0}\nОбщее количество '
                                  'спорщиков: **{1}**'.format(debaters, len(debaters_list)))

async def remove_debater(member, debaters_list):
    if member in debaters_list:
        debaters_list.remove(member)
        debater_names.remove(member.name)
        debaters = "**" + "**, **".join(debater_names) + "**"
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
                                      "Общее количество спорщиков: **{2}**".format(member.name, debaters,
                                                                                   len(debaters_list)))


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

    if message.content == "!help" or message.content == "!h":
        ch = await client.start_private_message(member)
        await client.send_message(ch, """```Чат-бот для игры в Fallacymania
        
Команды:

"!help" или "!h" - Выводит данную справку

"!r" или "!правила" - выводит правила

"!d" или "!спорщик" - Добавляет пользователя в группу спорщиков

"!-d" или "!-спорщик" - Удаляет пользователя из группы спорщиков

"!g" или "!отгадчик" - Добавляет пользователя в группу отгадчиков

"!-g" или "!-отгадчик" - Удаляет пользователя из группы отгадчиков

"!s" или "!старт! - если указанно минимальное количество отгадчиков и спорщиков, то запускает таймер игры

"%номер_софизма%" - ищет у спорщика софизм по номеру, если находит, то забирает и даёт новый

"+" или "-"  - дать или забрать очко у отгадчика

".+" или ".-" - дать или забрать попытку у отгадчика
```""")

    if message.content == "!d" or  message.content == "!спорщик":
        await add_debater(member, debaters_list)
        await remove_guesser(member, guessers_list)

    if message.content == "!g" or message.content == "!отгадчик":
        await client.loop.create_task(add_guesser(member, guessers_list))
        await client.loop.create_task(remove_debater(member, debaters_list))

    if message.content == "!-g" or message.content == "!-отгадчик":
        await remove_guesser(member, guessers_list)

    if message.content == "!-d" or message.content == "!-спорщик":
        await client.loop.create_task(remove_debater(member, debaters_list))


    # Старт игры
    if message.content == '!s' or message.content == '!старт':
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
            # • если отгадчиков больше 6, то 50 карт попыток делятся поровну между отгадчиками,
            # а остаток убирается обратно в коробку.
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

    # Пауза
    if message.content == '!p' or message.content == '!пауза':
        if started and not paused:
            game_timer.pause()
            game_timer.get_actual_time()
            paused = True
            await client.send_message(channel, "Пауза")
            s = int(game_timer.get_actual_time())
            m = int(s/60)
            await client.send_message(channel, "Осталось {0}м {1}с".format(m, s))
        elif not started:
            await client.send_message(channel, "Игра ещё не запущена")
        elif paused:
            await client.send_message(channel, "Игра уже на паузе")


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

    if message.content == '!r' or message.content == "!правила":
        """Показать правила игры"""
        ch = await client.start_private_message(member)
        # Разделено на 3 сообщения, из-за лимита на количество символов в discord
        await client.send_message(ch, '''
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

        await client.send_message(ch, '''**Ход игры**
    1. Игра идёт в реальном времени. Спорщики говорят фразы в поддержку своего тезиса, а также поддерживают или опровергают тезисы других спорщиков.
    Но всё это должно делаться с использованием софизмов, которые есть у спорщиков на картах.
    2. У спорщиков нет условий победы и поражения; их цель — попрактиковаться использовать софизмы так, чтобы аргументы звучали убедительно.
    3. Спорщики могут говорить в любом порядке; могут как отвечать на реплики других игроков, так и высказывать новые суждения относительно своего тезиса.
    4. Отгадчики смотрят дебаты и пытаются угадать, какие софизмы используют спорщики. Отгадчики соревнуются между собой, кто наберёт больше очков за угаданные софизмы.
    5. Любой из отгадчиков может в любой момент пытаться угадывать софизмы, которые используют спорщики. Для этого отгадчик громко говорит имя спорщика и название софизма, который, как ему кажется, употребил этот спорщик. Спорщик отвечает отгадчику, правильная была догадка или нет.
    6. Отгадчик может пытаться угадать софизмы __только из последней реплики__, сказанной спорщиком.
    Если спорщик уже начал говорить следующую реплику, предыдущие софизмы угадывать нельзя. Тем не менее, можно пытаться угадать последние сказанные софизмы других спорщиков, пока они не начали говорить.
        ''')
        await client.send_message(ch, '''
    7. Спорщик может использовать в одной реплике несколько софизмов одновременно из тех, которые есть у него на картах. Отгадчики тоже могут пытаться найти несколько софизмов в одной реплике спорщика.
    8. За каждый угаданный софизм отгадчик получает __1 очко__ , а спорщик откладывает угаданную карту софизма в сброс и берёт себе новую из колоды. Если колода заканчивается, то сброс перетасовывается и становится новой колодой.
    9. Спорщик больше не может использовать тот софизм, который ушёл в сброс, но может пользоваться новым полученным софизмом.
    10. Если отгадчик называет не тот софизм, который использовал спорщик, то он теряет 1 карту попытки . Когда карты попыток у отгадчика заканчиваются, __он начинает терять по 1 очку__ за каждую неправильную попытку.
    11. Игра продолжается __20 минут__. В конце игры среди отгадчиков определяется победитель по количеству набранных очков.''')


def current_score(guesser_points, guesser_attempts):
    msg = "Общий счёт (Игрок: очки | попытки):\n"
    for guesser in guesser_points:
        msg += "**{0}**: {1} | {2} \n".format(guesser.name, guesser_points[guesser], guesser_attempts[guesser])
    return msg


client.run(token)
