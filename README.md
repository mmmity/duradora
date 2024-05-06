# duradora
An API for music streaming service
![coverage](coverage.svg)

МФТИ, Практикум Python 2024, 1 курс, Б05-328, Канухин Александр

## Описание
Сервер для музыкального стримингового сервиса, написанный на Python. Хранит аудиофайлы и их метаданные, поддерживает регистрацию пользователей, загрузку аудиофайлов с метаданными от админов, стриминг аудиофайлов по id, составление плейлистов от пользователей. Всё через REST API.

## Варианты использования
### Базовый функционал
Загрузка аудиофайла и стриминг аудиофайла с клиента. Добавление метаданных, хранение данных о треках в базе данных. Регистрация и авторизация пользователей, ограничение доступа к некоторому функционалу для неавторизованных и неадминов.

### Дополнительный функционал
Поиск по имеющимся трекам, составление плейлистов для пользователей. Модификаторы доступа к плейлистам: публичные/приватные/по ссылке. Простенький клиент для тестирования.

## Стек
- Python 3.12
- fastapi
- sqlite

## Зависимости
- [fastapi](https://github.com/tiangolo/fastapi) - фреймворк для создания асинхронных REST API
- [sqlite3](https://docs.python.org/3/library/sqlite3.html) - для базы данных

## Запуск
На своем устройстве:
- `pip install -r requirements.txt`
- `python -m uvicorn duradora:app [--host <your-host> --port <your-port>]
Или собрать образ из Dockerfile и запустить его в Docker

## Эндпоинты
- GET `/docs` - посмотреть в браузере документацию к API в виде SwaggerUI
### Пользователи
#### POST `/register`
 Добавляет нового пользователя. В теле запроса должны содержаться username и password. Возвращает Success если пользователь успешно добавлен и Error в противном случае (например, пользователь уже существовал)
 Пример запроса:
 ```
 curl -X 'POST' 'http://localhost:8000/register' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"username": "mmmity", "password": "ilovedora"}'
 ```
#### POST `/login`
Пытается авторизоваться. Обязательные параметры - username и password, также есть необязательные, сгенерированные средствами fastapi для аутентификации, они ни на что не влияют.
В случае успешной авторизации возвращает JWT для доступа к авторизованной зоне, иначе ошибку.
Пример запроса:
```
curl -X 'POST' 'http://localhost:8000/login' -H 'accept: application/json' -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=mmmity&password=ilovedora'
```

Для доступа к авторизованной зоне нужно добавлять заголовок `Authorization: Bearer <your-jwt>`
#### POST `/user/update`
Меняет права пользователя, доступна только админу. Принимает username, password, is_admin - пароль и права заменяют старые. Возвращает Success или Error
Пример запроса:
```
curl -X 'POST' 'http://localhost:8000/user/update' -H 'accept: application/json' -H 'Authorization: Bearer <your-jwt>' -H 'Content-Type: application/json' -d '{"username": "mmmity", "password": "ilovedora", "is_admin": true}'
```
### Треки
#### POST `/track/add`
Добавляет новый трек. Параметры - title, artists (строки) и file (файл). Доступна только админу. Все параметры опциональные и их можно загрузить позднее. Возвращает либо идентификатор нового трека, либо описание ошибки, если такая возникла.
Пример запроса:
```
curl -X 'POST' 'http://localhost:8000/track/add?title=Duradora&artists=Dora' -H 'accept: application/json' -H 'Authorization: Bearer <your-jwt>' -H 'Content-Type: multipart/form-data' -F 'file=@duradora.mp3;type=audio/mpeg'
```
#### POST `/track/update`
Обновляет метаданные и файл уже существующего трека. Работает аналогично `/track/add`, но требует еще и uuid трека. Доступна только админу.
#### GET `/track`
Возвращает метаданные трека либо описание ошибки. Один параметр - `uuid`. Доступна без авторизации.
Пример запроса:
```
curl -X 'GET' 'http://localhost:8000/track?uuid=your-uuid' -H 'accept: application/json'
```
#### GET `/stream`
Устанавливает соединение для стриминга трека либо возвращает ошибку. Один параметр - `uuid`. Доступна без авторизации.
Пример запроса:
```
curl -X 'GET' 'http://localhost:8000/stream?uuid=your-uuid' -H 'accept: application/json'
```
### Плейлисты
Модификаторы доступа: 
- 0 - публичный, доступен всем авторизованным пользователям, отображается в списке плейлистов пользователя
- 1 - по ссылке, не отображается в списке плейлистов пользователя, но доступен всем авторизованным
- 2 - приватный, доступен только создателю и админу
#### POST `/playlist`
Создает новый плейлист для авторизованного пользователя. Принимает пользователя, к которому будет привязан, название и модификатор доступа. Возвращает идентификатор плейлиста или описание ошибки. Админ может привязывать плейлист к кому угодно, остальные пользователи только сами к себе.
Пример запроса:
```
curl -X 'POST' 'http://localhost:8000/playlist' -H 'accept: application/json' -H 'Authorization: Bearer <your-jwt>' -H 'Content-Type: application/json' -d '{"creator": "mmmity","title": "dora songs","access": 0}'
```
#### POST `/playlist/add_track`
Добавляет трек id в плейлист. Может быть выполнен только пользователем, к которому плейлист привязан, либо админом. Принимает uuid плейлиста и uuid трека. Возвращает либо success, либо описание ошибки
Пример запроса:
```
curl -X 'POST' 'http://localhost:8000/playlist/add_track?playlist_id=playlist-id&track_id=track-id' -H 'accept: application/json' -H 'Authorization: Bearer <your-jwt>'
```
#### POST `/playlist/remove_track?id=`
Удаляет трек id из плейлиста. Возвращает либо success, либо описание ошибки. Работает аналогично `/playlist/add_track`
#### GET `/playlist`
Выдает список треков в плейлисте, если он не приватный. Доступна только авторизованным пользователям. Если приватный, то доступна только создателю плейлиста либо админу. Возвращает список треков либо описание ошибки.
Пример запроса:
```
curl -X 'GET' 'http://localhost:8000/playlist?playlist_id=playlist-id' -H 'accept: application/json' -H 'Authorization: Bearer <youd-jwt>'
```
#### GET `/user/{username}/playlists`
Доступна только авторизованным пользователям. Выдает список публичных плейлистов у пользователя username (для админа или самого username показывает все) либо описание ошибки.
Пример запроса:
```
curl -X 'GET' 'http://localhost:8000/user/mmmity/playlists' -H 'accept: application/json' -H 'Authorization: Bearer <your-jwt>'
```
#### GET `/playlist/{playlist_id}/search`
Пытается провести поиск по плейлисту playlist_id и возвращает результаты. Принимает параметром строку search_str, возвращает все треки, в названии которых она есть.
Пример запроса:
```
curl -X 'GET' 'http://localhost:8000/playlist/search?playlist_id=bb469922-14df-4ec8-98ec-e12e6e0b77fe&search_str=Doradu' -H 'accept: application/json' -H 'Authorization: Bearer <your-jwt>'
```


## Архитектура
Основной функционал реализуется через методы FastAPI, к нему не нужна дополнительная обертка. Нужны:

### Классы баз данных
UserController, TrackController, PlaylistController - классы, которые содержат методы для работы с соответствующими таблицами SQL (примеры - `UserController.add_user(...)`, `PlaylistController.search(...)`)
Также датаклассы User, Track, Playlist, содержащие параметры соответствующих объектов.

### TrackStream
Класс, содержащий файл трека и метод `iter()`, который делает `yield` новой порции данных для того, чтобы возвращать созданный из него `fastapi.responses.StreamingResponse`

### Config
Класс, который умеет парсить конфигурационные файлы (toml, например), и содержит все нужные константы.

### Auth
Класс, содержащий методы для авторизации пользователей

### TrackHandler
Класс, содержащий методы для добавления треков в файловую систему и базу данных и работы с ними

### PlaylistHandler
Класс, содержащий методы для работы с плейлистами

### UserHandler
Класс, содержащий вспомогательные методы для работы с пользователями
