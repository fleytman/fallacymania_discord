# fallacymania_discord
Чат бот для игры [Fallacymania](http://fallacymania.com/) на [discord](https://discordapp.com/).

На данный реализован весь функционал для игры. Хотя бот сырой, нетестированный и не содержит нужное количество проверок, можно пробовать играть.

Команды:

```?играть тут``` - обязательная команда, устанавливает в какой текстовый канал будут выводить сообщения

```?правила``` - выводит правила

```?спорщики %спорщик2% %спорщик2% %спорщикn%``` - указываются именно имена юзера в чате, чтобы бот мог отправлять в лс

```?отгадчики %отгадчик2% %отгадчик2% %отгадчикn%``` - указываются именно имена юзера в чате, чтобы бот мог отправлять в лс

```?старт``` - если указанно минимальное количество отгадчиков и спорщиков, а также выбран текстовый чат, то запускает таймер

```?пауза``` - приостанавливает таймер игры

```?стоп``` - не реализованно

```?софизм %номер_софизма%``` - ищет у спорщиков софизм по номеру, если находит, то забирает и даёт новый

```?очко +1/-1 %отгадчик%``` - дать или забрать очко у отгадчика

```?попытка +1/-1 %отгдчик%``` - дать или забрать попытку у отгадчика

