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
# Переменная отвечает за то запущенна ли игра
started = False

async def end_game():
    global started
    global guesser_points

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
        msg = "Победители {}".format("**" + "**, **".join(winners) + "**")

    score = current_score(guesser_points, guesser_attempts)

    for user in guessers_list + debaters_list:
        ch = await client.start_private_message(user)
        await client.send_message(ch, "{0}\n{1}\nИгра закончилась".format(score, msg))
    print("Игра закончилась")


def end():
    client.loop.create_task(end_game())
    client.loop.create_task(reset())

t = 1200
game_timer = GameTimer.RenewableTimer(t, end)


@client.event
async def on_ready():

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)

    print('------')

    await reset()


async def reset():
    global debaters_list
    global debater_names
    global guessers_list
    global guesser_names
    global guesser_attempts
    global guesser_points
    global paused
    global guesser_last_turn

    paused = False
    debaters_list = []
    debater_names = []
    guesser_attempts = {}
    guessers_list = []
    guesser_names = []
    guesser_points = []
    guesser_points = {}
    guesser_last_turn = {}

async def add_guesser(member, guessers_list, guesser_names):
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
                                          "Общее количество отгадчиков: **{2}**".format(member.name, guessers,
                                                                                        len(guessers_list)))
            else:
                await client.send_message(ch,
                                          "Вы добавлены в группу отгадчиков\n"
                                          "Группа отгадчиков: {0}\n"
                                          "Общее количество отгадчиков: **{1}**".format(guessers, len(guessers_list)))
    elif member in guessers_list:
        guessers = "**" + "**, **".join(guesser_names) + "**"
        await client.send_message(ch,
                                  'Вы уже в группе отгадчиков \nГруппа отгадчиков: {0}\nОбщее количество '
                                  'отгадчиков: **{1}**'.format(guessers, len(guessers_list)))

async def remove_guesser(member, guessers_list, guesser_names):
    if member in guessers_list:
        guessers_list.remove(member)
        guesser_names.remove(member.name)
        guessers = "**" + "**, **".join(guesser_names) + "**"
        ch = await client.start_private_message(member)
        await client.send_message(ch,
                                  "Вы удалены из группы отгадчиков\n"
                                  "Группа отгадчиков: {0}\n"
                                  "Общее количество отгадчиков: **{1}**".format(guessers, len(guessers_list)))
        for guesser in guessers_list:
            ch = await client.start_private_message(guesser)
            await client.send_message(ch,
                                      "Игрок {0} удалён из группы отгадчиков\n"
                                      "Группа отгадчиков: {1}\n"
                                      "Общее количество отгадчиков: **{2}**".format(member.name, guessers,
                                                                                    len(guessers_list)))

async def add_debater(member, debaters_list, debater_names):
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
                                          "Общее количество спорщиков: **{2}**".format(member.name, debaters,
                                                                                       len(debaters_list)))
            else:
                await client.send_message(ch,
                                          "Вы добавлены в группу спорщиков\n"
                                          "Группа спорщиков: {1}\n"
                                          "Общее количество спорщиков: **{2}**".format(member.name, debaters,
                                                                                       len(debaters_list)))
    elif member in debaters_list:
        debaters = "**" + "**, **".join(debater_names) + "**"
        await client.send_message(ch,
                                  'Вы уже в группе спорщиков \nГруппа спорщиков: {0}\nОбщее количество '
                                  'спорщиков: **{1}**'.format(debaters, len(debaters_list)))

