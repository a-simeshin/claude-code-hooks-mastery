# Python Testing Standards

<!-- section:philosophy -->

## Философия тестирования

```
┌─────────────────────────────────────────────────────────────────┐
│           РЕАЛЬНЫЕ ИНТЕГРАЦИОННЫЕ ТЕСТЫ                         │
│      (HTTP через httpx, Postgres/Kafka через testcontainers)    │
│                                                                 │
│    → Основная корзина базовых сценариев                         │
│    → Максимальная стабильность в агентной разработке            │
│    → Ловят РЕАЛЬНЫЕ баги (миграции, схемы, сериализация)        │
└─────────────────────────────────────────────────────────────────┘
                            +
┌─────────────────────────────────────────────────────────────────┐
│           UNIT ТЕСТЫ С PROTOCOL-FAKES / pytest-mock             │
│              (edge cases, ветки валидации)                      │
│                                                                 │
│    → Добить coverage до 80/80 (line + branch)                   │
│    → Edge cases: concurrent updates, retries, partial failures  │
│    → Быстрый feedback loop для domain логики                    │
└─────────────────────────────────────────────────────────────────┘
                            +
┌─────────────────────────────────────────────────────────────────┐
│              PROPERTY-BASED ТЕСТЫ (Hypothesis)                  │
│                                                                 │
│    → Инварианты: round-trip сериализация, идемпотентность       │
│    → Ищут минимальный контрпример автоматически                 │
│    → Один такой тест ловит то, что 50 example-based не ловят    │
└─────────────────────────────────────────────────────────────────┘
```

## Правила написания тестов

### 1. Никогда не мокай БД, очереди, HTTP-серверы

`testcontainers-python` поднимает реальный Postgres/Redis/Kafka в Docker. Mock БД =
тест проходит, миграция падает в проде.

```
Инфраструктура (БД, очереди, HTTP API) → testcontainers / respx
Внутренние сервисы (классы твоего кода) → Protocol-fake или pytest-mock
Время → freezegun / time-machine
Внешние HTTP API (платёжки, gigachat, etc) → respx (httpx) или responses (requests)
```

### 2. Приоритет сценариев

```
┌─────────────────────────────────────────────────────────────────┐
│  1. ПОЗИТИВНЫЕ СЦЕНАРИИ (сначала!)                              │
│     → Happy path: валидный запрос → успешный ответ              │
│     → Основной бизнес-флоу работает end-to-end                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. КРИТИЧЕСКИЕ НЕГАТИВНЫЕ                                      │
│     → 404: ресурс не найден                                     │
│     → 422: ошибки валидации Pydantic                            │
│     → 409: конфликт бизнес-логики                               │
│     → 401/403: unauthorized/forbidden                           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. EDGE CASES (unit + property-based)                          │
│     → Граничные значения через Hypothesis                       │
│     → Concurrent updates, race conditions                       │
│     → Retry/timeout логика                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 3. НЕ пиши в тестах

```python
# ❌ НЕ пиши бенчмарки производительности
def test_create_order_performance():
    start = time.perf_counter()
    for _ in range(1000):
        order_service.create(request)
    duration = time.perf_counter() - start
    assert duration < 5.0  # ❌ Flaky! Зависит от железа CI

# ❌ НЕ тестируй throughput / latency
async def test_api_handles_100_rps(): ...  # ❌ Для locust/k6, не для pytest

# ❌ НЕ мокай свою бизнес-логику
def test_create_order():
    mock_service = Mock()
    mock_service.create.return_value = Mock(id=1)
    result = mock_service.create(Mock())  # ❌ Тестируем мок мока
    assert result.id == 1  # ❌ Бессмысленно

# ✅ Тестируй функциональность
async def test_create_order_with_valid_request_returns_201(client):
    request = build_valid_order_request()

    response = await client.post("/api/orders", json=request)

    assert response.status_code == 201
    assert response.json()["total"] == "300.00"
```

<!-- /section:philosophy -->

---

<!-- section:structure -->

# Part 1: Базовые паттерны

## 1. Naming Convention

Формат: `test_<unit>_<scenario>_<expected>`. Английский для имён, русский OK для docstring.

```python
# Формат: test_method_condition_expectedResult
def test_create_order_with_valid_items_returns_order_with_correct_total(): ...

def test_create_order_with_empty_items_raises_validation_error(): ...

def test_find_by_id_when_order_not_found_raises_not_found_error(): ...

def test_cancel_when_already_shipped_raises_conflict_error(): ...
```

**Файлы:**
- Тестовые файлы зеркалят `src/`: `tests/unit/services/test_order_service.py` для `src/myservice/services/order_service.py`.
- `*_test.py` или `test_*.py` (pytest auto-discovery).

## 2. Arrange-Act-Assert Structure

AAA блоки разделены пустыми строками. Не комментариями `# arrange` — структурой.

```python
# BAD: Сплошная стена кода — не видно где что
def test_create_order():
    customer_id = 1
    items = [OrderItem(product_id=1, quantity=2, price=Decimal("100"))]
    request = OrderCreate(customer_id=customer_id, items=items)
    result = order_service.create(request)
    assert result.id > 0
    assert result.total == Decimal("200")


# GOOD: Чёткие AAA блоки
def test_create_order_with_valid_items_calculates_correct_total():
    """Создание заказа считает итог корректно."""
    # Arrange
    request = OrderCreate(
        customer_id=1,
        items=[OrderItem(product_id=1, quantity=2, price=Decimal("100"))],
    )

    # Act
    result = order_service.create(request)

    # Assert
    assert result.id > 0
    assert result.total == Decimal("200")
```

**Альтернатива — given/when/then через docstring:**
```python
def test_cancel_shipped_order_raises_conflict():
    """
    Given: заказ в статусе SHIPPED
    When: пытаемся отменить
    Then: бросается ConflictError
    """
    order = build_order(status=OrderStatus.SHIPPED)

    with pytest.raises(ConflictError, match="отправленный"):
        order_service.cancel(order.id)
```

## 3. pytest assertions с introspection

Plain `assert`. pytest подставит детали при падении автоматически — никаких `assertEqual`.

```python
# BAD: unittest-style
self.assertEqual(result.total, Decimal("300"))
self.assertIn("error", response.text)
self.assertTrue(order.is_valid())


# GOOD: pytest plain assert + introspection
assert result.total == Decimal("300")
assert "error" in response.text
assert order.is_valid()


# Проверка коллекций
assert len(orders) == 3
assert all(o.status == OrderStatus.PENDING for o in orders)
assert orders[0].id == 1


# Проверка полей объекта — chain not allowed → отдельные assert'ы
assert result is not None
assert result.id > 0
assert result.status == OrderStatus.PENDING


# Проверка ВСЕЙ структуры через ==
assert result.model_dump() == {
    "id": 1,
    "status": "pending",
    "total": "300.00",
    "items_count": 2,
}
```

