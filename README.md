# VPN Access Service

Сервис управления VPN доступами (VLESS/Reality).

## Архитектура

```
app/
├── domain/                         # Ядро — интерфейсы, модели, исключения
│   ├── exceptions/base.py          # AppException иерархия
│   ├── interface/                  # LoggerPort, AbstractTokenService
│   ├── models/models.py            # Pydantic read-models (User, Subscribe, TokenPair)
│   └── repositories/               # Абстрактные репозитории + UoW
│
├── application/                    # Use cases — вся бизнес-логика
│   └── use_cases/
│       ├── auth.py                 # AuthService: register, login, refresh
│       ├── users.py                # UserService: list, activate, change_password
│       └── subscribes.py          # SubscribeService: CRUD + /me
│
├── infrastructure/                 # Адаптеры
│   ├── config/config.py            # Settings (split by domain)
│   ├── database/
│   │   ├── orm/models.py           # SQLAlchemy ORM (Users, Subscribes)
│   │   ├── repositories/vpn.py    # SQL реализации репозиториев
│   │   ├── uow.py                  # UnitOfWork + UnitOfWorkFactory
│   │   ├── engine.py               # async engine + session_maker
│   │   └── dependencies.py        # FastAPI DI: get_uow
│   ├── security/
│   │   ├── jwt.py                  # JoseTokenService
│   │   └── password.py            # BcryptPasswordHasher (pwdlib)
│   └── logging/                   # LoggerPort реализация + request_id ctx
│
└── presentation/fastapi/
    ├── main.py                     # create_application(), lifespan
    ├── dependencies.py            # FastAPI DI: сервисы + get_current_user
    ├── middleware/                 # ExceptionMiddleware, RequestIdMiddleware
    ├── routers/                    # auth.py, users.py, subscribes.py
    └── schemas/schemas.py         # Request/Response Pydantic schemas
```

## API

### Auth (публичные)
| Method | Endpoint | Описание |
|--------|----------|----------|
| POST | `/api/v1/auth/register` | Регистрация (аккаунт деактивирован) |
| POST | `/api/v1/auth/login` | Логин → JWT пара |
| POST | `/api/v1/auth/refresh` | Обновить токены |
| GET  | `/api/v1/auth/me` | Текущий пользователь |
| POST | `/api/v1/auth/logout` | Выход (client-side) |

### Users (авторизация обязательна)
| Method | Endpoint | Доступ | Описание |
|--------|----------|--------|----------|
| GET  | `/api/v1/users/me` | user | Свой профиль |
| GET  | `/api/v1/users/` | superuser | Все пользователи |
| GET  | `/api/v1/users/pending` | superuser | Ожидают активации |
| PATCH | `/api/v1/users/{id}/activate` | superuser | Активировать юзера |
| PATCH | `/api/v1/users/change-password` | superuser | Сменить пароль юзеру |

### Subscribes
| Method | Endpoint | Доступ | Описание |
|--------|----------|--------|----------|
| GET  | `/api/v1/subscribes/me` | user | Мои подписки с готовым payload |
| GET  | `/api/v1/subscribes/` | superuser | Все подписки |
| GET  | `/api/v1/subscribes/user/{user_id}` | superuser | Подписки юзера |
| POST | `/api/v1/subscribes/` | superuser | Выдать подписку |
| PATCH | `/api/v1/subscribes/{id}` | superuser | Обновить подписку |
| DELETE | `/api/v1/subscribes/{id}` | superuser | Удалить подписку |

## Payload

Payload хранится как шаблон с плейсхолдерами `{ip}` и `{port}`.  
При запросе `/subscribes/me` они подставляются автоматически:

```
# Шаблон при создании:
vless://60975a6b-8eb9-413a-b555-7a9e024083d8@{ip}:{port}?security=reality&sni=max.ru&...#rkn-pidarasi-leo-wl

# Что получает юзер:
vless://60975a6b-8eb9-413a-b555-7a9e024083d8@185.23.11.4:443?security=reality&sni=max.ru&...#rkn-pidarasi-leo-wl
```

## Запуск

```bash
cp .env.example .env          # заполнить переменные
cd compose
docker compose up -d

# первая миграция
docker exec backend alembic upgrade head

# создать суперюзера вручную через adminer (http://localhost:8080)
# или через psql:
# UPDATE users SET is_superuser=true, is_active=true WHERE email='admin@example.com';
```

## Docs

```
http://localhost:8000/vpn-service/docs
```
