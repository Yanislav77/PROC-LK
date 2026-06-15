# PROC-LK

Автоматизированные тесты для препродакшн-стенда личного кабинета [payment.center](https://preprodcabinet-alt.payment.center/new).

## Стек

| Слой | Инструмент |
|---|---|
| UI / E2E | Playwright + pytest-playwright |
| API | requests |
| Раннер | pytest |
| Отчёты | Allure |
| XLSX-парсинг | openpyxl |

## Структура проекта

```
PROC-LK/
├── api_clients/          # HTTP-клиенты
│   ├── base_client.py
│   ├── auth_client.py
│   ├── transactions_client.py
│   ├── exports_client.py
│   └── account_client.py
├── pages/                # Page Object Model
│   ├── components/       # переиспользуемые компоненты (sidebar)
│   ├── login_page.py
│   ├── transactions_page.py
│   └── transaction_detail_page.py
├── tests/
│   ├── api/              # API-тесты
│   │   ├── test_auth.py
│   │   ├── test_transactions.py
│   │   ├── test_account_services.py
│   │   ├── test_exports.py
│   │   └── test_transaction_actions.py
│   └── ui/               # UI / E2E тесты
│       ├── test_login.py
│       └── test_transactions.py
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

### API (42 теста)

| Модуль | Тесты | Описание |
|---|---|---|
| **Auth** | 3 | логин, неверный пароль, отсутствие логина |
| **Transactions** | 12 | список, пагинация, фильтры, `payment_method`, `p2p_bankdetails`, `payed_range` |
| **Account Services** | 7 | `POST /api/v4/account/services/` — терминалы по партнёрам, структура ответа, edge cases |
| **Exports** | 12 | создание CSV/XLSX, опрос статуса, скачивание, проверка колонок `Terminal ID` / `Terminal name` |
| **Transaction Actions** | 8 | возврат, отправка вебхука, запрос статуса — успех и ошибки |

### UI (16 тестов)

| Модуль | Тесты | Описание |
|---|---|---|
| **Login** | 4 | успешный вход, неверные креды, ссылка «Забыли пароль» |
| **Transactions** | 9 | загрузка таблицы, табы, кнопки экспорта, фильтры, детализация |
| **Navigation** | 3 | сайдбар, переходы между страницами |

## Известные расхождения с документацией

| Эндпоинт | Документация | Факт |
|---|---|---|
| `POST /api/v4/exports/` | статус `200` | возвращает `201` |
| `GET /api/v4/exports/{id}/` | статусы `RUNNING / DONE / FAILED` | также бывает `PENDING` |