**Сообщения assert'ов:**
```python
# При сложных проверках добавляй контекст
assert result.id > 0, f"Невалидный ID заказа: {result.id}"
assert response.status_code == 201, (
    f"Expected 201, got {response.status_code}. Body: {response.text}"
)
```

## 4. pytest.raises — проверка исключений

```python
# Простая проверка типа
def test_withdraw_negative_amount_raises():
    with pytest.raises(ValidationError):
        account.withdraw(Decimal("-100"))


# Проверка типа + сообщения через regex
def test_withdraw_negative_amount_raises_with_message():
    with pytest.raises(ValidationError, match=r"должна быть положительной"):
        account.withdraw(Decimal("-100"))


# Доступ к самому исключению для проверки атрибутов
def test_not_found_error_has_entity_info():
    with pytest.raises(NotFoundError) as exc_info:
        order_service.find_by_id(999)

    assert exc_info.value.entity == "Order"
    assert exc_info.value.entity_id == 999
    assert exc_info.value.code == "NOT_FOUND"


# ExceptionGroup — Python 3.11+
def test_validate_order_collects_all_errors():
    with pytest.raises(ExceptionGroup) as exc_info:
        validate_order(invalid_order)

    errors = exc_info.value.exceptions
    assert len(errors) == 3
    assert all(isinstance(e, ValidationError) for e in errors)
```

## 5. pytest.approx — числа с плавающей точкой

```python
# BAD: float равенство — flaky
assert result == 0.1 + 0.2  # ❌ 0.30000000000000004 != 0.3


# GOOD: pytest.approx
def test_calculate_discount():
    result = calculate_discount(price=99.99, percent=15)
    assert result == pytest.approx(84.99, abs=0.01)


# Для коллекций
assert results == pytest.approx([1.1, 2.2, 3.3], rel=1e-3)


# Для Decimal используй точное сравнение, approx не нужен
assert order.total == Decimal("84.99")
```

## 6. Группировка через классы

Тесты одного метода/эндпоинта — в одном классе. Аналог `@Nested` в Java.

```python
class TestOrderService:
    """Тесты для OrderService."""

    class TestCreate:
        """create() — создание заказа."""

        def test_with_valid_items_returns_order(self, order_service: OrderService) -> None:
            """Создание с валидными данными возвращает заказ."""
            request = build_valid_order_request()

            result = order_service.create(request)

            assert result.id > 0
            assert result.status == OrderStatus.PENDING

        def test_with_empty_items_raises_validation_error(
            self, order_service: OrderService
        ) -> None:
            """Пустой список items вызывает ValidationError."""
            request = OrderCreate(customer_id=1, items=[])

            with pytest.raises(ValidationError, match="items"):
                order_service.create(request)

    class TestCancel:
        """cancel() — отмена заказа."""

        def test_pending_order_cancels_successfully(
            self, order_service: OrderService, pending_order: Order
        ) -> None:
            """Отмена pending заказа работает."""
            cancelled = order_service.cancel(pending_order.id)

            assert cancelled.status == OrderStatus.CANCELLED

        def test_shipped_order_raises_conflict(
            self, order_service: OrderService, shipped_order: Order
        ) -> None:
            """Нельзя отменить отправленный."""
            with pytest.raises(ConflictError, match="отправленный"):
                order_service.cancel(shipped_order.id)
```

⚠️ Классы в pytest **не должны иметь** `__init__`. Фикстуры передаются как параметры методов.

<!-- /section:structure -->

---

<!-- section:config -->

# Part 2: pytest Configuration

## 7. pyproject.toml — pytest настройки

```toml
[tool.pytest.ini_options]
addopts = [
    "-ra",                  # показать причины skip/xfail
    "--strict-markers",     # опечатка в @pytest.mark.unti = ошибка, не skip
    "--strict-config",      # опечатка в config = ошибка
    "--showlocals",         # показывать локальные переменные при падении
    "-p", "no:cacheprovider",
]
testpaths = ["tests"]
asyncio_mode = "auto"        # async тесты без @pytest.mark.asyncio
xfail_strict = true          # xfail который вдруг прошёл = ошибка
log_cli = true
log_cli_level = "WARNING"
markers = [
    "unit: быстрые тесты без I/O",
    "integration: тесты с реальными зависимостями (БД, HTTP)",
    "e2e: end-to-end тесты",
    "slow: тесты выполняющиеся > 5 секунд",
]
filterwarnings = [
    "error",                                            # warning → error
    "ignore::DeprecationWarning:pkg_resources.*",       # внешние либы
]
```

**Что даёт каждый флаг:**
- `--strict-markers` — `@pytest.mark.untegration` (опечатка) упадёт с ошибкой, не молчаливо.
- `--strict-config` — неизвестная опция в `pyproject.toml` упадёт.
- `xfail_strict=true` — `xfail` тест который вдруг прошёл = ошибка. Чинит «забытые» xfail.
- `filterwarnings=["error"]` — DeprecationWarning ломает тест. Не даёт коду гнить.

## 8. conftest.py — иерархия

Один conftest.py на уровень. НЕ один гигантский файл.

```
tests/
├── conftest.py             # общие: settings, app, client
├── unit/
│   ├── conftest.py         # моки сервисов
│   └── services/
│       └── test_*.py
├── integration/
│   ├── conftest.py         # БД фикстуры через testcontainers
│   ├── api/
│   │   └── test_*.py
│   └── repositories/
│       └── test_*.py
└── e2e/
    └── conftest.py         # полноценный стек
```

```python
# tests/conftest.py — корень
import pytest
from collections.abc import AsyncIterator
from httpx import ASGITransport, AsyncClient

from myservice.api import create_app
from myservice.config import Settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Настройки для тестов."""
    return Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        secret_key="test-secret",
        debug=True,
    )


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """HTTP-клиент для тестирования API."""
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# tests/integration/conftest.py — фикстуры с реальной БД
@pytest.fixture(scope="session")
def postgres_container():
    """PostgreSQL через testcontainers — один на всю сессию."""
    from testcontainers.postgres import PostgresContainer
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


# tests/integration/api/conftest.py — фикстуры для API тестов
@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """Заголовки авторизации для защищённых эндпоинтов."""
    response = await client.post(
        "/auth/login",
        json={"email": "test@test.com", "password": "secret"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

<!-- /section:config -->

---

<!-- section:fixtures -->

# Part 3: Fixtures

## 9. Fixture Scopes — производительность

Правильный scope = быстрые тесты. Тяжёлые ресурсы создаются **один раз**.

```python
# BAD: Тяжёлая фикстура пересоздаётся на каждый тест (10 минут вместо 30 секунд)
@pytest.fixture
def db_engine():
    engine = create_engine(TEST_DB_URL)  # 500ms каждый раз × 1000 тестов!
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