async def remove_debater(member, debaters_list, debater_names):
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
    global debater_names
    global debaters
    global guessers_list
    global guessers
    global guesser_names
    global fallacies
    global pack
    global debater_cards
    global guesser_points
    global guesser_attempts
    global discard
    global t
    global guesser_last_turn

    member = message.author
    channel = message.channel

    # we do not want the client to reply to itself
    if member == client.user:
        return

    if message.content == "!help" or message.content == "!h":
        ch = await client.start_private_message(member)
        msg = """```Чат-бот для игры в Fallacymania

        Команды:

        "!h" или "!help" - Выводит данную справку

        "!r" или "!правила" - Выводит правила

        "*" или "!софизмы" - Отправляет в ответ лист с софизмами

        "!d" или "!спорщик" - Добавляет пользователя в группу спорщиков

        "!-d" или "!-спорщик" - Удаляет пользователя из группы спорщиков

        "!g" или "!отгадчик" - Добавляет пользователя в группу отгадчиков

        "!-g" или "!-отгадчик" - Удаляет пользователя из группы отгадчиков

        "!s" или "!старт" - Если указано минимальное количество отгадчиков и спорщиков, то запускает таймер игры

        "!p" или "!пазуа" - Приостанавливает таймер игры

        "!stop" или "завершить" - Завершает игру о останавливает таймер

        "%номер_софизма%" - Ищет у спорщика софизм по номеру, если находит, то забирает и даёт новый (вбивается без знаков процент)

        "+" или "-" - Даёт или забирает 1 очко у отгадчика. Пока у отгадчика есть попытки ```-``` забирает 1 попытку, а не 1 очко.
        
        ".." или "!z" - Отменяет последнее действие отгадчика.
        ```"""

        if not started:
            await client.send_message(channel, msg)
        else:
            await client.send_message(ch, msg)

    if message.content == "!d" or message.content == "!спорщик":
        await add_debater(member, debaters_list, debater_names)
        await remove_guesser(member, guessers_list, guesser_names)

    if message.content == "!g" or message.content == "!отгадчик":
        await client.loop.create_task(add_guesser(member, guessers_list, guesser_names))
        await client.loop.create_task(remove_debater(member, debaters_list,debater_names))

    if message.content == "!-g" or message.content == "!-отгадчик":
        await remove_guesser(member, guessers_list, guesser_names)

    if message.content == "!-d" or message.content == "!-спорщик":
        await client.loop.create_task(remove_debater(member, debaters_list, debater_names))

    # Сбросить параматеры игры
    if message.content == "!reset" or message.content == "!сброс":
        if not started:
            for user in debaters_list + guessers_list:
                ch = await client.start_private_message(user)
                await client.send_message(ch, "Список игроков и их счёт сброшены")

            await reset()

        else:
            ch = await client.start_private_message(member)
            await client.send_message(ch, """"Игра уже запущена. Чтобы завершить игру введите "!stop""""")

    # Завершить игру
    if message.content == "!stop" or message.content == "!завершить":
        if started:
            game_timer.cancel()
            end()
        else:
            ch = await client.start_private_message(member)
            await client.send_message(ch, "Нельзя остановить ещё не запущенную игру")

    # Старт игры
    if message.content == '!s' or message.content == '!старт':
        # Если таймер не запущен и игра не на паузе, есть как минимум 2 спорщика и 1 отгадчик
        if not (game_timer.timer.isAlive() or paused) and len(debaters_list) > 1 and len(guessers_list) > 0:
            game_timer = GameTimer.RenewableTimer(t, end)
            debater_cards = {}
            pack = deepcopy(fallacies)
            discard = []
            # Перемешать колоду
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
                await client.send_message(ch, "http://i.imgur.com/ivEjvmi.png\nhttp://i.imgur.com/BukCpJ7.png\nhttp://i.imgur.com/s4qav82.png")
                # Установить начальное количество попыток и очков для отгадчиков
                guesser_points.update({guesser: 0})
                guesser_attempts.update({guesser: number_attempts})
                guesser_last_turn.update({guesser: None})

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
            await client.send_message(channel, "Нужно указать как минимум 1 отгадчика")

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


    # Выдать лист с софизмом
    if message.content == '!софизмы' or message.content == '*':
        ch = await client.start_private_message(member)
        await client.send_message(ch,
                                  "http://i.imgur.com/ivEjvmi.png\nhttp://i.imgur.com/BukCpJ7.png\nhttp://i.imgur.com/s4qav82.png")


    # Начиление очков
    if message.content == '+' or message.content == '-':
        ch = await client.start_private_message(member)
        if not started:
            return await client.send_message(ch, "Игра не запущенна. Проводить манипуляции со счётом до старта игры нельзя.".format(member))

        if member not in guesser_points:
            return await client.send_message(ch, "'+' или '-' отправленное отгадчиком даёт или отнимает очко у "
                                                 "этого отгадчика. **{0}** - не отгадчик".format(member))

        if message.content == "+":
            guesser_points[member] = guesser_points[member] + 1
            guesser_last_turn[member] = "plus_point"
            msg = "Игрок **{0}** получил 1 очко.".format(member.name)
            msg1 = "Вы получили 1 очко."
        elif message.content == "-":
            if guesser_attempts[member] > 0:
                guesser_attempts[member] = guesser_attempts[member] - 1
                guesser_last_turn[member] = "minus_attempt"
                msg = "Игрок **{0}** потерял 1 попытку.".format(member.name)
                msg1 = "Вы потеряли 1 попытку.".format(member.name)
            else:
                guesser_points[member] = guesser_points[member] - 1
                guesser_last_turn[member] = "minus_point"
                msg = "Игрок **{0}** потерял 1 очко.".format(member.name)
                msg1 = "Вы потеряли 1 очко."

        for guesser in guesser_points:
            ch = await client.start_private_message(guesser)
            if guesser != member:
                await client.send_message(ch, "{0} {1}".format(msg, current_score(guesser_points, guesser_attempts)))
            else:
                await client.send_message(ch, "{0} {1}".format(msg1, current_score(guesser_points, guesser_attempts)))

    # Отмена
    if message.content == '!z' or message.content == '..':
        ch = await client.start_private_message(member)

        if not started:
            return await client.send_message(ch, "Игра не запущенна. Нельзя отменить последнее действие".format(member))

        elif member not in guesser_last_turn:
            return await client.send_message(ch, "Отменить последнее действие может только отгадчик.".format(member))

        elif guesser_last_turn[member] is None:
            return await client.send_message(ch, "Вы ещё не совершали никаких действия")

        elif guesser_last_turn[member] == "returned":
            return await client.send_message(ch, "Вы уже отменили своё действие. Отменять больше 1 действия подряд нельзя.")

        elif guesser_last_turn[member] == "plus_point":
            guesser_points[member] = guesser_points[member] - 1
            guesser_last_turn[member] = "returned"
            msg = "Игрок **{0}** отменил своё последнее действие. У него забирается 1 очко.".format(member.name)
            msg1 = "Вы отменили своё последнее действие. У вас забирается 1 очко."

        elif guesser_last_turn[member] == "minus_point":
            guesser_points[member] = guesser_points[member] + 1
            guesser_last_turn[member] = "minus_point"
            guesser_last_turn[member] = "returned"
            msg = "Игрок **{0}** отменил своё последнее действие. Ему возвращается 1 очко.".format(member.name)
            msg1 = "Вы отменили своё последнее действие. Вам возвращается 1 очко."

        elif guesser_last_turn[member] == "minus_attempt":
            guesser_attempts[member] = guesser_attempts[member] + 1
            guesser_last_turn[member] = "returned"
            msg = "Игрок **{0}** отменил своё последнее действие. Ему возвращается 1 попытка.".format(member.name)
            msg1 = "Вы отменили своё последнее действие. Вам возвращается 1 попытка.".format(member.name)

        for guesser in guesser_points:
            ch = await client.start_private_message(guesser)
            if guesser != member:
                await client.send_message(ch, "{0} {1}".format(msg, current_score(guesser_points, guesser_attempts)))
            else:
                await client.send_message(ch, "{0} {1}".format(msg1, current_score(guesser_points, guesser_attempts)))

    # Удаляет карту в сброс
    if message.content.isdigit() and len(message.content) < 3 and member in debaters_list:
        ch = await client.start_private_message(member)
        if len(fallacies) <= int(message.content):
            return await client.send_message(ch, "Номер карточки должен быть не больше {}".format(len(fallacies) - 1))

        so = fallacies[int(message.content)]

        card_list = debater_cards.get(member)
        if card_list.count(so) > 0:
            card_list.remove(so)
            card = pack.pop()
            card_list.append(card)
            discard.append(card)
            await client.send_message(ch, " ".join(card_list))

        else:
            return await client.send_message(ch, "У вас нет карточки номер {}".format(message.content))

        # Если колода закончилась, то сброшенные карты перемешиваются и становятся колодой
        if not pack:
            pack = deepcopy(discard)
            random.shuffle(pack)
            discard = []

    if message.content == '!r' or message.content == "!правила":
        """Показать правила игры"""
        ch = await client.start_private_message(member)
        # Разделено на 3 сообщения, из-за лимита на количество символов в discord
        await client.send_message(ch, '''
            **Fallacymania — правила игры**
    Данные правила являются минимальной модификацией оригинальных правил - http://gdurl.com/z6s0A/download с учётом особенностей игры с чатботом в discord.

    Для игры нужно 3–20 игроков (рекомендуется 4–12). Игроки разбиваются на 2 группы: спорщики (2–10 игроков) и отгадчики (1–10 игроков). Ведущий может играть в любой из этих ролей.
    Чтобы войти в группу спорщиков надо написать в чат ```!d```, чтобы в группу отгадчиков ```!g```
    Игра требует наличия микрофона у каждого игрока. Все игроки (спорщики и отгадчики) должны быть в одном аудиоканале.

**Подготовка к игре**
    1. Некоторые (или все) спорщики определяют для себя тезисы, которые они будут отстаивать с использованием софизмов. Тезисы можно написать в общий чат, а можно проговорить словами.
    Задача спорщиков — проталкивать собственные тезисы, а также комментировать (поддерживать или опровергать) сказанное другими спорщиками, но с использованием софизмов со своих карт
    Примеры тезисов:
        Инопланетных цивилизаций не существует;
        Никого невозможно в чём-то убедить при помощи софизмов;
        Зелёный цвет красивее, чем красный.
    2. Спорщики могут объединяться в группы, когда несколько человек отстаивают один и тот же тезис. Те спорщики, которые не взяли себе никакой тезис, используют софизмы только для ответов на сказанное другими.
    3. Для начала игры следует написать в чат ```!s```После этого чат-бот раздаст спорщикам по 5 карточек с софизмами, а отгадчикам лист с софизмами
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
    8. За каждый угаданный софизм отгадчик получает __1 очко__. Очки начисляет себе отгадчик сам, для этого он должен написать в чат ```+``` или ```-```, а спорщик откладывает угаданную карту софизма в сброс и берёт себе новую из колоды, вводя номер софизма в чат например ```22``` Если колода заканчивается, то сброс перетасовывается и становится новой колодой.
    9. Спорщик больше не может использовать тот софизм, который ушёл в сброс, но может пользоваться новым полученным софизмом.
    10. Если отгадчик называет не тот софизм, который использовал спорщик, то он теряет 1 карту попытки . Когда карты попыток у отгадчика заканчиваются, __он начинает терять по 1 очку__ за каждую неправильную попытку, для этого он должен написать в чат ```.-```, если ошибся и отнял у себя лишнюю попытку, то можно вернуть попытку с помощью ```.+```
    11. Игра продолжается __20 минут__. В конце игры среди отгадчиков определяется победитель по количеству набранных очков.''')


def current_score(guesser_points, guesser_attempts):
    msg = "Общий счёт (Игрок: очки | попытки):\n"
    for guesser in guesser_points:
        msg += "**{0}**: {1} | {2} \n".format(guesser.name, guesser_points[guesser], guesser_attempts[guesser])
    return msg


client.run(token)
