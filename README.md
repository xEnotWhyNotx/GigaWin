# GigaWin

Презентация: https://disk.yandex.ru/d/fkZvSP4CzNs7tQ

Документация: https://disk.yandex.ru/i/ai0xQdVga_22Hw

В блокноте research_and_model.ipynb проводилось исследование предостваленных данных и построение модели предсказания аварийных ситуаций.


Инструкция по развертыванию:

Необходимо добавить в папку data файл `11.Выгрузка_ОДПУ_отопление_ВАО_20240522.xlsx`, его не удалось загрузить в ГитХаб из-за ограничения на размер файла в 100mb. 
В папке data лежат данные предоставленные организаторами хакатона, их можно заменить другим набором данных.
Данные должны иметь идентичную структуру. Названия файлов должны быть такими же как и в предоставленном наборе данных.

Развертывание:
1. Собрать Docker образ при помощи команды `docker build -t gigawin:1.0 .`
2. Запустить образ при помощи команды `docker run gigawin:1.0`
3. Сервис бедет доступен по адресу: http://127.0.0.1:8050/

Запуск сервиса занимает достаточно много времяни, так как в процессе запуска сервис обрабатывает предоставленные данные.
Время запуска может варьироваться в пределах от 10 до 60 мин в зависимости от производительности комьпьютера.