# GOOD: Тяжёлый ресурс — session scope, изоляция через транзакции
@pytest.fixture(scope="session")
def db_engine():
    """Движок БД — один на всю сессию тестов."""
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine) -> Iterator[Session]:
    """Сессия БД — новая для каждого теста, с откатом транзакции."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()  # Изоляция между тестами
    connection.close()
```

**Справочник scope'ов:**

| Scope | Когда |
|---|---|
| `session` | Один раз на запуск pytest. Docker контейнеры, движки БД. |
| `module` | Один раз на файл с тестами. Тестовые данные внутри файла. |
| `class` | Один раз на тестовый класс. Редко нужен. |
| `function` | На каждый тест (default). Сессии БД, mocks, изменяемые данные. |

## 10. Async Fixtures

```python
# pytest-asyncio с asyncio_mode="auto" — async фикстуры работают без декоратора

@pytest.fixture
async def async_session(async_engine) -> AsyncIterator[AsyncSession]:
    """Async сессия БД с откатом."""
    async with async_engine.connect() as connection:
        async with connection.begin() as transaction:
            session = AsyncSession(
                bind=connection,
                join_transaction_mode="create_savepoint",
                expire_on_commit=False,
            )
            try:
                yield session
            finally:
                await session.close()
                await transaction.rollback()


@pytest.fixture
async def populated_db(async_session: AsyncSession) -> AsyncSession:
    """БД с тестовыми данными."""
    users = [
        UserModel(name=f"User {i}", email=f"user{i}@test.com")
        for i in range(1, 6)
    ]
    async_session.add_all(users)
    await async_session.commit()
    return async_session
```

## 11. Factory Fixtures

Фабрики вместо отдельной фикстуры на каждую комбинацию.

```python
# BAD: Отдельная фикстура для каждого случая — 20 фикстур на 20 вариантов
@pytest.fixture
def active_user():
    return User(name="Ivan", status="active")

@pytest.fixture
def inactive_user():
    return User(name="Petr", status="inactive")

@pytest.fixture
def admin_user():
    return User(name="Admin", status="active", role="admin")
# ... ещё 17 фикстур


# GOOD: Фабричная фикстура — гибкая, компактная
from collections.abc import Callable

@pytest.fixture
def make_user() -> Callable[..., User]:
    """Фабрика пользователей с дефолтами."""
    counter = 0

    def _make_user(
        *,
        name: str = "Test User",
        email: str | None = None,
        status: UserStatus = UserStatus.ACTIVE,
        role: UserRole = UserRole.USER,
    ) -> User:
        nonlocal counter
        counter += 1
        return User(
            id=counter,
            name=name,
            email=email or f"user{counter}@test.com",
            status=status,
            role=role,
        )

    return _make_user


# Использование — компактно
def test_admin_can_delete_user(make_user) -> None:
    admin = make_user(role=UserRole.ADMIN)
    target = make_user(name="To Delete")

    assert admin.can_delete(target) is True


def test_regular_user_cannot_delete(make_user) -> None:
    user = make_user(role=UserRole.USER)
    target = make_user()

    assert user.can_delete(target) is False
```

## 12. Polyfactory — фабрики для Pydantic

Для Pydantic / dataclass / SQLAlchemy моделей лучше использовать `polyfactory` вместо ручных фабрик.

```python
from polyfactory.factories.pydantic_factory import ModelFactory

class UserFactory(ModelFactory[User]):
    """Автоматическая фабрика, генерирует все поля User."""
    __model__ = User

    # Кастомные значения для конкретных полей
    role = UserRole.USER
    status = UserStatus.ACTIVE


def test_create_user():
    user = UserFactory.build()  # все поля заполнены валидными значениями

    assert user.id is not None
    assert "@" in user.email


def test_admin_permissions():
    admin = UserFactory.build(role=UserRole.ADMIN)
    target = UserFactory.build()

    assert admin.can_delete(target)


def test_batch():
    users = UserFactory.batch(size=10)  # 10 пользователей одной командой
    assert len(users) == 10
```

## 13. Cleanup через yield

```python
# GOOD: yield-based cleanup
@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """Временная директория с автоудалением."""
    import tempfile, shutil
    path = Path(tempfile.mkdtemp())
    try:
        yield path
    finally:
        shutil.rmtree(path)


# GOOD: Async cleanup
@pytest.fixture
async def kafka_consumer(kafka_bootstrap: str) -> AsyncIterator[AIOKafkaConsumer]:
    """Kafka consumer с автозакрытием."""
    consumer = AIOKafkaConsumer(
        "orders.events",
        bootstrap_servers=kafka_bootstrap,
        group_id="test-group",
    )
    await consumer.start()
    try:
        yield consumer
    finally:
        await consumer.stop()
```

<!-- /section:fixtures -->

---

<!-- section:parametrize -->

# Part 4: Parametrization

## 14. parametrize вместо копипасты

Один тест, много данных. Аналог JUnit `@ParameterizedTest`.

```python
# BAD: 10 одинаковых тестов
def test_validate_email_valid_standard():
    assert validate_email("user@example.com") is True

def test_validate_email_valid_short():
    assert validate_email("a@b.co") is True

def test_validate_email_missing_at():
    assert validate_email("userexample.com") is False
# ... ещё 7


# GOOD: parametrize с осмысленными ids
@pytest.mark.parametrize(
    ("email", "expected"),
    [
        pytest.param("user@example.com", True, id="standard"),
        pytest.param("a@b.co", True, id="minimal-valid"),
        pytest.param("user+tag@example.com", True, id="with-plus-tag"),
        pytest.param("userexample.com", False, id="missing-at"),
        pytest.param("@example.com", False, id="missing-local-part"),
        pytest.param("user@", False, id="missing-domain"),
        pytest.param("", False, id="empty"),
        pytest.param(" user@example.com ", False, id="with-whitespace"),
    ],
)
def test_validate_email(email: str, expected: bool) -> None:
    """Валидация email для разных входных данных."""
    assert validate_email(email) is expected
```

⚠️ **id обязателен** — в отчётах CI без id увидишь `test_validate_email[user@example.com-True]`,
с id — `test_validate_email[standard]`. Намного читабельнее.

## 15. parametrize с marks

```python
@pytest.mark.parametrize(
    ("amount", "balance", "expected"),
    [
        pytest.param(Decimal("10"), Decimal("100"), Decimal("90"), id="happy_path"),
        pytest.param(Decimal("0"), Decimal("100"), Decimal("100"), id="zero_amount"),
        pytest.param(
            Decimal("-5"),
            Decimal("100"),
            None,
            id="negative_rejected",
            marks=pytest.mark.xfail(reason="negative amount validation TBD", strict=True),
        ),
        pytest.param(
            Decimal("1000000"),
            Decimal("100"),
            None,
            id="insufficient_funds",
            marks=pytest.mark.skip(reason="требует limit-checker"),
        ),
    ],
)
def test_withdraw(amount, balance, expected): ...
```

## 16. Parametrize нескольких аргументов

Каждая `@pytest.mark.parametrize` умножается:

```python
# 3 × 2 = 6 тестов автоматически
@pytest.mark.parametrize("currency", ["USD", "EUR", "RUB"])
@pytest.mark.parametrize("amount", [Decimal("10"), Decimal("100")])
def test_money_construction(currency: str, amount: Decimal) -> None:
    money = Money(amount=amount, currency=currency)
    assert money.amount == amount
    assert money.currency == currency
```

## 17. Indirect parametrize — параметризованные фикстуры

```python
@pytest.fixture
def order_in_status(request) -> Order:
    """Фикстура создающая заказ в указанном статусе."""
    status: OrderStatus = request.param
    return Order(id=1, status=status, items=[], total=Decimal("0"))


@pytest.mark.parametrize(
    "order_in_status",
    [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.SHIPPED],
    indirect=True,
    ids=["pending", "confirmed", "shipped"],
)
def test_order_id_present(order_in_status: Order) -> None:
    assert order_in_status.id == 1
```

<!-- /section:parametrize -->

---

<!-- section:integration -->

# Part 5: Integration Tests

## 18. testcontainers-python — реальные зависимости

```python
# BAD: SQLite вместо Postgres — пропустит баги PG-specific фич
@pytest.fixture(scope="session")
def db():
    return create_engine("sqlite:///:memory:")  # Нет JSON, нет ARRAY, нет GIN индексов


# GOOD: Реальный Postgres через testcontainers
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    """PostgreSQL контейнер — один на сессию (~3 секунды старт)."""
    with PostgresContainer("postgres:16-alpine", driver="psycopg") as container:
        yield container


@pytest.fixture(scope="session")
async def async_engine(postgres_container: PostgresContainer) -> AsyncIterator[AsyncEngine]:
    """Async engine, схема создаётся один раз."""
    url = postgres_container.get_connection_url(driver="asyncpg")
    engine = create_async_engine(url, pool_pre_ping=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def db_session(async_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Сессия с rollback — изоляция между тестами через savepoint."""
    async with async_engine.connect() as connection:
        await connection.begin()
        async with AsyncSession(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        ) as session:
            yield session
        await connection.rollback()
