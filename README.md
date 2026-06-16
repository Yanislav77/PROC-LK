# PROC-LK — Автотесты личного кабинета

Автоматизированные тесты препродакшн-стенда: [preprodcabinet-alt.payment.center](https://preprodcabinet-alt.payment.center/new)

---

## Стек

| Слой | Инструмент |
|---|---|
| UI / E2E | Playwright + pytest-playwright |
| API | requests |
| Раннер | pytest |
| HTML-отчёт | pytest-html (self-contained) |
| XLSX-парсинг | openpyxl |

---

## Быстрый старт

### 1. Клонировать и перейти в папку

```bash
git clone <repo-url>
cd PROC-LK
```

### 2. Создать виртуальное окружение и установить зависимости

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### 3. Создать `.env` из шаблона

```bash
cp .env.example .env
```

Заполнить `.env` реальными данными:

```env
BASE_URL=https://preprodcabinet-alt.payment.center/new
API_BASE_URL=https://preprodcabinet-alt.payment.center/api/v4
TEST_USER_EMAIL=your@email.com
TEST_USER_PASSWORD=yourpassword
HEADLESS=true
VIDEO=false
```

> `HEADLESS=false` — браузер открывается на экране (удобно для отладки).

---

## Запуск тестов

```bash
# все тесты
pytest

# только API-тесты
pytest -m api

# только UI-тесты
pytest -m ui

# smoke-набор (быстрая проверка)
pytest -m smoke

# конкретный файл
pytest tests/ui/transactions/test_transactions_filters.py

# конкретный тест
pytest tests/ui/transactions/test_transactions_filters.py::TestFilterControls::test_filter_label_status_visible
```

---

## HTML-отчёт

После каждого прогона автоматически создаётся новый файл в папке `reports/` — единый самодостаточный HTML, который открывается в браузере без сервера.

Имя файла содержит дату и время запуска:
```
reports/report_2026-06-16_17-25-43.html
```

```bash
# открыть последний отчёт (Windows PowerShell)
start (Get-ChildItem reports\report_*.html | Sort-Object LastWriteTime | Select-Object -Last 1).FullName

# macOS / Linux
open $(ls -t reports/report_*.html | head -1)
```

Что есть в отчёте:
- статус каждого теста (passed / failed / skipped)
- время выполнения
- **описание теста** — кликни на строку теста, описание отобразится прямо внутри
- **скриншот при падении** — тоже встроен в строку теста, без внешних файлов
- трейс ошибки

---

## Запись видео

Включается переменной `VIDEO=true` — видео сохраняются в `reports/videos/` в формате `.webm`.

```bash
# через переменную окружения (добавить в .env или передать напрямую)
VIDEO=true pytest -m ui

# Windows PowerShell
$env:VIDEO="true"; pytest -m ui
```

Каждый прогон создаёт свою папку с тем же timestamp, что и отчёт:
```
reports/
├── report_2026-06-16_17-25-43.html
└── videos/
    └── 2026-06-16_17-25-43/
        └── TestTransactionsTabs__test_switch_to_payouts_tab.webm
```

---

## Структура проекта

```
PROC-LK/
├── api_clients/              # HTTP-клиенты для API-тестов
│   ├── base_client.py
│   ├── auth_client.py
│   ├── transactions_client.py
│   ├── exports_client.py
│   └── account_client.py
│
├── pages/                    # Page Object Model (UI)
│   ├── components/           # переиспользуемые компоненты
│   ├── base_page.py
│   ├── login_page.py
│   ├── transactions_page.py
│   └── transaction_detail_page.py
│
├── tests/
│   ├── api/                  # API-тесты
│   │   ├── test_auth.py
│   │   ├── test_transactions.py
│   │   ├── test_account_services.py
│   │   ├── test_exports.py
│   │   └── test_transaction_actions.py
│   │
│   └── ui/                   # UI / E2E тесты
│       ├── conftest.py        # общие фикстуры: login_page, authenticated_page, скриншоты на падение
│       ├── test_login.py
│       └── transactions/      # все тесты страницы транзакций
│           ├── conftest.py    # фикстура transactions_page
│           ├── test_transactions.py              # загрузка, табы, навигация
│           ├── test_transactions_filters.py      # видимость и контролы фильтров
│           ├── test_transactions_dropdown_content.py  # содержимое dropdown-ов
│           ├── test_transactions_date_picker.py       # датапикеры
│           ├── test_transactions_filter_application.py  # применение фильтров
│           ├── test_transactions_filter_network.py      # сетевые запросы (базовые)
│           ├── test_transactions_filter_network_extended.py  # запросы метод/режим/тип даты
│           ├── test_transactions_table_structure.py    # заголовки и данные таблицы
│           ├── test_transactions_pagination.py         # пагинация
│           ├── test_transactions_export.py             # экспорт CSV/XLSX
│           ├── test_transactions_action_buttons.py     # кнопки действий
│           └── test_transactions_detail.py             # страница детализации
│
├── utils/
│   └── config.py             # загрузка переменных из .env
│
├── reports/                  # генерируется автоматически (gitignored)
│   ├── report.html           # HTML-отчёт последнего прогона
│   ├── screenshots/          # скриншоты упавших тестов
│   └── videos/               # видео (если VIDEO=true)
│
├── .env.example
├── pytest.ini
└── requirements.txt
```

---

## Покрытие

### API (~42 теста)

| Модуль | Что проверяется |
|---|---|
| **Auth** | успешный логин, неверный пароль, отсутствие логина |
| **Transactions** | список, пагинация, фильтры, `payment_method`, `p2p_bankdetails`, `payed_range` |
| **Account Services** | `POST /api/v4/account/services/` — терминалы по партнёрам, структура, edge cases |
| **Exports** | создание CSV/XLSX, опрос статуса, скачивание, проверка колонок |
| **Transaction Actions** | возврат, отправка вебхука, запрос статуса — успех и ошибки |

### UI (~160 тестов)

| Модуль | Что проверяется |
|---|---|
| **Login** | успешный вход, неверные креды, ссылка «Забыли пароль» |
| **Transactions — базовые** | загрузка таблицы, табы (Платежи/Выплаты/Chargeback/Все), кнопки, навигация |
| **Dropdown-контент** | все значения в фильтрах: Статус (8 вариантов), Метод (Card/P2P/APM), Режим (Test/Live), Дата тип, Параметры поиска, Размер страницы |
| **Датапикеры** | дефолт = последние 7 дней, поля кликабельны, ввод с клавиатуры |
| **Применение фильтров** | Статус, диапазон дат, поиск — применение и сброс |
| **Сетевые запросы — базовые** | `status_id__in`, `created__range`, `type__in` при смене вкладок |
| **Сетевые запросы — расширенные** | `method__in`, `payed__range` (тип «Дата оплаты»), режимные фильтры |
| **Структура таблицы** | заголовки 10 столбцов, статус/режим/даты в строках, ссылки с ID |
| **Пагинация** | дефолт size=10, `size=25/50/100` в запросах, переключение страниц |
| **Экспорт** | кнопки CSV/XLSX видимы и активны, оба шлют POST на один endpoint |
| **Кнопки действий** | Запросить статус / Отправить вебхук / Возврат — видимы и disabled без выбора |
| **Детализация** | заголовок, секции, кнопка «Назад», кнопки действий |

---

## Известные расхождения с документацией

| Эндпоинт | Документация | Факт |
|---|---|---|
| `POST /api/v4/exports/` | статус `200` | возвращает `201` |
| `GET /api/v4/exports/{id}/` | статусы `RUNNING / DONE / FAILED` | также бывает `PENDING` |
