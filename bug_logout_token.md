## Баг: refresh token не инвалидируется после logout

**Среда:** препрод — https://preprodcabinet-alt.payment.center

**Эндпоинты:**
- POST /api/v4/auth/token/ — логин
- POST /api/v4/auth/logout/ — выход
- POST /api/v4/auth/token/refresh/ — обновление токена

---

### Ожидаемое поведение

После успешного logout refresh token должен быть инвалидирован на сервере. Любая попытка использовать его после logout должна возвращать 401 Unauthorized.

### Фактическое поведение

После logout сервер принимает старый refresh token и возвращает новый access token с кодом 200 OK. Пользователь фактически не разлогинивается.

---

### Шаги воспроизведения

**Шаг 1 — Логин:**

POST /api/v4/auth/token/
Body: {"username": "...", "password": "..."}

Результат: 200 OK, в Set-Cookie приходит refreshToken=<TOKEN>

**Шаг 2 — Сохранить значение refreshToken из cookie**

**Шаг 3 — Logout:**

POST /api/v4/auth/logout/
(с cookie refreshToken из шага 1)

Результат: 200 OK
Set-Cookie: refreshToken=""; Max-Age=0; HttpOnly; Path=/api/v4/auth/token/refresh/; SameSite=Lax; Secure

Cookie очищается на клиенте (Max-Age=0) — выглядит корректно.

**Шаг 4 — Refresh старым токеном (отдельная сессия, без session cookie):**

POST /api/v4/auth/token/refresh/
Cookie: refreshToken=<TOKEN из шага 1>

Результат: 200 OK — выдаётся новый access token.

{
  "message": "success",
  "response": {
    "access": "eyJhbGci..."
  }
}

---

### Почему это проблема

Logout только очищает cookie на клиенте через Max-Age=0, но не инвалидирует токен в базе данных/хранилище на сервере. Злоумышленник, перехвативший refresh token до logout (например, из логов, сниффером или XSS), может продолжать получать новые access token после того, как пользователь вышел из системы.

---

### Ожидаемое исправление

При вызове POST /api/v4/auth/logout/ сервер должен добавлять refresh token в blacklist (или удалять из БД). Последующий запрос с этим токеном должен возвращать 401.