```

**Другие контейнеры:**
```python
from testcontainers.redis import RedisContainer
from testcontainers.kafka import KafkaContainer
from testcontainers.minio import MinioContainer
from testcontainers.localstack import LocalStackContainer  # AWS

@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7-alpine") as container:
        yield container

@pytest.fixture(scope="session")
def kafka_container():
    with KafkaContainer("confluentinc/cp-kafka:7.5.0") as container:
        yield container
```

## 19. httpx AsyncClient — FastAPI in-process

`httpx.AsyncClient` через `ASGITransport` — НЕ requests, НЕ внешний сервер.

```python
# BAD: requests + запущенный сервер
import requests

def test_get_user():
    resp = requests.get("http://localhost:8000/users/1")  # ❌ нужен сервер
    assert resp.status_code == 200


# GOOD: httpx AsyncClient — in-process
import pytest
from httpx import ASGITransport, AsyncClient
from collections.abc import AsyncIterator

from myservice.api import create_app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """HTTP-клиент, работает напрямую с FastAPI без сетевого стека."""
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


async def test_get_user_returns_user_data(client: AsyncClient, populated_db) -> None:
    """Получение пользователя возвращает корректные поля."""
    response = await client.get("/users/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["email"] == "user1@test.com"


async def test_create_user_returns_201(client: AsyncClient) -> None:
    """Создание пользователя возвращает 201."""
    payload = {"name": "Ivan", "email": "ivan@test.com"}

    response = await client.post("/users", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Ivan"
    assert data["email"] == "ivan@test.com"
    assert "id" in data
```

## 20. HTTP Integration Tests

```python
class TestOrdersAPI:
    """Тесты для /api/orders."""

    class TestCreateOrder:
        """POST /api/orders."""

        async def test_with_valid_request_returns_201_and_order(
            self, client: AsyncClient
        ) -> None:
            """Валидный запрос — заказ создан, ответ 201, тело корректно."""
            request = {
                "customer_id": 1,
                "items": [
                    {"product_id": 1, "quantity": 2, "price": "100.00"},
                    {"product_id": 2, "quantity": 1, "price": "200.00"},
                ],
            }

            response = await client.post("/api/orders", json=request)

            assert response.status_code == 201
            data = response.json()
            assert data["id"] > 0
            assert Decimal(data["total"]) == Decimal("400.00")
            assert data["status"] == "pending"

        async def test_with_empty_items_returns_422(self, client: AsyncClient) -> None:
            """Пустой список items — 422 Unprocessable Entity."""
            request = {"customer_id": 1, "items": []}

            response = await client.post("/api/orders", json=request)

            assert response.status_code == 422
            error = response.json()
            assert any("items" in err["loc"] for err in error["detail"])

        async def test_persisted_in_db(
            self, client: AsyncClient, db_session: AsyncSession
        ) -> None:
            """После POST заказ виден в БД."""
            response = await client.post("/api/orders", json=build_valid_request())
            order_id = response.json()["id"]

            from_db = await db_session.get(OrderModel, order_id)

            assert from_db is not None
            assert from_db.id == order_id

    class TestGetOrder:
        """GET /api/orders/{id}."""

        async def test_existing_order_returns_200(
            self, client: AsyncClient, existing_order: Order
        ) -> None:
            response = await client.get(f"/api/orders/{existing_order.id}")

            assert response.status_code == 200
            assert response.json()["id"] == existing_order.id

        async def test_missing_order_returns_404(self, client: AsyncClient) -> None:
            response = await client.get("/api/orders/999999")

            assert response.status_code == 404
            assert response.json()["code"] == "NOT_FOUND"
```

## 21. respx — мокинг внешних HTTP API

Внешние API (платёжки, GigaChat, etc) — `respx` для httpx, `responses` для requests.

```python
# BAD: реальный HTTP к платёжке в тестах — flaky, медленно, может стоить денег
async def test_process_payment(client):
    response = await client.post("/api/orders/1/pay")  # ❌ реальный запрос!


# GOOD: respx для httpx
import respx
from httpx import Response

@respx.mock
async def test_process_payment_when_gateway_returns_success(
    client: AsyncClient, existing_order: Order
) -> None:
    """Успешная оплата через платёжку."""
    payment_route = respx.post("https://gateway.example.com/api/payments").mock(
        return_value=Response(
            200,
            json={"transaction_id": "txn-123", "status": "SUCCESS"},
        )
    )

    response = await client.post(f"/api/orders/{existing_order.id}/pay")

    assert response.status_code == 200
    assert response.json()["status"] == "paid"

    # проверяем что запрос был сделан с правильным телом
    assert payment_route.called
    request = payment_route.calls.last.request
    assert json.loads(request.content)["amount"] == "300.00"


@respx.mock
async def test_process_payment_when_gateway_fails_returns_502(
    client: AsyncClient, existing_order: Order
) -> None:
    """Ошибка платёжки — 502 Bad Gateway."""
    respx.post("https://gateway.example.com/api/payments").mock(
        return_value=Response(500, text="Internal Server Error")
    )

    response = await client.post(f"/api/orders/{existing_order.id}/pay")

    assert response.status_code == 502


@respx.mock
async def test_process_payment_when_gateway_timeout_returns_504(
    client: AsyncClient, existing_order: Order
) -> None:
    """Таймаут платёжки — 504 Gateway Timeout."""
    import httpx
    respx.post("https://gateway.example.com/api/payments").mock(
        side_effect=httpx.TimeoutException("timeout")
    )

    response = await client.post(f"/api/orders/{existing_order.id}/pay")

    assert response.status_code == 504
```

## 22. Database Integration Tests

```python
class TestOrderRepository:
    """Интеграция OrderRepository с реальным Postgres."""

    async def test_save_and_find_by_id(self, db_session: AsyncSession) -> None:
        """Сохранение и чтение по ID."""
        repo = OrderRepository(db_session)
        order = build_order(customer_id=1)

        saved = await repo.save(order)

        found = await repo.find_by_id(saved.id)
        assert found is not None
        assert found.id == saved.id

    async def test_find_by_status_returns_only_matching(
        self, db_session: AsyncSession
    ) -> None:
        """Фильтр по статусу возвращает только совпадающие."""
        repo = OrderRepository(db_session)
        await repo.save(build_order(status=OrderStatus.PENDING))
        await repo.save(build_order(status=OrderStatus.PENDING))
        await repo.save(build_order(status=OrderStatus.SHIPPED))

        pending = await repo.find_by_status(OrderStatus.PENDING)

        assert len(pending) == 2
        assert all(o.status == OrderStatus.PENDING for o in pending)

    async def test_calculate_total_by_customer(self, db_session: AsyncSession) -> None:
        """Агрегация по клиенту."""
        repo = OrderRepository(db_session)
        await repo.save(build_order(customer_id=1, total=Decimal("100")))
        await repo.save(build_order(customer_id=1, total=Decimal("200")))
        await repo.save(build_order(customer_id=2, total=Decimal("500")))

        total = await repo.calculate_total_by_customer(customer_id=1)

        assert total == Decimal("300")
```

<!-- /section:integration -->

---

<!-- section:unit -->

# Part 6: Unit Tests with Mocks

## 23. pytest-mock — mocker fixture

`pytest-mock` даёт `mocker` fixture с авто-cleanup. Лучше чем `unittest.mock` напрямую.

```python
# BAD: unittest.mock с ручным management
from unittest.mock import patch

def test_send_notification():
    with patch("myservice.services.email.send") as mock_send:
        notification_service.notify_user(user)
        mock_send.assert_called_once()


# GOOD: pytest-mock — auto-cleanup, чище
def test_send_notification(mocker: MockerFixture) -> None:
    mock_send = mocker.patch("myservice.services.email.send")

    notification_service.notify_user(user)

    mock_send.assert_called_once()
```

## 24. autospec — обязательно

`Mock(spec=Class)` или `mocker.create_autospec(Class)` — иначе тест не упадёт от рефакторинга сигнатуры.

```python
# BAD: голый Mock — переименуй метод и тест всё равно «зелёный»
def test_create_order():
    repo = Mock()
    repo.save_order_lol_typo.return_value = order  # ❌ Mock проглотит любое имя!
    service = OrderService(repo)
    service.create(request)
    repo.save_order_lol_typo.assert_called()  # ❌ зелёный, но в проде упадёт


# GOOD: autospec — Mock проверяет что метод реально существует
def test_create_order(mocker: MockerFixture) -> None:
    repo = mocker.create_autospec(OrderRepository, spec_set=True)
    repo.save.return_value = order

    service = OrderService(repo)
    service.create(request)

    repo.save.assert_called_once()
    repo.save_order_lol_typo  # ❌ AttributeError — метод не существует
```

## 25. Protocol-based fakes — лучше моков

Часто проще написать простой fake-класс через Protocol чем настраивать Mock.

```python
# Protocol определяет контракт
class OrderRepository(Protocol):
    async def save(self, order: Order) -> Order: ...
    async def find_by_id(self, order_id: int) -> Order | None: ...
    async def find_by_status(self, status: OrderStatus) -> list[Order]: ...


# Простой in-memory fake
class FakeOrderRepository:
    """In-memory fake для тестов — нагляднее моков."""

    def __init__(self) -> None:
        self._storage: dict[int, Order] = {}
        self._next_id = 1

    async def save(self, order: Order) -> Order:
        if order.id == 0:
            order = replace(order, id=self._next_id)
            self._next_id += 1
        self._storage[order.id] = order
        return order

    async def find_by_id(self, order_id: int) -> Order | None:
        return self._storage.get(order_id)

    async def find_by_status(self, status: OrderStatus) -> list[Order]:
        return [o for o in self._storage.values() if o.status == status]


# Тест с fake'ом — читается как обычный код
async def test_create_order_persists_with_pending_status() -> None:
    repo = FakeOrderRepository()
    service = OrderService(repo=repo)

    result = await service.create(build_request())

    assert result.id > 0
    assert result.status == OrderStatus.PENDING
    assert (await repo.find_by_id(result.id)) == result
```

**Когда fake, когда mock:**
- **Fake** — если у зависимости 2-5 методов и логика простая (CRUD).
- **Mock** — если нужно проверить *как именно* был вызван (assert_called_with).

## 26. Edge Cases — то для чего нужен mock

```python
class TestEdgeCases:
    """Edge cases для добивания coverage."""

    async def test_cancel_when_concurrent_update_retries_and_succeeds(
        self, mocker: MockerFixture
    ) -> None:
        """Concurrent update — retry, и со второй попытки успех."""
        repo = mocker.create_autospec(OrderRepository, spec_set=True)
        order = build_order(status=OrderStatus.PENDING)
        repo.find_by_id.return_value = order
        repo.save.side_effect = [
            OptimisticLockError("Concurrent update"),
            replace(order, status=OrderStatus.CANCELLED),
        ]

        service = OrderService(repo=repo)
        result = await service.cancel(order.id)

        assert result.status == OrderStatus.CANCELLED
        assert repo.save.call_count == 2

    async def test_create_order_when_notification_fails_still_saves_order(
        self, mocker: MockerFixture
    ) -> None:
        """Падение нотификации не ломает создание заказа."""
        repo = FakeOrderRepository()
        notifier = mocker.create_autospec(NotificationService, spec_set=True)
        notifier.send_order_created.side_effect = NotifierError("email service down")

        service = OrderService(repo=repo, notifier=notifier)
        result = await service.create(build_request())

        assert result is not None  # заказ сохранён несмотря на падение notifier
        assert (await repo.find_by_id(result.id)) is not None

    async def test_partial_payment_updates_remaining_amount(
        self, mocker: MockerFixture
    ) -> None:
        """Частичная оплата обновляет remaining_amount."""
        repo = FakeOrderRepository()
        order = await repo.save(build_order(total=Decimal("1000")))
        gateway = mocker.create_autospec(PaymentGateway, spec_set=True)
        gateway.charge.return_value = PaymentResult(
            charged=Decimal("500"),
            status=PaymentStatus.PARTIAL,
        )

        service = OrderService(repo=repo, gateway=gateway)
        await service.process_payment(order.id)

        updated = await repo.find_by_id(order.id)
        assert updated.remaining_amount == Decimal("500")
```

## 27. freezegun — заморозка времени

```python
from freezegun import freeze_time

@freeze_time("2026-01-15 10:00:00")
def test_create_order_sets_created_at_to_now():
    """created_at = текущее время."""
    order = order_service.create(request)
    assert order.created_at == datetime(2026, 1, 15, 10, 0, 0)


def test_token_expires_after_one_hour():
    """JWT токен истекает через час."""
    with freeze_time("2026-01-15 10:00:00"):
        token = auth_service.create_token(user_id=1)

    with freeze_time("2026-01-15 11:00:01"):
        with pytest.raises(TokenExpiredError):
            auth_service.verify(token)


# Сдвиг времени внутри теста
def test_billing_cycle():
    with freeze_time("2026-01-01") as frozen:
        subscription = create_subscription(user_id=1)

        frozen.tick(timedelta(days=30))  # +30 дней
        billing_service.process_renewal(subscription.id)

        assert subscription.next_billing == datetime(2026, 3, 2)
```

⚠️ Альтернатива — `time-machine`. Быстрее на больших проектах, тот же API.

<!-- /section:unit -->

---

<!-- section:property -->

# Part 7: Property-Based Testing (Hypothesis)

## 28. Зачем property-based

Hypothesis генерирует тысячи входов, ищет минимальный контрпример, сохраняет регрессионные кейсы в `.hypothesis/`. Один такой тест ловит то, что 50 example-based не поймают.

**Использовать для:**
- Round-trip сериализация (`from_json(to_json(x)) == x`)
- Идемпотентность (`f(f(x)) == f(x)`)
- Монотонность (`a < b → f(a) <= f(b)`)
- Симметрия (`merge(a, b) == merge(b, a)`)
- Парсинг (`parse(stringify(x)) == x`)
- Инварианты бизнес-логики

```python
from hypothesis import given, strategies as st

# Round-trip
@given(st.decimals(min_value=0, max_value=Decimal("1_000_000"), places=2))
def test_money_serialization_round_trip(amount: Decimal) -> None:
    """Money → JSON → Money сохраняет значение."""
    money = Money(amount=amount, currency="USD")

    serialized = money.to_json()
    restored = Money.from_json(serialized)

    assert restored == money


# Идемпотентность
@given(st.text())
def test_normalize_email_is_idempotent(email: str) -> None:
    """normalize(normalize(x)) == normalize(x)."""
    once = normalize_email(email)
    twice = normalize_email(once)

    assert once == twice


# Инвариант
@given(
    items=st.lists(
        st.builds(
            OrderItem,
            quantity=st.integers(min_value=1, max_value=100),
            price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("10000"), places=2),
        ),
        min_size=1,
        max_size=20,
    ),
)
def test_order_total_equals_sum_of_items(items: list[OrderItem]) -> None:
    """Total всегда == сумма позиций × цен."""
    order = Order(items=items)

    expected = sum((item.price * item.quantity for item in items), Decimal("0"))
    assert order.calculate_total() == expected
```

## 29. Strategies — генераторы данных

```python
from hypothesis import strategies as st

# Базовые
st.integers(min_value=0, max_value=100)
st.floats(allow_nan=False, allow_infinity=False, min_value=0, max_value=1e9)
st.decimals(places=2)
st.text(min_size=1, max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126))
st.booleans()
st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 31))
st.datetimes(timezones=st.just(timezone.utc))
st.uuids()
st.emails()
st.ip_addresses(v=4)
st.from_regex(r"^[A-Z]{3}-\d{4}$", fullmatch=True)

