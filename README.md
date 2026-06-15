# PROC-LK

Автоматизированные тесты для препродакшн-стенда личного кабинета [payment.center](https://preprodcabinet-alt.payment.center/new).

## Стек

| Слой | Инструмент |
|------|-----------|
| UI / E2E | Playwright + pytest-playwright |
| API | requests |
| Раннер | pytest |
| Отчёты | Allure |

## Структура проекта

```
PROC-LK/
├── api_clients/          # HTTP-клиенты (auth, transactions)
├── pages/                # Page Object Model
│   └── components/       # переиспользуемые UI-компоненты (sidebar)
├── tests/
│   ├── api/              # API-тесты
│   └── ui/               # UI / E2E тесты
├── fixtures/             # тестовые данные
├── utils/                # конфигурация
├── reports/              # Allure-отчёты (gitignored)
└── conftest.py           # общие фикстуры
```

## Быстрый старт

### 1. Установить зависимости

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Настроить окружение

```bash
cp .env.example .env
```

Заполнить `.env`:

```
BASE_URL=https://preprodcabinet-alt.payment.center/new
API_BASE_URL=https://preprodcabinet-alt.payment.center/api/v4
TEST_USER_EMAIL=your@email.com
TEST_USER_PASSWORD=yourpassword
HEADLESS=true
```

## Запуск тестов

```bash
# все тесты
pytest

# только API
pytest -m api

# только UI
pytest -m ui

# smoke-набор
pytest -m smoke

# с Allure-отчётом
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

## Покрытие

### API (9 тестов)
- **Auth** — логин, неверный пароль, отсутствие логина
- **Transactions** — список с фильтром по дате, пагинация, поля ответа
- **Filters** — партнёры, сервисы, статусы

### UI (16 тестов)
- **Login** — успешный вход, неверные креды, ссылка «Забыли пароль»
- **Transactions** — загрузка таблицы, табы, кнопки экспорта, фильтры
- **Navigation** — сайдбар, переходы между страницами
- **Transaction detail** — открытие по клику, валидация URL
