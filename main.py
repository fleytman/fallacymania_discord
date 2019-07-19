import configparser
import logging
import random
import sys
from copy import deepcopy

import discord

import GameTimer


def load_config():
    c = configparser.ConfigParser()
    c.read('config.ini')
    try:
        time = c.getint('game', 'time')
    except ValueError:
        logger.error(
            "В config.ini неверно указано значение time. Значение установлено на 1200")
        time = 1200
    return {'t': time}


class DiscordClient(discord.Client):
    def __init__(self, **kwargs):
        discord.Client.__init__(self, **kwargs)

        self.paused = False
        self.debaters_list = []
        self.debater_names = []
        self.guesser_attempts = {}
        self.guessers_list = []
        self.guesser_names = []
        self.guesser_points = {}
        self.guesser_last_turn = {}
        self.guesser_messages = 0

        self.debater_cards = {}
        self.pack = {}
        self.discard = []

        try:
            config = load_config()
            self.t = config["t"]
        except:
            self.t = 1200
            logger.error(
                "Файл config.ini отсуствует или содержит некорретные данные, были загруженны настройки по умолчанию.")

        print(self.t)
        self.game_timer = GameTimer.RenewableTimer(self.t, self.end)

        self.started = False

    async def on_ready(self):
        await self.__reset__()
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)

        print('------')

    async def __reset__(self):
        self.paused = False
        self.debaters_list.clear()
        self.debater_names.clear()
        self.guesser_attempts.clear()
        self.guessers_list.clear()
        self.guesser_names.clear()
        self.guesser_points.clear()
        self.guesser_last_turn.clear()
        self.guesser_messages = 0

    def end(self):
        self.loop.create_task(self.end_game())
        self.loop.create_task(self.__reset__())

    async def end_game(self):
        self.started = False

        max_points = 0
        winners = []
        # Определяет отгадчика с максимальным количеством очков
        for guesser in self.guesser_points:
            if self.guesser_points[guesser] > max_points:
                max_points = self.guesser_points[guesser]
                winner = guesser
                winners = [winner.name]
            elif self.guesser_points[guesser] == max_points:
                winners.append(guesser.name)

        if len(self.guesser_points) < 2:
            end_game_message = "Победитель **{}**".format(guesser.name)
        elif len(winners) < 2:
            end_game_message = "Победитель **{}**".format(winner.name)
        elif len(winners) > 1:
            end_game_message = "Победители {}".format("**" + "**, **".join(winners) + "**")

        score = self.current_score()

        for user in self.guessers_list + self.debaters_list:
            await user.send("{0}\n{1}\nИгра закончилась".format(score, end_game_message))
        print("Игра закончилась")

    def current_score(self):
        score_message = "Общий счёт (Игрок: очки | попытки):\n"
        for guesser in self.guesser_points:
            score_message += "**{0}**: {1} | {2} \n".format(guesser.name, self.guesser_points[guesser],
                                                            self.guesser_attempts[guesser])
        return score_message

    async def add_guesser(self, member):
        if member not in self.guessers_list:
            self.guessers_list.append(member)
            self.guesser_names.append(member.name)
            guessers = "**" + "**, **".join(self.guesser_names) + "**"

            for guesser in self.guessers_list:
                if guesser != member:
                    await guesser.send(
                        "Игрок {0} добавлен в группу отгадчиков\n"
                        "Группа отгадчиков: {1}\n"
                        "Общее количество отгадчиков: **{2}**".format(member.name, guessers,
                                                                      len(self.guessers_list)))
                else:
                    await guesser.send(
                        "Вы добавлены в группу отгадчиков\n"
                        "Группа отгадчиков: {0}\n"
                        "Общее количество отгадчиков: **{1}**".format(guessers,
                                                                      len(self.guessers_list)))
        elif member in self.guessers_list:
            guessers = "**" + "**, **".join(self.guesser_names) + "**"
            await member.send(
                'Вы уже в группе отгадчиков \nГруппа отгадчиков: {0}\nОбщее количество '
                'отгадчиков: **{1}**'.format(guessers, len(self.guessers_list)))

    async def remove_guesser(self, member):
        if member in self.guessers_list:
            self.guessers_list.remove(member)
            self.guesser_names.remove(member.name)
            guessers = "**" + "**, **".join(self.guesser_names) + "**"
            await member.send(
                "Вы удалены из группы отгадчиков\n"
                "Группа отгадчиков: {0}\n"
                "Общее количество отгадчиков: **{1}**".format(guessers, len(self.guessers_list)))
            for guesser in self.guessers_list:
                await guesser.send(
                    "Игрок {0} удалён из группы отгадчиков\n"
                    "Группа отгадчиков: {1}\n"
                    "Общее количество отгадчиков: **{2}**".format(member.name, guessers,
                                                                  len(self.guessers_list)))

    async def add_debater(self, member):
        if member not in self.debaters_list:
            self.debaters_list.append(member)
            self.debater_names.append(member.name)
            debaters = "**" + "**, **".join(self.debater_names) + "**"

            for debater in self.debaters_list:
                if debater != member:
                    await debater.send(
                        "Игрок {0} добавлен в группу спорщиков\n"
                        "Группа спорщиков: {1}\n"
                        "Общее количество спорщиков: **{2}**".format(member.name, debaters,
                                                                     len(self.debaters_list)))
                else:
                    await debater.send(
                        "Вы добавлены в группу спорщиков\n"
                        "Группа спорщиков: {1}\n"
                        "Общее количество спорщиков: **{2}**".format(member.name, debaters,
                                                                     len(self.debaters_list)))
        elif member in self.debaters_list:
            debaters = "**" + "**, **".join(self.debater_names) + "**"
            await member.send(
                'Вы уже в группе спорщиков \nГруппа спорщиков: {0}\nОбщее количество '
                'спорщиков: **{1}**'.format(debaters, len(self.debaters_list)))

        # we do not want the client to reply to itself
        if member == discord.Client.user:
            return

    async def remove_debater(self, member):
        if member in self.debaters_list:
            self.debaters_list.remove(member)
            self.debater_names.remove(member.name)
            debaters = "**" + "**, **".join(self.debater_names) + "**"
            await member.send(
                "Вы удалены из группы спорщиков\n"
                "Группа спорщиков: {0}\n"
                "Общее количество спорщиков: **{1}**".format(debaters, len(self.debaters_list)))
            for debater in self.debaters_list:
                await debater.send(
                    "Игрок {0} удалён из группы спорщиков\n"
                    "Группа отгадчиков: {1}\n"
                    "Общее количество спорщиков: **{2}**".format(member.name, debaters,
                                                                 len(self.debaters_list)))

    async def on_message(self, message):
        member = message.author
        channel = message.channel

        if message.content == "!help" or message.content == "!h":
            message_to_other_guessers = """```Чат-бот для игры в Fallacymania

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

        "!reset" или "!сброс" - Удаляет всех игроков из групп отгадчиков и спорщиков

        "%номер_софизма%" - Ищет у спорщика софизм по номеру, если находит, то забирает и даёт новый (вбивается без знаков процент)

        "+" или "-" - Даёт или забирает 1 очко у отгадчика. Пока у отгадчика есть попытки "-" забирает 1 попытку, а не 1 очко.

        ".." или "!z" - Отменяет последнее действие отгадчика.
        ```"""

            if not self.started:
                await channel.send(message_to_other_guessers)
            else:
                await member.send(message_to_other_guessers)

        if message.content == "!d" or message.content == "!спорщик":
            await self.add_debater(member)
            await self.remove_guesser(member)

        if message.content == "!g" or message.content == "!отгадчик":
            await client.loop.create_task(self.add_guesser(member))
            await client.loop.create_task(self.remove_debater(member))

        if message.content == "!-g" or message.content == "!-отгадчик":
            await self.remove_guesser(member)

        if message.content == "!-d" or message.content == "!-спорщик":
            await self.client.loop.create_task(self.remove_debater(member))

        # Сбросить параматеры игры
        if message.content == "!reset" or message.content == "!сброс":
            if not self.started:
                if self.debaters_list + self.guessers_list != []:
                    for user in self.debaters_list + self.guessers_list:
                        await user.send("Список игроков и их счёт сброшены")
                else:
                    await member.send("Список игроков и их счёт сброшены")
                await self.__reset__()

            else:
                await member.send(""""Игра уже запущена. Чтобы завершить игру введите "!stop""""")

        # Завершить игру
        if message.content == "!stop" or message.content == "!завершить":
            if self.started:
                self.game_timer.cancel()
                self.end()
            else:
                member.send("Нельзя остановить ещё не запущенную игру")
        #
        # Старт игры
        if message.content == '!s' or message.content == '!старт':
            # Если таймер не запущен и игра не на паузе, есть как минимум 2 спорщика и 1 отгадчик
            if not (self.game_timer.timer.isAlive() or self.paused) and len(self.debaters_list) > 1 and len(
                    self.guessers_list) > 0:
                self.game_timer = GameTimer.RenewableTimer(self.t, self.end)
                self.debater_cards = {}
                self.pack = deepcopy(fallacies)
                self.discard = []
                # Перемешать колоду
                random.shuffle(self.pack)
                # Раздать карты спорщикам
                for debater in self.debaters_list:
                    i = 0
                    card_list = []
                    cards = ""
                    while i < 5:
                        card = self.pack.pop()
                        cards += card
                        card_list.append(card)
                        i += 1
                    await debater.send(cards)
                    self.debater_cards.update({debater: card_list})

                # • если отгадчиков 1-2, каждый берёт по 15 карт попыток;
                # • если отгадчиков 3-4, каждый берёт по 10 карт попыток;
                # • если отгадчиков 5-6, каждый берёт по 8 карт попыток;
                # • если отгадчиков больше 6, то 50 карт попыток делятся поровну между отгадчиками,
                # а остаток убирается обратно в коробку.
                if len(self.guessers_list) < 3:
                    number_attempts = 15
                elif len(self.guessers_list) < 5:
                    number_attempts = 10
                elif len(self.guessers_list) < 7:
                    number_attempts = 8
                elif len(self.guessers_list) > 6:
                    number_attempts = int(50 / len(self.guessers_list))

                for guesser in self.guessers_list:
                    # Раздать лист с софизмами отгадчикам
                    await guesser.send(
                        "http://i.imgur.com/ivEjvmi.png\nhttp://i.imgur.com/BukCpJ7.png\nhttp://i.imgur.com/s4qav82.png")
                    # Установить начальное количество попыток и очков для отгадчиков
                    self.guesser_points.update({guesser: 0})
                    self.guesser_attempts.update({guesser: number_attempts})
                    self.guesser_last_turn.update({guesser: None})

                self.game_timer.start()
                await channel.send("Игра началась")
                self.started = True
            # Если таймер запущен
            elif self.game_timer.timer.isAlive() and not self.paused:
                await channel.send("Таймер уже запущен")
                self.game_timer.pause()
                m, s = divmod(int(self.game_timer.get_actual_time()), 60)
                await channel.send("Осталось {0}м {1}с".format(m, s))
                self.game_timer.resume()
            elif self.paused:
                for user in self.guessers_list + self.debaters_list:
                    m, s = divmod(int(self.game_timer.get_actual_time()), 60)
                    await user.send("Игра продолжается\nОсталось {0}м {1}с".format(m, s))
                self.game_timer.resume()
                self.paused = False

            elif len(self.debaters_list) < 2:
                await channel.send("Нужно указать как минимум 2 спорщиков")
            elif len(self.guessers_list) < 1:
                await channel.send("Нужно указать как минимум 1 отгадчика")

        # Пауза
        if message.content == '!p' or message.content == '!пауза':
            if self.started and not self.paused:
                self.game_timer.pause()
                self.game_timer.get_actual_time()
                self.paused = True

                for user in self.guessers_list + self.debaters_list:
                    m, s = divmod(int(self.game_timer.get_actual_time()), 60)
                    await user.send("Пауза\nОсталось {0}м {1}с".format(m, s))
            elif not self.started:
                await channel.send("Игра ещё не запущена")
            elif self.paused:
                await channel.send("Игра уже на паузе")

        # Выдать лист с софизмом
        if message.content == '!софизмы' or message.content == '*':
            await member.send(
                "http://i.imgur.com/ivEjvmi.png\nhttp://i.imgur.com/BukCpJ7.png\nhttp://i.imgur.com/s4qav82.png")

        # Начиление очков
        if message.content == '+' or message.content == '-':
            if not self.started:
                return await member.send(
                    "Игра не запущенна. Проводить манипуляции со счётом до старта игры нельзя.".format(
                        member))

            if member not in self.guesser_points:
                return await member.send("'+' или '-' отправленное отгадчиком даёт или отнимает очко у "
                                         "этого отгадчика. **{0}** - не отгадчик".format(member))

            if message.content == "+":
                self.guesser_points[member] = self.guesser_points[member] + 1
                self.guesser_last_turn[member] = "plus_point"
                message_to_other_guessers = "Игрок **{0}** получил 1 очко.".format(member.name)
                message_to_member_guesser = "Вы получили 1 очко."
            elif message.content == "-":
                if self.guesser_attempts[member] > 0:
                    self.guesser_attempts[member] = self.guesser_attempts[member] - 1
                    self.guesser_last_turn[member] = "minus_attempt"
                    message_to_other_guessers = "Игрок **{0}** потерял 1 попытку.".format(member.name)
                    message_to_member_guesser = "Вы потеряли 1 попытку.".format(member.name)
                else:
                    self.guesser_points[member] = self.guesser_points[member] - 1
                    self.guesser_last_turn[member] = "minus_point"
                    message_to_other_guessers = "Игрок **{0}** потерял 1 очко.".format(member.name)
                    message_to_member_guesser = "Вы потеряли 1 очко."

            self.guesser_messages += 1
            for guesser in self.guesser_points:
                if guesser != member:
                    await guesser.send("{0} {1}".format(message_to_other_guessers, self.current_score()))
                else:
                    await guesser.send("{0} {1}".format(message_to_member_guesser, self.current_score()))

                # Раздать лист с софизмами после 3х сообщений о счёте
                if self.guesser_messages > 2:
                    await guesser.send(
                        "http://i.imgur.com/ivEjvmi.png\nhttp://i.imgur.com/BukCpJ7.png\nhttp://i.imgur.com/s4qav82.png")
            if self.guesser_messages > 2:
                self.guesser_messages = 0

        # Отмена
        if message.content == '!z' or message.content == '..':
            if not self.started:
                return await member.send("Игра не запущенна. Нельзя отменить последнее действие".format(
                    member))

            elif member not in self.guesser_last_turn:
                return await member.send("Отменить последнее действие может только отгадчик.".format(
                    member))

            elif self.guesser_last_turn[member] is None:
                return await member.send("Вы ещё не совершали никаких действия")

            elif self.guesser_last_turn[member] == "returned":
                return await member.send("Вы уже отменили своё действие. Отменять больше 1 действия подряд нельзя.")

            elif self.guesser_last_turn[member] == "plus_point":
                self.guesser_points[member] = self.guesser_points[member] - 1
                self.guesser_last_turn[member] = "returned"
                message_to_other_players = "Игрок **{0}** отменил своё последнее действие. У него забирается 1 очко.".format(
                    member.name)
                message_to_member_player = "Вы отменили своё последнее действие. У вас забирается 1 очко."

            elif self.guesser_last_turn[member] == "minus_point":
                self.guesser_points[member] = self.guesser_points[member] + 1
                self.guesser_last_turn[member] = "minus_point"
                self.guesser_last_turn[member] = "returned"
                message_to_other_players = "Игрок **{0}** отменил своё последнее действие. Ему возвращается 1 очко.".format(
                    member.name)
                message_to_member_player = "Вы отменили своё последнее действие. Вам возвращается 1 очко."

            elif self.guesser_last_turn[member] == "minus_attempt":
                self.guesser_attempts[member] = self.guesser_attempts[member] + 1
                self.guesser_last_turn[member] = "returned"
                message_to_other_players = "Игрок **{0}** отменил своё последнее действие. Ему возвращается 1 попытка.".format(
                    member.name)
                message_to_member_player = "Вы отменили своё последнее действие. Вам возвращается 1 попытка.".format(
                    member.name)

            for guesser in self.guesser_points:
                ch = await client.start_private_message(guesser)
                if guesser != member:
                    await client.send_message(ch, "{0} {1}".format(message_to_other_players,
                                                                   self.current_score()))
                else:
                    await client.send_message(ch, "{0} {1}".format(message_to_member_player,
                                                                   self.current_score()))

        # Удаляет карту в сброс
        if message.content.isdigit() and len(message.content) < 3 and member in self.debaters_list:
            if len(fallacies) <= int(message.content):
                return await member.send("Номер карточки должен быть не больше {}".format(
                    len(fallacies) - 1))

            so = fallacies[int(message.content)]

            card_list = self.debater_cards.get(member)
            if card_list.count(so) > 0:
                card_list.remove(so)
                card = self.pack.pop()
                card_list.append(card)
                self.discard.append(card)
                await member.send(" ".join(card_list))

            else:
                return await member.send("У вас нет карточки номер {}".format(message.content))

            # Если колода закончилась, то сброшенные карты перемешиваются и становятся колодой
            if not self.pack:
                self.pack = deepcopy(self.discard)
                random.shuffle(self.pack)
                self.discard = []

        if message.content == '!r' or message.content == "!правила":
            """Показать правила игры"""
            # Разделено на 3 сообщения, из-за лимита на количество символов в discord
            await message.channel.send('''
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

            await message.channel.send('''**Ход игры**
        1. Игра идёт в реальном времени. Спорщики говорят фразы в поддержку своего тезиса, а также поддерживают или опровергают тезисы других спорщиков.
        Но всё это должно делаться с использованием софизмов, которые есть у спорщиков на картах.
        2. У спорщиков нет условий победы и поражения; их цель — попрактиковаться использовать софизмы так, чтобы аргументы звучали убедительно.
        3. Спорщики могут говорить в любом порядке; могут как отвечать на реплики других игроков, так и высказывать новые суждения относительно своего тезиса.
        4. Отгадчики смотрят дебаты и пытаются угадать, какие софизмы используют спорщики. Отгадчики соревнуются между собой, кто наберёт больше очков за угаданные софизмы.
        5. Любой из отгадчиков может в любой момент пытаться угадывать софизмы, которые используют спорщики. Для этого отгадчик громко говорит имя спорщика и название софизма, который, как ему кажется, употребил этот спорщик. Спорщик отвечает отгадчику, правильная была догадка или нет.
        6. Отгадчик может пытаться угадать софизмы __только из последней реплики__, сказанной спорщиком.
        Если спорщик уже начал говорить следующую реплику, предыдущие софизмы угадывать нельзя. Тем не менее, можно пытаться угадать последние сказанные софизмы других спорщиков, пока они не начали говорить.
            ''')
            message.channel.send('''
        7. Спорщик может использовать в одной реплике несколько софизмов одновременно из тех, которые есть у него на картах. Отгадчики тоже могут пытаться найти несколько софизмов в одной реплике спорщика.
        8. За каждый угаданный софизм отгадчик получает __1 очко__. Очки начисляет себе отгадчик сам, для этого он должен написать в чат ```+``` или ```-```, а спорщик откладывает угаданную карту софизма в сброс и берёт себе новую из колоды, вводя номер софизма в чат например ```22``` Если колода заканчивается, то сброс перетасовывается и становится новой колодой.
        9. Спорщик больше не может использовать тот софизм, который ушёл в сброс, но может пользоваться новым полученным софизмом.
        10. Если отгадчик называет не тот софизм, который использовал спорщик, то он теряет 1 карту попытки . Когда карты попыток у отгадчика заканчиваются, __он начинает терять по 1 очку__ за каждую неправильную попытку, для этого он должен написать в чат ```.-```, если ошибся и отнял у себя лишнюю попытку, то можно вернуть попытку с помощью ```.+```
        11. Игра продолжается __20 минут__. В конце игры среди отгадчиков определяется победитель по количеству набранных очков.''')


if __name__ == "__main__":
    try:
        with open(file="token.txt", mode="r") as f:
            token = " ".join(f.readline().split())
            if token == "":
                input(
                    'В первую строку файла "token.txt" надо вставить токен.\n'
                    'Нажмите любую клавишу для выхода из программы...\n')
                exit()
    except FileNotFoundError:
        input('Файла "token.txt" нет в директории.\nНажмите любую клавишу для выхода из программы...\n')
        exit()

    try:
        with open(file="fallacies.txt", mode="r") as f:
            fallacies = f.readlines()
    except FileNotFoundError:
        input('Файла "fallacies.txt" нет в директории.\nНажмите любую клавишу для выхода из программы...\n')
        exit()

    # ------------------------------------------------------------------------------
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.ERROR)
    logger.addHandler(stdout_handler)
    # ------------------------------------------------------------------------------
    description = '''Чат-бот для игры в fallacymania'''
    # ------------------------------------------------------------------------------
    # Переменная отвечает за то запущенна ли игра

    client = DiscordClient()
    client.run(token)