# Композиция
st.lists(st.integers(), min_size=1, max_size=10)
st.dictionaries(keys=st.text(), values=st.integers(), min_size=1)
st.sets(st.integers())
st.tuples(st.text(), st.integers())

# st.builds — генерация dataclass/Pydantic
order_strategy = st.builds(
    Order,
    customer_id=st.integers(min_value=1),
    items=st.lists(item_strategy, min_size=1, max_size=20),
)

# Свои композитные стратегии
@st.composite
def valid_email_strategy(draw):
    """Кастомная стратегия для валидных email."""
    local = draw(st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=20))
    domain = draw(st.sampled_from(["example.com", "test.io", "domain.org"]))
    return f"{local}@{domain}"
```

## 30. Settings и регрессионные кейсы

```python
from hypothesis import given, settings, example

@given(st.decimals(min_value=0, max_value=Decimal("1_000_000"), places=2))
@settings(max_examples=500, deadline=None)  # больше примеров, без таймаута
@example(amount=Decimal("0"))                # обязательно проверить ноль
@example(amount=Decimal("0.01"))             # минимальное значение
@example(amount=Decimal("999999.99"))        # граница
def test_money_serialization(amount: Decimal) -> None:
    money = Money(amount=amount, currency="USD")
    assert Money.from_json(money.to_json()) == money
