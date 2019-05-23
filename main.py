import configparser

import discord
import sys
import logging

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
started = False


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
        self.text = "fww"
        await self.__reset__()

    async def on_ready(self):
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)

        print('------')
        await self.test()

    async def _test_(self):
        await self.__reset__()
        self.paused = True
        print(self.paused)
        await self.__reset__()
        print(self.paused)

    async def __reset__(self):
        self.paused = False
        self.debaters_list = []
        self.debater_names = []
        self.guesser_attempts = {}
        self.guessers_list = []
        self.guesser_names = []
        self.guesser_points = []
        self.guesser_points = {}
        self.guesser_last_turn = {}
        self.guesser_messages = 0
        print(self.paused)


client = DiscordClient()
client.run(token)
