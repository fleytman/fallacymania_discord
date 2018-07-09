# fallacymania_discord
Чат бот для игры [Fallacymania](http://fallacymania.com/) на [discord](https://discordapp.com/).

Чуть подробнее про данный чат-бот: [тут](https://fleytman.ru/2017/08/14/fallacymania-for-discord/).

Как разворачивать: [тут](https://github.com/fleytman/fallacymania_discord/wiki/%D0%9A%D0%B0%D0%BA-%D0%B7%D0%B0%D0%BF%D1%83%D1%81%D1%82%D0%B8%D1%82%D1%8C-%D1%87%D0%B0%D1%82-%D0%B1%D0%BE%D1%82-fallacymania_discord-%D0%BD%D0%B0-Windows).

![screenshot](http://i.imgur.com/BzYnAIP.png)

На данный реализован весь функционал игры, бот проходит позитивные кейсы.

Стоит учитывать: бот сырой, на негативные кейсы нетестирован, распространяется "as is".


Команды:

```!h``` или ```!help``` - Выводит данную справку

```!r``` или ```!правила``` - Выводит правила

```*``` или ```!софизмы``` - Отправляет в ответ лист с софизмами

```!d``` или ```!спорщик``` - Добавляет пользователя в группу спорщиков

```!-d``` или ```!-спорщик``` - Удаляет пользователя из группы спорщиков

```!g``` или ```!отгадчик``` - Добавляет пользователя в группу отгадчиков

```!-g``` или ```!-отгадчик``` - Удаляет пользователя из группы отгадчиков

```!s``` или ```!старт``` - Если указано минимальное количество отгадчиков и спорщиков, то запускает таймер игры

```!p``` или ```!пазуа``` - Приостанавливает таймер игры

```!stop``` или ```завершить``` - Завершает игру о останавливает таймер

```!reset``` или ```!сброс``` - Удаляет всех игроков из групп отгадчиков и спорщиков

```%номер_софизма%``` - Ищет у спорщика софизм по номеру, если находит, то забирает и даёт новый

```+``` или ```-```  - Даёт или забирает 1 очко у отгадчика. Пока у отгадчика есть попытки ```-``` забирает 1 попытку, а не 1 очко.

```..``` или ```!z``` - Отменяет последнее действие отгадчика.