```

Hypothesis **сам сохраняет** упавшие кейсы в `.hypothesis/examples/` — следующий запуск проверит их первыми. Коммить эту директорию.

<!-- /section:property -->

---

<!-- section:snapshot -->

# Part 8: Snapshot Testing

Для сериализаторов, парсеров, генерации текста/JSON — `syrupy` или `inline-snapshot`. Дифф читаем, обновление одной командой. Лучше чем 200 строк ручных `assert`.

## 31. syrupy

```python
def test_order_serializes_correctly(snapshot):
    """OrderResponse.model_dump() матчит snapshot."""
    order = build_order(id=1, customer_id=42)

    response = OrderResponse.model_validate(order)

    assert response.model_dump() == snapshot


# Запуск с обновлением snapshot'ов:
# pytest --snapshot-update
```

Snapshot'ы хранятся в `__snapshots__/` рядом с тестом. Изменения коммитятся вместе с кодом — ревью видит дельту.

## 32. inline-snapshot

Snapshot прямо в коде теста:

```python
from inline_snapshot import snapshot

def test_order_response():
    order = build_order(id=1, customer_id=42, total=Decimal("300"))

    response = OrderResponse.model_validate(order).model_dump()

    assert response == snapshot({
        "id": 1,
        "customer_id": 42,
        "total": "300.00",
        "status": "pending",
        "items": [],
    })


