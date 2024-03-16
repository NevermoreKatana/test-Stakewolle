# test-Stakewolle

[![Django CI Тесты](https://github.com/NevermoreKatana/test-Stakewolle/actions/workflows/django.yml/badge.svg)](https://github.com/NevermoreKatana/test-Stakewolle/actions/workflows/django.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/5b8f1dcc4c5248369aa3e45cead2454e)](https://app.codacy.com/gh/NevermoreKatana/test-Stakewolle/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/5b8f1dcc4c5248369aa3e45cead2454e)](https://app.codacy.com/gh/NevermoreKatana/test-Stakewolle/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

# Стек
- Django
- DRF
- Requests
- Pydantic
- drf-yasg(Swagger UI)
- Coverage
- PostgreSQL
- Docker
- Makefile
- Sqlite(Для тестов)

# Установка
Перед началом установки нужно заполнить и создать .env файл, пример заполнения можно взять из .env.example
## Настройка Django сервера
```
SECRET_KEY= Можно сгенерироватьб с помощью команды make secretkey, либо просто написать случайный набор чисел и букв
```
```
DEBUG= True/False, для разработчиков необходимо включить режим Debug
```
## База данных
```
POSTGRES_DB= Название БД
POSTGRES_USER=Имя пользователя БД
POSTGRES_PASSWORD=Пароль пользователя БД
POSTGRES_PORT=Порт для БД
POSTGRES_HOST=Хост для БД (При использовании docker, необходимо написать postgres - ссылка на сервис, который создается в докере)
```
## Настройка почты
```
EMAIL_BACKEND=Указать backend для отправки писем smtp/console 
EMAIL_HOST= Хост провайдера почты
EMAIL_PORT= Порт провайдера почты 
EMAIL_USE_SSL = True/False использовать/не использовать SSl (Узнать у провайдера почты)
EMAIL_HOST_USER=Имя пользователя почты
EMAIL_HOST_PASSWORD=Пароль пользователя почты
```
## Апи ключ для emailhunter.co
```
EH_API_KEY= Апи ключ для emailhunter.co, можно узнать в профиле
```

# Запуск сервера Django - PostgreSQL

```
make docker-build
```

## Документации
Документация созданная с помощью Postman:
- [Документация Postman](https://documenter.getpostman.com/view/29777293/2sA2xnwpYt)
Документация созданная с помощью Swagger:
- [Swagger UI Docs](http://localhost:8000/swagger/)

### Примечание:
### Открыть ссылку на документацию Swagger возможно открыть только при запущенном сервере, если сервер запущен не на localhost:8000 - ничего не получится!

## Тесты
С результатами тестов АПИ можно ознакомиться нажав по бейджу [![Django CI Тесты](https://github.com/NevermoreKatana/test-Stakewolle/actions/workflows/django.yml/badge.svg)](https://github.com/NevermoreKatana/test-Stakewolle/actions/workflows/django.yml) 

С результатами покрытия кода можно ознакомиться кликнув по бейджу[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/5b8f1dcc4c5248369aa3e45cead2454e)](https://app.codacy.com/gh/NevermoreKatana/test-Stakewolle/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

Использовался сервис Codacy

### Миграции выполняются автоматически при каждый раз при запуске контейнера