# Обновление: pytest --inline-snapshot=update
```

Удобно когда snapshot маленький — не надо переключаться между файлами.

<!-- /section:snapshot -->

---

<!-- section:async -->

# Part 9: Async Tests

## 33. pytest-asyncio с asyncio_mode="auto"

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # все async тесты запускаются автоматически
```

```python
# С asyncio_mode = "auto" — никаких декораторов
async def test_fetch_user_returns_user(db_session: AsyncSession) -> None:
    """Получение пользователя из БД."""
    repo = UserRepository(db_session)
    await repo.save(User(name="Ivan", email="ivan@test.com"))

    user = await repo.find_by_email("ivan@test.com")

    assert user is not None
    assert user.name == "Ivan"
```

## 34. Параллельные сценарии — TaskGroup

```python
async def test_concurrent_requests_handled_correctly(client: AsyncClient) -> None:
    """API корректно обрабатывает 5 параллельных запросов."""
    async with asyncio.TaskGroup() as tg:
        tasks = [
            tg.create_task(client.get(f"/users/{uid}"))
            for uid in range(1, 6)
        ]

    statuses = [t.result().status_code for t in tasks]
    assert all(s == 200 for s in statuses)
```

## 35. anyio для backend-agnostic тестов

```python
# Если код использует anyio (FastAPI, asyncpg) — тестируй через anyio
@pytest.mark.anyio
async def test_works_on_both_asyncio_and_trio():
    """Тест работает и на asyncio, и на trio backend'е."""
    result = await my_anyio_function()
    assert result == "ok"


@pytest.fixture
def anyio_backend():
    return "asyncio"
```

<!-- /section:async -->

---

<!-- section:test-data -->

# Part 10: Test Data Builders

## 36. Полноценные builders

Аналог Java TestDataBuilders — отдельный модуль для переиспользования.

```python
# tests/fixtures/builders.py
from decimal import Decimal
from datetime import datetime
from uuid import uuid4

from myservice.domain.order import Order, OrderItem, OrderStatus

# ─────────────────────────────────────────────────────────────
# Orders
# ─────────────────────────────────────────────────────────────

def build_order(
    *,
    id: int = 0,
    customer_id: int = 1,
    status: OrderStatus = OrderStatus.PENDING,
    items: list[OrderItem] | None = None,
    total: Decimal = Decimal("300"),
    created_at: datetime | None = None,
) -> Order:
    """Создаёт тестовый Order с переопределяемыми полями."""
    return Order(
        id=id or 0,
        customer_id=customer_id,
        status=status,
        items=items or [build_order_item()],
        total=total,
        created_at=created_at or datetime(2026, 1, 1, 12, 0),
    )


def build_order_item(
    *,
    product_id: int | None = None,
    quantity: int = 1,
    price: Decimal = Decimal("100"),
) -> OrderItem:
    """Создаёт OrderItem с дефолтами."""
    return OrderItem(
        product_id=product_id or hash(uuid4()) % 10000,
        quantity=quantity,
        price=price,
    )


def build_pending_order() -> Order:
    return build_order(status=OrderStatus.PENDING)


def build_shipped_order() -> Order:
    return build_order(status=OrderStatus.SHIPPED)


# ─────────────────────────────────────────────────────────────
# Requests (для API тестов)
# ─────────────────────────────────────────────────────────────

def build_valid_order_request() -> dict[str, object]:
    """Валидное тело запроса для POST /api/orders."""
    return {
        "customer_id": 1,
        "items": [
            {"product_id": 1, "quantity": 2, "price": "100.00"},
            {"product_id": 2, "quantity": 1, "price": "100.00"},
        ],
    }
```

Использование:
```python
from tests.fixtures.builders import build_order, build_pending_order

async def test_cancel_pending_order(order_service: OrderService, db_session) -> None:
    saved = await db_session.save(build_pending_order())

    result = await order_service.cancel(saved.id)

    assert result.status == OrderStatus.CANCELLED
```

## 37. Faker — реалистичные данные

```python
from faker import Faker

@pytest.fixture(scope="session")
def faker() -> Faker:
    """Faker с фиксированным seed для воспроизводимости."""
    fake = Faker("ru_RU")
    Faker.seed(42)
    return fake


def test_create_user_with_realistic_data(faker: Faker, user_service):
    """Создание пользователя с реалистичными данными."""
    user_data = {
        "email": faker.email(),
        "name": faker.name(),
        "phone": faker.phone_number(),
    }

    user = user_service.create(user_data)

    assert user.email == user_data["email"]
```

<!-- /section:test-data -->

---

<!-- section:ci -->

# Part 11: CI & Quality Gates

## 38. Coverage с branch

```toml
[tool.coverage.run]
branch = true                              # branch coverage, не только line
source = ["src"]
omit = [
    "src/*/migrations/*",
    "src/*/__main__.py",
]

[tool.coverage.report]
fail_under = 80                            # CI падает если < 80%
show_missing = true
skip_covered = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
    "@abstractmethod",
    "raise NotImplementedError",
    "\\.\\.\\.",
]
```

```bash
# Локальный запуск с отчётом
pytest --cov --cov-report=term-missing

# HTML отчёт
pytest --cov --cov-report=html
open htmlcov/index.html

# CI gate
pytest --cov --cov-fail-under=80
```

## 39. diff-cover — coverage по дельте PR

100% покрытие легаси кода — нереально. Но новый код должен быть покрыт.

```bash
# Coverage только для строк изменённых в PR
diff-cover coverage.xml --compare-branch=main --fail-under=90
```

В CI: 80% общий + 90% на изменённых строках.

## 40. Параллельный запуск — pytest-xdist

```bash
# Параллельно по числу CPU
pytest -n auto

# Конкретное число воркеров
pytest -n 4
```

⚠️ Если падают параллельно — у тебя shared state. Чини, не отключай xdist. Это ловит interdependence тестов.

## 41. pytest-randomly — рандомный порядок

Запускает тесты в случайном порядке. Ловит тесты, которые зависят от порядка выполнения.

```toml
[project.optional-dependencies]
test = ["pytest-randomly>=3.16"]
```

```bash
# Сид показывается в выводе — для воспроизведения упавшего запуска
pytest -p randomly --randomly-seed=12345
```

## 42. pytest-timeout — защита от зависаний

```toml
[tool.pytest.ini_options]
timeout = 60                # глобальный таймаут 60 секунд
timeout_method = "thread"
```

```python
# Локально для конкретного теста
@pytest.mark.timeout(5)
async def test_quick_response():
    ...

# Запретить таймаут (например для slow integration)
@pytest.mark.timeout(0)
async def test_long_migration():
    ...
```

## 43. Markers — фильтрация

```python
@pytest.mark.unit
def test_calculate_tax(): ...

@pytest.mark.integration
async def test_full_order_flow(): ...

@pytest.mark.slow
@pytest.mark.integration
async def test_database_migration(): ...

@pytest.mark.e2e
async def test_browser_checkout_flow(): ...
```

```bash
# Запуск по маркерам
pytest -m unit                          # только быстрые
pytest -m "integration and not slow"    # integration без медленных
pytest -m "not e2e"                     # всё кроме e2e
pytest -m "unit or integration"         # unit + integration
```

## 44. CI gate — обязательный минимум

В каждом PR (`.github/workflows/ci.yml` или аналог):

```yaml
- name: Lint
  run: ruff check --no-fix

- name: Format
  run: ruff format --check

- name: Type check
  run: pyright

- name: Security
  run: |
    bandit -r src/ -ll
    pip-audit

- name: Unit tests
  run: pytest -m "not integration and not e2e" --cov --cov-fail-under=80

- name: Integration tests
  run: pytest -m integration

- name: Coverage diff
  run: diff-cover coverage.xml --compare-branch=origin/main --fail-under=90
```

<!-- /section:ci -->

---

<!-- section:dependencies -->

# Part 12: Test Dependencies

```toml
[project.optional-dependencies]
test = [
    # Ядро
    "pytest>=8.3",
    "pytest-asyncio>=0.24",
    "pytest-mock>=3.14",

    # Качество прогона
    "pytest-randomly>=3.16",
    "pytest-xdist>=3.6",
    "pytest-timeout>=2.3",

    # HTTP / FastAPI
    "httpx>=0.28",
    "respx>=0.22",                # моки httpx
    # "responses>=0.25",          # моки requests (если используешь requests)

    # Реальные зависимости
    "testcontainers[postgres,redis,kafka]>=4.9",

    # Время
    "freezegun>=1.5",
    # "time-machine>=2.16",       # альтернатива freezegun, быстрее

    # Property-based
    "hypothesis>=6.122",

    # Snapshot
    "syrupy>=4.7",
    # "inline-snapshot>=0.18",    # альтернатива syrupy

    # Test data
    "polyfactory>=2.18",          # фабрики для Pydantic / dataclass
    "faker>=33.1",                # реалистичные данные

    # Coverage
    "coverage[toml]>=7.6",
    "diff-cover>=9.2",
]
```

<!-- /section:dependencies -->

---

# Quick Checklist

**Структура теста:**
- [ ] Naming: `test_<unit>_<scenario>_<expected>`
- [ ] AAA блоки разделены пустыми строками
- [ ] pytest plain `assert` (не unittest assertEqual)
- [ ] `pytest.raises` с `match=` для проверки сообщений
- [ ] `pytest.approx` для float (не для Decimal)
- [ ] Группировка через классы `class TestXxx`

**Configuration:**
- [ ] `--strict-markers` и `--strict-config` в `addopts`
- [ ] `xfail_strict = true`
- [ ] `asyncio_mode = "auto"` в `pyproject.toml`
- [ ] `filterwarnings = ["error"]`
- [ ] conftest.py разнесены по уровням, не один корневой

**Fixtures:**
- [ ] Правильные scope: session для БД/контейнеров, function для данных
- [ ] Async фикстуры через `AsyncIterator`
- [ ] Factory fixtures вместо отдельной фикстуры на каждый случай
- [ ] Cleanup через `yield` + `finally`

**Parametrize:**
- [ ] `pytest.param(..., id="...")` для всех кейсов — id обязателен
- [ ] `marks=pytest.mark.xfail(strict=True)` для известных багов

**Integration:**
- [ ] testcontainers для Postgres/Redis/Kafka — НЕ SQLite
- [ ] httpx AsyncClient + ASGITransport — НЕ requests
- [ ] respx для внешних HTTP API (не реальные запросы)
- [ ] Транзакция-rollback fixture для изоляции БД-тестов

**Unit:**
- [ ] `mocker` из pytest-mock с `create_autospec(Class, spec_set=True)`
- [ ] Protocol-based fakes для простых зависимостей (CRUD)
- [ ] Mock только для внешних — БД/HTTP/email
- [ ] freezegun/time-machine для проверок времени

**Property-based:**
- [ ] Hypothesis для round-trip, идемпотентности, инвариантов
- [ ] `@example(...)` для критических кейсов
- [ ] `.hypothesis/examples/` коммитится в репозиторий

**CI Gate:**
- [ ] Coverage 80% общий, 90% на diff (diff-cover)
- [ ] `branch = true` в coverage
- [ ] pytest-randomly включён — порядок рандомизирован
- [ ] pytest-xdist `-n auto` — параллельный запуск без shared state
- [ ] pytest-timeout — глобальный таймаут на тест
- [ ] Markers с фильтрацией: unit / integration / e2e / slow

**Команды:**
```bash
pytest                                              # все тесты
pytest -m "not integration"                         # без integration
pytest -n auto                                      # параллельно
pytest --cov --cov-report=term-missing              # с покрытием
pytest -k "test_create_order"                       # по имени
pytest --lf                                         # last failed
pytest --ff                                         # failed first
pytest -x                                           # стоп на первой ошибке
pytest --pdb                                        # pdb при падении
pytest -p randomly --randomly-seed=12345            # воспроизвести порядок
```
