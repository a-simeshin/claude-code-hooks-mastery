# Python Code Standards

Современный Python (3.12+) — строгий, типизированный, иммутабельный по умолчанию. Если кодовая база этому не следует — она устаревшая, а не «питоничная».

**Testing:** см. `.claude/refs/python-testing.md`

<!-- section:layout -->

# Part 1: Project Layout & Toolchain

## 1. src/ Layout — обязательно

`src/` layout — это `src/main/java` для Python. Импорт `myservice` работает только после `pip install -e .`, что ловит баги «работает локально, падает в проде».

```
project/
├── pyproject.toml           # единый конфиг (pom.xml/build.gradle)
├── uv.lock                  # лок-файл (uv) или poetry.lock
├── .pre-commit-config.yaml
├── src/
│   └── myservice/
│       ├── __init__.py
│       ├── domain/          # value objects, entities (без I/O!)
│       ├── application/     # use cases, services
│       ├── infrastructure/  # БД, HTTP, очереди — реализации Protocol'ов
│       ├── api/             # FastAPI/Litestar handlers
│       └── config.py
└── tests/
    ├── unit/
    ├── integration/
    ├── e2e/
    ├── conftest.py
    └── fixtures/
```

**Запрещено:**
- `setup.py` — легаси, удалён из современных шаблонов
- `requirements.txt` без лок-файла
- top-level пакет в корне репозитория
- Mixing `domain/` и `infrastructure/` импортов (чистый домен не знает про БД)

## 2. pyproject.toml — единый конфиг

Один файл для всего: зависимости, линтеры, тесты, coverage. Никаких `setup.cfg`, `.flake8`, `tox.ini`, `mypy.ini`.

```toml
[project]
name = "myservice"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "pydantic>=2.9",
    "pydantic-settings>=2.6",
    "structlog>=24.4",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.30",
    "httpx>=0.28",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.8",
    "pyright>=1.1.390",
    "bandit>=1.8",
    "pip-audit>=2.7",
    "pre-commit>=4.0",
]
test = [
    "pytest>=8.3",
    "pytest-asyncio>=0.24",
    "pytest-mock>=3.14",
    "pytest-randomly>=3.16",
    "pytest-xdist>=3.6",
    "pytest-timeout>=2.3",
    "coverage[toml]>=7.6",
    "hypothesis>=6.122",
    "testcontainers>=4.9",
    "respx>=0.22",
    "freezegun>=1.5",
    "polyfactory>=2.18",
    "syrupy>=4.7",
]

[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["ALL"]
ignore = [
    "D203",    # one-blank-line-before-class (конфликт с D211)
    "D213",    # multi-line-summary-second-line (конфликт с D212)
    "COM812",  # missing-trailing-comma (конфликт с formatter)
    "ISC001",  # implicit-string-concat (конфликт с formatter)
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "PLR2004", "ANN", "D"]  # assert/magic numbers/annotations OK in tests

[tool.pyright]
include = ["src", "tests"]
strict = ["src"]
pythonVersion = "3.12"
reportMissingTypeStubs = "error"
reportImplicitOverride = "error"
reportUnknownParameterType = "error"
reportUnknownMemberType = "warning"

[tool.pytest.ini_options]
addopts = "-ra --strict-markers --strict-config"
testpaths = ["tests"]
asyncio_mode = "auto"
xfail_strict = true
markers = [
    "unit: быстрые тесты без I/O",
    "integration: тесты с реальными зависимостями (БД, HTTP)",
    "e2e: end-to-end тесты",
    "slow: тесты выполняющиеся > 5 секунд",
]

[tool.coverage.run]
branch = true
source = ["src"]
omit = ["src/*/migrations/*", "src/*/__main__.py"]

[tool.coverage.report]
fail_under = 80
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

## 3. Toolchain Stack

| Цель | Инструмент | Java аналог |
|---|---|---|
| Менеджер зависимостей | **uv** (или Poetry/PDM) | Maven/Gradle |
| Линтер + форматтер | **Ruff** | Checkstyle + Spotless |
| Статический анализатор | **Pyright** (strict) | SpotBugs / ErrorProne |
| Безопасность | **Bandit** + **pip-audit** | OWASP Dependency-Check |
| Тесты | **pytest** | JUnit 5 |
| Coverage | **coverage.py** | JaCoCo |
| Property-based | **Hypothesis** | jqwik |
| Контейнеры в тестах | **testcontainers-python** | Testcontainers |
| Pre-commit gate | **pre-commit** | Git hooks + Husky |

**Ruff заменил**: flake8, isort, pylint, pyupgrade, autoflake, pep8-naming, pydocstyle, eradicate, bugbear. Один бинарь, ~50× быстрее.

## 4. Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/RobertCraigie/pyright-python
    rev: v1.1.390
    hooks:
      - id: pyright

  - repo: https://github.com/PyCQA/bandit
    rev: 1.8.0
    hooks:
      - id: bandit
        args: [-c, pyproject.toml]
        additional_dependencies: ["bandit[toml]"]
```

<!-- /section:layout -->

---

<!-- section:typing -->

# Part 2: Type System

Type hints — не опция, а контракт. `pyright --strict` в CI работает как `javac -Werror`.

## 5. Type Hints Everywhere

Все функции, переменные модуля, параметры, возвращаемые типы — с аннотациями. Без исключений.

```python
# BAD: Нет типов — контракт не виден
def process_order(order, items):
    total = 0
    for item in items:
        total += item["price"] * item["qty"]
    return {"order_id": order["id"], "total": total}


# GOOD: Явные типы
from decimal import Decimal

def process_order(order: Order, items: list[OrderItem]) -> OrderResult:
    total: Decimal = sum(
        (item.price * item.quantity for item in items),
        start=Decimal("0"),  # ВАЖНО: без start будет int 0 → TypeError на Decimal
    )
    return OrderResult(order_id=order.id, total=total)
```

**Правила:**
```python
from __future__ import annotations  # отложенная оценка типов — в каждом файле

# Коллекции — встроенные generic (Python 3.9+)
names: list[str] = []
config: dict[str, int] = {}
unique_ids: set[int] = set()

# Optional — через union (PEP 604, Python 3.10+)
description: str | None = None

# Callable
handler: Callable[[Request], Response]

# Возвращаемый тип — ВСЕГДА (включая None)
def get_name() -> str: ...
def save(item: Item) -> None: ...
async def fetch(url: str) -> bytes: ...
```

## 6. Запрет на Any в production коде

`Any` отключает проверку типов. Если иначе нельзя — `# type: ignore[reason]` с объяснением.

```python
# BAD: Any проедает контракт
def parse(data: Any) -> dict[str, Any]:
    return json.loads(data)

# GOOD: Конкретные типы или TypedDict
def parse(data: bytes) -> UserPayload:
    raw: dict[str, object] = json.loads(data)
    return UserPayload.model_validate(raw)
```

## 7. Self, override, Final, Literal, NewType

Современный type system Python — это Java `final`, `@Override`, sealed types, type-safe IDs.

```python
from typing import Final, Literal, NewType, Self, override

# === Final — Java `final` для атрибутов и констант ===
class Config:
    """Конфиг приложения, поля неизменяемы после init."""
    api_url: Final[str]
    timeout_seconds: Final[int]

    def __init__(self, api_url: str, timeout: int) -> None:
        self.api_url = api_url
        self.timeout_seconds = timeout

MAX_RETRY_ATTEMPTS: Final = 3  # type выводится как Literal[3]

# === Self — для fluent API и factory methods (PEP 673, 3.11+) ===
class QueryBuilder:
    """Fluent SQL builder."""
    def __init__(self) -> None:
        self._where: list[str] = []

    def where(self, condition: str) -> Self:  # вернёт правильный subclass
        self._where.append(condition)
        return self

    @classmethod
    def for_table(cls, table: str) -> Self:
        return cls()

# === @override — Java @Override (PEP 698, 3.12+) ===
class BaseRepository:
    def find_by_id(self, entity_id: int) -> object | None: ...

class UserRepository(BaseRepository):
    @override
    def find_by_id(self, entity_id: int) -> User | None:
        # компилятор проверит что метод реально существует в родителе
        ...

# === Literal — типобезопасные строковые константы ===
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

def set_level(level: LogLevel) -> None:  # mypy/pyright поймает опечатку
    ...

set_level("INFO")     # OK
set_level("invalid")  # ❌ type error

# === NewType — type-safe ID типы вместо голого int ===
UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)

def transfer(from_user: UserId, to_user: UserId, order: OrderId) -> None: ...

user_id = UserId(42)
order_id = OrderId(100)
transfer(user_id, order_id, user_id)  # ❌ type error: OrderId передан вместо UserId
```

## 8. Protocol — структурная типизация

`Protocol` (PEP 544) = Java интерфейс, но без обязательного `implements`. Любой класс с подходящей сигнатурой — реализация.

```python
from typing import Protocol, runtime_checkable

class NotificationSender(Protocol):
    """Контракт для отправки уведомлений."""
    def send(self, recipient: str, message: str) -> bool: ...


# Любой класс с подходящим методом — автоматически реализация
class EmailSender:
    """Отправка email через SMTP."""
    def send(self, recipient: str, message: str) -> bool:
        return True

class SmsSender:
    """Отправка SMS через шлюз."""
    def send(self, recipient: str, message: str) -> bool:
        return True


def notify(sender: NotificationSender, recipient: str, message: str) -> bool:
    """Принимает любой класс реализующий Protocol."""
    return sender.send(recipient, message)


notify(EmailSender(), "user@test.com", "Hello")  # OK
notify(SmsSender(), "+79001234567", "Hello")     # OK
```

**ABC vs Protocol:**

```python
# Protocol — duck typing с проверкой типов (для DI)
class Repository(Protocol):
    def find_by_id(self, entity_id: int) -> Entity | None: ...
    def save(self, entity: Entity) -> Entity: ...

# ABC — когда нужна общая логика (template method)
from abc import ABC, abstractmethod

class BaseRepository[E: Entity](ABC):
    """Базовый репозиторий с общей логикой."""

    @abstractmethod
    def find_by_id(self, entity_id: int) -> E | None: ...

    @abstractmethod
    def save(self, entity: E) -> E: ...

    def find_or_raise(self, entity_id: int) -> E:
        """Общая реализация — найти или бросить NotFoundError."""
        result = self.find_by_id(entity_id)
        if result is None:
            raise NotFoundError(self.__class__.__name__, entity_id)
        return result
```

## 9. assert_never — exhaustive проверки

`typing.assert_never` = Java `sealed switch` exhaustiveness check. Если забыл case — pyright не пропустит.

```python
from typing import assert_never, Literal

OrderStatus = Literal["pending", "shipped", "delivered", "cancelled"]

def describe_status(status: OrderStatus) -> str:
    """Pyright проверяет покрытие всех значений."""
    match status:
        case "pending":
            return "Ожидает обработки"
        case "shipped":
            return "Отправлен"
        case "delivered":
            return "Доставлен"
        case "cancelled":
            return "Отменён"
        case _:
            assert_never(status)  # ❌ компилятор скажет если case забыт


# То же для discriminated unions
@dataclass(frozen=True, slots=True)
class Success:
    kind: Literal["success"] = "success"
    value: int

@dataclass(frozen=True, slots=True)
class Failure:
    kind: Literal["failure"] = "failure"
    error: str

Result = Success | Failure

def handle(result: Result) -> str:
    match result:
        case Success(value=v):
            return f"Got {v}"
        case Failure(error=e):
            return f"Error: {e}"
        case _:
            assert_never(result)  # exhaustive проверка
```

## 10. TYPE_CHECKING для разрыва циклов импортов

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Импорт нужен ТОЛЬКО для type checker, не для runtime
    from myservice.domain.user import User
    from myservice.domain.order import Order

class OrderService:
    def for_user(self, user: User) -> list[Order]:  # типы как строки до runtime
        ...
```

<!-- /section:typing -->

---

<!-- section:data -->

# Part 3: Data Modeling

## 11. Иммутабельность по умолчанию

Все data containers — `frozen=True, slots=True, kw_only=True`. Это Java `record`.

```python
# BAD: Mutable, позиционные аргументы, без slots
@dataclass
class Money:
    amount: Decimal
    currency: str
    # Можно мутировать, лишние атрибуты, путаница в позициях

money = Money(Decimal("100"), "USD")
money.amount = Decimal("999")  # ❌ Незаметно меняем


# GOOD: Полностью защищённый dataclass
@dataclass(frozen=True, slots=True, kw_only=True)
class Money:
    """Деньги — immutable value object."""
    amount: Decimal
    currency: str

money = Money(amount=Decimal("100"), currency="USD")  # явные имена
money.amount = Decimal("999")  # ❌ FrozenInstanceError
money.extra = "foo"            # ❌ AttributeError (slots блокирует лишние)
```

**Что даёт каждый флаг:**
- `frozen=True` — иммутабельность, hashable, эквивалент Java `final` полей.
- `slots=True` — фиксированная схема, ~30% экономия памяти, запрет лишних атрибутов.
- `kw_only=True` — обязательно именованные аргументы, нет ада из 7 позиционных.

## 12. dataclass vs Pydantic vs NamedTuple

| Тип | Когда использовать |
|---|---|
| **`@dataclass`** | Внутренние value objects, DTO между слоями, domain entities |
| **Pydantic BaseModel** | Границы системы — HTTP request/response, JSON, очереди |
| **`NamedTuple`** | Лёгкие неизменяемые кортежи (точки, координаты, пары) |
| **`TypedDict`** | JSON shape без runtime валидации (например ответ от API) |

```python
# === dataclass: domain layer ===
@dataclass(frozen=True, slots=True, kw_only=True)
class OrderCalculation:
    """Результат расчёта стоимости заказа."""
    subtotal: Decimal
    tax: Decimal
    total: Decimal

# === Pydantic: API boundary ===
from pydantic import BaseModel, Field

class OrderResponse(BaseModel):
    """HTTP-ответ создания заказа."""
    id: int
    total: Decimal = Field(..., gt=0)
    created_at: datetime

# === NamedTuple: лёгкие кортежи ===
class Point(NamedTuple):
    x: float
    y: float

# === TypedDict: shape для не-валидируемых данных ===
class GitHubUser(TypedDict):
    login: str
    id: int
    avatar_url: str
```

## 13. Enum — никаких магических строк

```python
# BAD: Магические строки — опечатка = баг в рантайме
def set_status(order: Order, status: str) -> None:
    order.status = status  # "active"? "Active"? "ACTIVE"?

set_status(order, "actve")  # Опечатка прошла — упадёт через час


# GOOD: StrEnum (Python 3.11+) — сериализуется как строка автоматически
from enum import StrEnum, IntEnum, auto

class OrderStatus(StrEnum):
    """Статусы заказа в жизненном цикле."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

def set_status(order: Order, status: OrderStatus) -> None:
    order.status = status

set_status(order, OrderStatus.CONFIRMED)
print(OrderStatus.CONFIRMED)         # "confirmed"
json.dumps({"s": OrderStatus.CONFIRMED})  # {"s": "confirmed"}


# IntEnum — для числовых констант
class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
```

**Когда `Literal`, а когда `Enum`:**
- `Enum` — есть поведение/методы, нужна итерация значений, важна идентичность.
- `Literal["a", "b"]` — лёгкое перечисление, нет методов, чисто type-level.

<!-- /section:data -->

---

<!-- section:errors -->

# Part 4: Error Handling

## 14. Custom Exception Hierarchy

Иерархия исключений как в Java: базовый класс приложения, доменные подклассы.

```python
# BAD: Голые Exception без контекста
def get_user(user_id: int):
    user = db.find(user_id)
    if not user:
        raise Exception("not found")  # Какой user? Что делать?


# GOOD: Иерархия с контекстом
class AppError(Exception):
    """Базовое исключение приложения. Никогда не наследуется от BaseException."""

    def __init__(self, message: str, code: str = "UNKNOWN") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class DomainError(AppError):
    """Ошибки бизнес-логики (отличается от технических ошибок)."""


class InfrastructureError(AppError):
    """Ошибки инфраструктуры (БД, сеть, файлы)."""


class NotFoundError(DomainError):
    """Сущность не найдена."""

    def __init__(self, entity: str, entity_id: str | int) -> None:
        super().__init__(
            message=f"{entity} с id={entity_id} не найден",
            code="NOT_FOUND",
        )
        self.entity = entity
        self.entity_id = entity_id


class ValidationError(DomainError):
    """Ошибка валидации входных данных."""

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(
            message=f"Поле '{field}': {reason}",
            code="VALIDATION_ERROR",
        )
        self.field = field
        self.reason = reason


# Использование — информативно
def get_user(user_id: int) -> User:
    user = db.find(user_id)
    if user is None:
        raise NotFoundError("User", user_id)
    return user
```

## 15. raise from — сохранение причины

Всегда используй `raise X from original` — сохраняет цепочку, как Java `caused by`.

```python
# BAD: Теряем оригинальную ошибку
def fetch_user(user_id: int) -> User:
    try:
        return db.find_by_id(user_id)
    except SQLAlchemyError:
        raise InfrastructureError("DB error")  # ❌ потеряли stack trace


# GOOD: from сохраняет причину
def fetch_user(user_id: int) -> User:
    try:
        return db.find_by_id(user_id)
    except SQLAlchemyError as exc:
        raise InfrastructureError("DB error") from exc  # ✅ полная цепочка


# GOOD: from None — если намеренно скрываем (security, абстракция)
def authenticate(token: str) -> User:
    try:
        return decode_jwt(token)
    except (jwt.InvalidSignatureError, jwt.ExpiredSignatureError) as exc:
        # не показываем деталь почему именно токен невалиден
        raise AuthError("Invalid credentials") from None
```

## 16. ExceptionGroup — несколько ошибок сразу

Python 3.11+: можно бросить пачку ошибок (например все ошибки валидации).

```python
def validate_order(order: OrderInput) -> None:
    """Собирает ВСЕ ошибки валидации, не падает на первой."""
    errors: list[ValidationError] = []

    if not order.customer_id:
        errors.append(ValidationError("customer_id", "обязательное поле"))
    if order.total < 0:
        errors.append(ValidationError("total", "не может быть отрицательным"))
    if not order.items:
        errors.append(ValidationError("items", "минимум одна позиция"))

    if errors:
        raise ExceptionGroup("Ошибки валидации заказа", errors)


# Обработка через except*
try:
    validate_order(order)
except* ValidationError as eg:
    for err in eg.exceptions:
        logger.warning("validation_failed", field=err.field, reason=err.reason)
```

## 17. Никогда `except:` или `except Exception:` без логики

```python
# BAD: Глотает всё, включая SystemExit, KeyboardInterrupt
try:
    do_work()
except:
    pass  # ❌ скрывает баги навсегда


# BAD: Глотает Exception без логирования
try:
    do_work()
except Exception:
    pass  # ❌ хуже чем падение — невидимая ошибка


# GOOD: Логируем + перебрасываем или явное намерение
try:
    do_work()
except SpecificError as exc:
    logger.exception("operation_failed", operation="do_work")
    raise  # перебрасываем

# GOOD: Только если ДЕЙСТВИТЕЛЬНО можем восстановиться
try:
    cache.set(key, value)
except CacheError as exc:
    # кэш недоступен — продолжаем без него, но логируем
    logger.warning("cache_unavailable", error=str(exc))
```

## 18. Никаких голых assert в production

`assert` отключается флагом `python -O`. Для проверок инвариантов используй `raise`.

```python
# BAD: assert в продакшен-коде
def withdraw(account: Account, amount: Decimal) -> None:
    assert amount > 0, "amount must be positive"  # ❌ пропадёт под -O
    account.balance -= amount


# GOOD: явное исключение
def withdraw(account: Account, amount: Decimal) -> None:
    if amount <= 0:
        raise ValidationError("amount", "должна быть положительной")
    account.balance -= amount
```

`assert` OK **только** в тестах и для type narrowing внутри функции.

<!-- /section:errors -->

---

<!-- section:logging -->

# Part 5: Logging

## 19. structlog — структурированные логи

`print()` запрещён в любом коде кроме CLI. Структурированные логи обязательны.

```python
# BAD: print не виден в проде, нет уровней, нет контекста
def process_payment(order_id: str, amount: float):
    print(f"Processing payment for {order_id}")
    print(f"Amount: {amount}")
    print("Done!")


# GOOD: structlog — JSON логи, привязанный контекст
import structlog

logger = structlog.get_logger()

def process_payment(order_id: str, amount: Decimal) -> PaymentResult:
    log = logger.bind(order_id=order_id, amount=str(amount))
    log.info("payment_processing_started")

    try:
        result = gateway.charge(amount)
        log.info("payment_completed", transaction_id=result.tx_id)
        return result
    except GatewayError as exc:
        log.exception("payment_failed", gateway=gateway.name)
        raise
```

**Конвенции имён событий:**
- snake_case в прошедшем времени или present continuous: `payment_completed`, `user_created`, `request_started`
- НЕ предложения: `"Payment was completed"` — это для message, не для event

## 20. Stdlib logging — fallback

Если structlog недоступен — stdlib `logging` с lazy форматированием.

```python
import logging

logger = logging.getLogger(__name__)

# GOOD: lazy формат — не тратит CPU если уровень DEBUG выключен
logger.info("Обработка платежа: order=%s, amount=%s", order_id, amount)

# BAD: f-string выполняется ВСЕГДА, даже если лог отфильтрован
logger.info(f"Обработка платежа: order={order_id}, amount={amount}")  # ❌
```

<!-- /section:logging -->

---

<!-- section:io -->

# Part 6: I/O & Resources

## 21. pathlib over os.path

`pathlib.Path` — единственный API для файлов и путей.

```python
# BAD: os.path — строковые операции, нечитаемо
import os

config_path = os.path.join(os.path.dirname(__file__), "..", "config", "app.yaml")
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        data = f.read()


# GOOD: pathlib — объектный API, кроссплатформенный
from pathlib import Path

CONFIG_DIR: Final[Path] = Path(__file__).parent.parent / "config"

def load_config(name: str = "app.yaml") -> str:
    config_path = CONFIG_DIR / name
    if not config_path.exists():
        raise FileNotFoundError(f"Конфиг не найден: {config_path}")
    return config_path.read_text(encoding="utf-8")
```

**Полезные методы:**
```python
path = Path("/data/reports/2024")

path.mkdir(parents=True, exist_ok=True)  # Создать с родителями
path.iterdir()                           # Итерация по содержимому
path.glob("*.csv")                       # Поиск файлов
path.rglob("**/*.py")                    # Рекурсивный поиск
path.suffix                              # ".csv"
path.stem                                # "report"
path.with_suffix(".json")                # Замена расширения
path.read_text(encoding="utf-8")
path.write_text(data, encoding="utf-8")
path.read_bytes()
path.write_bytes(data)
```

## 22. Context Managers — обязательно для ресурсов

```python
# BAD: Ручное управление — можно забыть закрыть
def export_data(data: list[dict], path: Path) -> None:
    f = open(path, "w")
    try:
        json.dump(data, f)
    finally:
        f.close()  # При исключении в close() файл может остаться открытым


# GOOD: with — автоматическое закрытие
def export_data(data: list[dict[str, object]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

**Кастомный context manager через contextlib:**
```python
from contextlib import contextmanager, asynccontextmanager
from collections.abc import Iterator, AsyncIterator
import time

@contextmanager
def measure_time(operation: str) -> Iterator[None]:
    """Замер времени выполнения операции."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info("operation_completed", operation=operation, elapsed_ms=elapsed * 1000)


@asynccontextmanager
async def db_transaction(session: AsyncSession) -> AsyncIterator[AsyncSession]:
    """Транзакция с автоматическим rollback при ошибке."""
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
```

<!-- /section:io -->

---

<!-- section:idiom -->

# Part 7: Functional Idioms

## 23. Comprehensions — читаемые, не вложенные

Один уровень. Вложенные comprehensions запрещены — разбить на функции.

```python
# BAD: Вложенный comprehension — нечитаемо
result = [
    transform(item)
    for group in data
    if group.is_active
    for item in group.items
    if item.price > 0 and item.category in allowed_categories
]


# GOOD: Разбить на шаги
def is_eligible(item: Item, allowed: set[str]) -> bool:
    """Проверяет, подходит ли товар по цене и категории."""
    return item.price > 0 and item.category in allowed

active_items: list[Item] = [
    item
    for group in data if group.is_active
    for item in group.items
]

result: list[TransformedItem] = [
    transform(item)
    for item in active_items
    if is_eligible(item, allowed_categories)
]
```

```python
# dict / set comprehensions
users_by_id: dict[int, User] = {user.id: user for user in users}
unique_emails: set[str] = {user.email.lower() for user in users}

# generator expression — для больших коллекций (не материализует список)
total = sum(item.price for item in items)
```

## 24. match/case — pattern matching

Python 3.10+ pattern matching — мощнее Java switch для рекурсивных структур.

```python
# Простой match по литералам
def http_status_message(code: int) -> str:
    match code:
        case 200 | 201 | 204:
            return "Success"
        case 400 | 422:
            return "Bad Request"
        case 401 | 403:
            return "Unauthorized"
        case 404:
            return "Not Found"
        case 500 | 502 | 503:
            return "Server Error"
        case _:
            return f"Unknown status: {code}"


# Pattern matching по структурам — destructuring
@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float

@dataclass(frozen=True, slots=True)
class Circle:
    center: Point
    radius: float

@dataclass(frozen=True, slots=True)
class Rectangle:
    top_left: Point
    bottom_right: Point

Shape = Circle | Rectangle

def area(shape: Shape) -> float:
    match shape:
        case Circle(radius=r):
            return 3.14159 * r * r
        case Rectangle(top_left=Point(x=x1, y=y1), bottom_right=Point(x=x2, y=y2)):
            return abs(x2 - x1) * abs(y2 - y1)
        case _:
            assert_never(shape)


# Pattern matching по dict (для JSON парсинга)
def parse_event(event: dict[str, object]) -> Event:
    match event:
        case {"type": "user_created", "id": int(uid), "name": str(name)}:
            return UserCreated(user_id=uid, name=name)
        case {"type": "order_placed", "order_id": int(oid), "items": list(items)}:
            return OrderPlaced(order_id=oid, items=items)
        case {"type": event_type}:
            raise ValueError(f"Unknown event type: {event_type}")
        case _:
            raise ValueError("Invalid event format")
```

## 25. functools — кэширование и мультиметоды

```python
from functools import cache, lru_cache, cached_property, singledispatch

# === @cache — без лимита, для чистых функций ===
@cache
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# === @lru_cache(maxsize=N) — с лимитом памяти ===
@lru_cache(maxsize=1024)
def get_user_settings(user_id: int) -> UserSettings:
    """Кэш на 1024 пользователя."""
    return db.fetch_settings(user_id)

# === @cached_property — кэш на инстансе ===
class Order:
    """Заказ. items_count считается один раз."""
    def __init__(self, items: list[OrderItem]) -> None:
        self.items = items

    @cached_property
    def items_count(self) -> int:
        """Дорогой подсчёт — кэшируется на инстансе."""
        return sum(item.quantity for item in self.items)

# === @singledispatch — multimethods (как @overload в Java) ===
@singledispatch
def serialize(value: object) -> str:
    raise NotImplementedError(f"Не умею сериализовать {type(value).__name__}")

@serialize.register
def _(value: int) -> str:
    return str(value)

@serialize.register
def _(value: datetime) -> str:
    return value.isoformat()

@serialize.register
def _(value: Decimal) -> str:
    return f"{value:.2f}"
```

## 26. Async/Await — только для I/O

`async` для реального I/O. Не для CPU-bound (там `concurrent.futures.ProcessPoolExecutor`).

```python
# BAD: async без причины — добавляет overhead
async def calculate_tax(amount: Decimal) -> Decimal:
    return amount * Decimal("0.20")  # Чистый расчёт, async не нужен


# GOOD: async для реального I/O
async def fetch_user(user_id: int, session: AsyncSession) -> User | None:
    """Загрузка пользователя из БД."""
    result = await session.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    return result.scalar_one_or_none()


# GOOD: sync для вычислений
def calculate_tax(amount: Decimal) -> Decimal:
    """Расчёт налога — чистая функция, без I/O."""
    return amount * Decimal("0.20")
```

**Параллельный I/O — gather/TaskGroup:**
```python
# BAD: Последовательные запросы (медленно)
async def get_dashboard(user_id: int) -> Dashboard:
    user = await fetch_user(user_id)
    orders = await fetch_orders(user_id)    # Ждёт user!
    balance = await fetch_balance(user_id)  # Ждёт orders!


# GOOD: asyncio.gather — параллельно
async def get_dashboard(user_id: int) -> Dashboard:
    user, orders, balance = await asyncio.gather(
        fetch_user(user_id),
        fetch_orders(user_id),
        fetch_balance(user_id),
    )
    return Dashboard(user=user, orders=orders, balance=balance)


# GOOD: TaskGroup (Python 3.11+) — структурированная конкурентность
async def get_dashboard(user_id: int) -> Dashboard:
    async with asyncio.TaskGroup() as tg:
        user_task = tg.create_task(fetch_user(user_id))
        orders_task = tg.create_task(fetch_orders(user_id))
        balance_task = tg.create_task(fetch_balance(user_id))
    # Если любая задача упала — все остальные отменяются автоматически
    return Dashboard(
        user=user_task.result(),
        orders=orders_task.result(),
        balance=balance_task.result(),
    )
```

<!-- /section:idiom -->

---

<!-- section:fastapi -->

# Part 8: FastAPI Patterns

## 27. APIRouter — модульная структура

Все эндпоинты по роутерам. `main.py` — только сборка.

```python
# BAD: Всё в main.py — 500 строк эндпоинтов
app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int): ...

@app.post("/users")
async def create_user(user: UserCreate): ...
# ... ещё 50 эндпоинтов


# GOOD: Роутеры по доменам
# src/myservice/api/users.py
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Получение пользователя по ID."""
    return await service.get_by_id(user_id)


# src/myservice/api/__init__.py
from fastapi import FastAPI
from myservice.api import users, orders, payments

def create_app() -> FastAPI:
    app = FastAPI(title="My Service", lifespan=lifespan)
    app.include_router(users.router)
    app.include_router(orders.router)
    app.include_router(payments.router)
    return app
```

## 28. Pydantic v2 — валидация на границе

```python
from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
from typing import Self

class OrderItemCreate(BaseModel):
    """Позиция заказа."""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=10000)
    price: Decimal = Field(..., gt=0, decimal_places=2)


class OrderCreate(BaseModel):
    """Данные для создания заказа."""
    customer_id: int = Field(..., gt=0, description="ID покупателя")
    items: list[OrderItemCreate] = Field(..., min_length=1)
    discount_percent: float = Field(default=0, ge=0, le=100)
    comment: str | None = Field(default=None, max_length=500)

    @field_validator("items")
    @classmethod
    def validate_unique_products(cls, v: list[OrderItemCreate]) -> list[OrderItemCreate]:
        """Уникальность товаров в заказе."""
        product_ids = [item.product_id for item in v]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Дублирующиеся товары в заказе")
        return v

    @model_validator(mode="after")
    def validate_total_limit(self) -> Self:
        """Заказ не может превышать лимит."""
        total = sum(item.price * item.quantity for item in self.items)
        if total > Decimal("1000000"):
            raise ValueError("Заказ превышает лимит 1млн")
        return self

    @computed_field
    @property
    def total_items(self) -> int:
        """Общее количество позиций."""
        return len(self.items)
```

## 29. Depends() — DI в FastAPI

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncIterator[AsyncSession]:
    """Сессия БД с автоматическим закрытием."""
    async with async_session_factory() as session:
        yield session

# Type alias для переиспользования
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_user_service(db: DbSession) -> UserService:
    """Сервис пользователей с внедрённой сессией."""
    return UserService(repo=UserRepository(db))

UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, service: UserServiceDep) -> UserResponse:
    """Зависимости внедряются автоматически."""
    return await service.get_by_id(user_id)
```

## 30. Response Models, Status Codes, Validation

```python
from fastapi import status, Query, Path

class UserResponse(BaseModel):
    """Ответ с данными пользователя."""
    id: int
    email: str
    display_name: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)  # позволяет из ORM

class UserListResponse(BaseModel):
    """Список с пагинацией."""
    items: list[UserResponse]
    total: int
    page: int
    page_size: int


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание пользователя",
)
async def create_user(body: UserCreate, service: UserServiceDep) -> UserResponse:
    """Создаёт нового пользователя и возвращает его данные."""
    return await service.create(body)


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: Annotated[int, Query(ge=1, le=1000)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    *,
    service: UserServiceDep,
) -> UserListResponse:
    """Список пользователей с пагинацией."""
    return await service.list(page=page, page_size=page_size)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: Annotated[int, Path(gt=0, description="ID пользователя")],
    service: UserServiceDep,
) -> UserResponse:
    """Получение пользователя по ID."""
    return await service.get_by_id(user_id)
```

## 31. Global Exception Handler

Единый формат ответов на ошибки.

```python
from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Базовая ошибка приложения с HTTP статусом."""
    def __init__(self, message: str, code: str, status_code: int = 400) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code

class NotFoundError(AppError):
    def __init__(self, entity: str, entity_id: int | str) -> None:
        super().__init__(
            message=f"{entity} с id={entity_id} не найден",
            code="NOT_FOUND",
            status_code=404,
        )

class ConflictError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="CONFLICT", status_code=409)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message},
        )


# Сервис бросает понятные исключения
async def get_user(self, user_id: int) -> User:
    user = await self.repo.find_by_id(user_id)
    if user is None:
        raise NotFoundError("User", user_id)
    return user
```

## 32. Lifespan для startup/shutdown

`lifespan` context manager. `on_event` deprecated.

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Жизненный цикл приложения."""
    # Startup
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    app.state.db_engine = engine
    app.state.session_factory = session_factory
    logger.info("app_started", database=settings.database_url)

    yield  # приложение работает

    # Shutdown
    await engine.dispose()
    logger.info("app_stopped")


app = FastAPI(title="My Service", lifespan=lifespan)
```

## 33. BackgroundTasks — лёгкие фоновые задачи

```python
from fastapi import BackgroundTasks

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: OrderCreate,
    background_tasks: BackgroundTasks,
    service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    """Создание заказа. Email отправляется в фоне после ответа клиенту."""
    order = await service.create(body)
    background_tasks.add_task(send_confirmation_email, order.id, order.customer_email)
    return order


async def send_confirmation_email(order_id: int, email: str) -> None:
    """Фоновая отправка. НЕ перебрасываем — фон не ломает основной flow."""
    try:
        await email_service.send(to=email, template="order_confirmation", order_id=order_id)
    except Exception:
        logger.exception("email_send_failed", order_id=order_id, email=email)
```

⚠️ Для тяжёлых задач (минуты/часы) — Celery, RQ, Dramatiq. BackgroundTasks для секундных операций.

## 34. Middleware — кросс-эндпоинт логика

CORS, логирование, авторизация — через middleware, не в каждом handler'е.

```python
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# Стандартный CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Логирование всех HTTP-запросов с временем выполнения."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            elapsed_ms=round(elapsed_ms, 2),
        )
        return response


app.add_middleware(RequestLoggingMiddleware)
```

## 35. Settings через pydantic-settings

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

class Settings(BaseSettings):
    """Конфигурация приложения. Читается из env + .env файла."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Обязательные
    database_url: str = Field(..., description="URL подключения к БД")
    secret_key: SecretStr = Field(..., description="Секретный ключ для JWT")

    # С дефолтами
    debug: bool = Field(default=False)
    app_name: str = Field(default="My Service")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    redis_url: str = Field(default="redis://localhost:6379/0")
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])


from functools import cache

@cache
def get_settings() -> Settings:
    """Синглтон настроек."""
    return Settings()


@router.get("/health")
async def health(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, object]:
    return {"app": settings.app_name, "debug": settings.debug}
```

<!-- /section:fastapi -->

---

<!-- section:concurrency -->

# Part 9: Async Concurrency & FastAPI Performance

Критичные правила для production FastAPI. Большинство багов на проде — не в бизнес-логике, а в неправильном обращении с event loop, threadpool, пулами соединений и cancellation.

## 36. Event Loop Fundamentals

FastAPI/uvicorn = **один процесс = один event loop = один поток**. Любая блокирующая операция в `async def` останавливает обработку **всех** запросов до её завершения.

```
Thread 1 (Event Loop):
  ├─ request 1: await db.fetch()       ← await освобождает loop
  ├─ request 2: await http.get()       ← может работать параллельно
  ├─ request 3: time.sleep(5)          ← ❌ БЛОКИРУЕТ ВСЕ остальные на 5 секунд!
  └─ request 4: ждёт... ждёт... ждёт...
```

**Что блокирует loop:**
- `time.sleep()` вместо `asyncio.sleep()`
- `requests.get()` вместо `httpx.AsyncClient.get()`
- `psycopg2` (sync) вместо `asyncpg` или async SQLAlchemy
- `redis-py` sync API вместо `redis.asyncio`
- `boto3` (sync) вместо `aioboto3`
- `pymongo` (sync) вместо `motor`
- Чтение/запись файлов через `open()` без `aiofiles` или `asyncio.to_thread`
- CPU-bound > 10ms (regex на больших строках, json гигабайтов, ML inference)
- `subprocess.run()` вместо `asyncio.create_subprocess_exec`
- Тяжёлые `json.dumps()` / `json.loads()` на больших структурах

**Обнаружение блокировки:**
```python
# Метрика event loop lag в production
async def measure_loop_lag() -> None:
    """Если > 100ms — есть блокировка."""
    while True:
        start = time.perf_counter()
        await asyncio.sleep(0)
        lag_ms = (time.perf_counter() - start) * 1000
        if lag_ms > 100:
            logger.warning("event_loop_lag_high", lag_ms=lag_ms)
        await asyncio.sleep(1)


# uvloop — замена встроенного event loop, в 2-4 раза быстрее
# uvicorn --loop uvloop main:app
```

## 37. Sync vs Async Endpoints

FastAPI запускает их **по-разному**:

| Endpoint | Где исполняется | Когда использовать |
|---|---|---|
| `async def` | На event loop | Async I/O (asyncpg, httpx, redis.asyncio) |
| `def` (sync) | В anyio threadpool (40 потоков default) | Sync библиотеки которые иначе блокировали бы loop |

```python
# GOOD: async def с async библиотеками
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user = await db.get(User, user_id)
    return UserResponse.model_validate(user)


# GOOD: sync def если зависимость sync
@router.get("/legacy/users/{user_id}")
def get_user_legacy(user_id: int, db: Session = Depends(get_sync_db)) -> UserResponse:
    """psycopg2 sync — пусть FastAPI запустит в threadpool."""
    user = db.query(User).filter_by(id=user_id).one()
    return UserResponse.model_validate(user)


# CRITICAL BAD: sync либа внутри async def — блок event loop!
@router.get("/users/{user_id}")
async def get_user_bad(user_id: int) -> UserResponse:
    user = sync_db.query(User).filter_by(id=user_id).one()  # ❌ БЛОК всего loop!
    return UserResponse.model_validate(user)
```

**Правило:** если в endpoint есть **хотя бы один блокирующий вызов**, либо весь endpoint делай `def`, либо оборачивай блокирующие куски в `asyncio.to_thread()`.

## 38. Threadpool Capacity

AnyIO threadpool по умолчанию = **40 потоков**. Каждый sync endpoint занимает 1 поток на время выполнения. Если все 40 заняты — sync запросы встают в очередь.

```python
from anyio import to_thread

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Увеличить лимит если много sync endpoints / DB sessions
    limiter = to_thread.current_default_thread_limiter()
    limiter.total_tokens = 100  # default 40
    yield
```

**Сколько ставить:**
- Чисто async сервис → не трогать (40 хватает с запасом).
- Mix sync/async → `max(40, среднее число одновременных sync операций × 2)`.
- Если sync эндпоинт держит DB connection → `total_tokens >= db_pool.max_size`.

⚠️ Слишком высокий лимит → больше памяти на стеки потоков (1MB × N) и context switches.

## 39. Async Libraries — карта замен

| Sync (НЕ использовать в async def) | Async замена |
|---|---|
| `requests` | **`httpx.AsyncClient`** |
| `urllib.request` | **`httpx.AsyncClient`** или `aiohttp` |
| `psycopg2` / `psycopg` (sync) | **`asyncpg`** или `psycopg[async]` |
| SQLAlchemy 1.x sync | **SQLAlchemy 2.x async** + asyncpg |
| `redis-py` sync API | **`redis.asyncio`** (тот же пакет) |
| `pymongo` | **`motor`** или `pymongo` async (3.13+) |
| `boto3` | **`aioboto3`** или `aiobotocore` |
| `kafka-python` | **`aiokafka`** |
| `pika` (RabbitMQ) | **`aio-pika`** |
| `elasticsearch` (sync) | **`elasticsearch[async]`** |
| File I/O (`open()`) | **`aiofiles`** или `asyncio.to_thread(path.read_bytes)` |
| `subprocess.run` | **`asyncio.create_subprocess_exec`** |
| `time.sleep` | **`asyncio.sleep`** |
| `socket` | **`asyncio.open_connection`** |
| `imaplib` / `smtplib` | **`aioimaplib`** / `aiosmtplib` |

## 40. asyncio.to_thread — обёртка над sync

Если async замены нет — оборачиваем в threadpool.

```python
import asyncio

# GOOD: asyncio.to_thread (Python 3.9+) — простой случай
async def get_user_credit_score(user_id: int) -> int:
    """Sync либа credit_check_sdk не имеет async версии."""
    return await asyncio.to_thread(credit_check_sdk.get_score, user_id)


# Типобезопасная обёртка
from typing import ParamSpec, TypeVar
from collections.abc import Callable

P = ParamSpec("P")
T = TypeVar("T")

async def run_blocking(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """Выполняет блокирующую функцию в threadpool."""
    return await asyncio.to_thread(func, *args, **kwargs)
```

**Когда `to_thread` НЕ помогает:**
- CPU-bound на pure Python — GIL не отпускается, всё равно блокирует.
- Чрезвычайно быстрые вызовы (< 1ms) — overhead на switch выше выгоды.

## 41. CPU-bound — ProcessPoolExecutor

```python
from concurrent.futures import ProcessPoolExecutor

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.cpu_pool = ProcessPoolExecutor(max_workers=4)
    yield
    app.state.cpu_pool.shutdown(wait=True)


@router.post("/render-pdf")
async def render_pdf(data: RenderRequest, request: Request) -> bytes:
    """PDF рендеринг — CPU-bound, отдельный процесс."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        request.app.state.cpu_pool,
        render_pdf_sync,
        data.template_id,
        data.payload,
    )
```

⚠️ Аргументы должны быть picklable. Тяжёлые вычисления > секунды лучше выносить в Celery / отдельный микросервис.

## 42. Singleton Clients via Lifespan

Не создавай клиент на каждый запрос. Это HTTPS handshake каждый раз, нет переиспользования соединений.

```python
# BAD: новый клиент в каждом запросе
@router.get("/external-data")
async def get_data() -> dict:
    async with httpx.AsyncClient() as client:  # ❌
        response = await client.get("https://api.example.com/data")
        return response.json()


# GOOD: singleton через lifespan
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0),
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20,
            keepalive_expiry=30.0,
        ),
    )
    app.state.db_pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=10,
        max_size=50,
        max_inactive_connection_lifetime=300,
        command_timeout=30,
    )
    app.state.redis = redis.asyncio.from_url(
        settings.redis_url,
        max_connections=50,
        decode_responses=True,
    )

    yield

    # Graceful shutdown — обратный порядок
    await app.state.http_client.aclose()
    await app.state.redis.aclose()
    await app.state.db_pool.close()


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client

HttpClient = Annotated[httpx.AsyncClient, Depends(get_http_client)]


@router.get("/external-data")
async def get_data(client: HttpClient) -> dict:
    response = await client.get("https://api.example.com/data")
    return response.json()
```

**Несколько клиентов под разные сервисы:**
```python
# Разные timeouts/limits для разных backend'ов
app.state.payment_client = httpx.AsyncClient(
    base_url="https://gateway.example.com",
    timeout=httpx.Timeout(60.0, connect=10.0),  # платёжки медленные
    limits=httpx.Limits(max_connections=20),
)

app.state.notification_client = httpx.AsyncClient(
    base_url="https://notify.internal",
    timeout=httpx.Timeout(5.0),
    limits=httpx.Limits(max_connections=50),
)
```

## 43. Timeouts — на всё

Любая сетевая операция без таймаута = потенциально вечно висящий запрос. Висящие съедают connection pool, потом весь threadpool, потом весь сервис.

```python
# BAD: нет таймаута — может висеть часами
async with httpx.AsyncClient() as client:
    response = await client.get("https://slow-api.example.com")  # ❌


# GOOD: explicit timeout с разделением фаз
async with httpx.AsyncClient(
    timeout=httpx.Timeout(
        connect=5.0,    # установка TCP+TLS
        read=30.0,      # чтение после connect
        write=10.0,     # запись (для POST)
        pool=5.0,       # ожидание свободного connection в pool
    ),
) as client:
    response = await client.get("https://api.example.com")


# asyncio.timeout() — Python 3.11+, глобальный таймаут на блок
async def fetch_with_budget(url: str, budget_seconds: float = 10.0) -> str:
    try:
        async with asyncio.timeout(budget_seconds):
            response = await client.get(url)
            return response.text
    except TimeoutError:
        logger.warning("fetch_timeout", url=url, budget=budget_seconds)
        raise


# До 3.11 — asyncio.wait_for
result = await asyncio.wait_for(slow_operation(), timeout=10.0)
```

**DB query timeouts** — обязательны. Одна тяжёлая query без таймаута убьёт весь pool.

```python
# asyncpg
pool = await asyncpg.create_pool(
    dsn=settings.database_url,
    command_timeout=30,
)

# SQLAlchemy 2.x
engine = create_async_engine(
    settings.database_url,
    connect_args={
        "command_timeout": 30,
        "server_settings": {"statement_timeout": "30000"},  # PG ms
    },
)
```

**Default budgets:**

| Операция | Connect | Read | Total |
|---|---|---|---|
| Внутренний LAN сервис | 1s | 5s | 10s |
| Внешний API | 5s | 10s | 30s |
| Платёжный шлюз | 10s | 30s | 60s |
| LLM API | 5s | 60s | 120s |
| DB query (OLTP) | 1s | 5s | 10s |
| DB query (отчёт) | 1s | 30s | 60s |
| Redis | 0.5s | 1s | 2s |

Endpoint должен иметь **общий budget** меньше суммы внутренних таймаутов.

## 44. Connection Pools

Pool size **не должен** быть равен числу CPU. В async — pool size = ожидаемое число одновременных операций.

```python
# Database (asyncpg)
pool = await asyncpg.create_pool(
    dsn=DATABASE_URL,
    min_size=10,
    max_size=50,
    max_inactive_connection_lifetime=300,
    max_queries=50000,
    command_timeout=30,
)


# SQLAlchemy 2.x async
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
)


# Redis
redis_client = redis.asyncio.Redis(
    host=REDIS_HOST,
    max_connections=50,
    socket_timeout=2.0,
    socket_connect_timeout=2.0,
    health_check_interval=30,
    retry_on_timeout=True,
)


# httpx
client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20,
        keepalive_expiry=30.0,
    ),
)
```

**Формула pool size:**
```
DB pool size = (peak concurrent requests × queries per request) / target query duration

Пример: 200 RPS, 10ms query, 2 query на request → 4 в среднем → запас 5x → pool_size = 20
```

**Метрика:** `pool.in_use / pool.size`. Стабильно > 80% — увеличить. < 10% — уменьшить.

## 45. asyncio.gather vs TaskGroup

```python
# gather — независимые задачи, частичные неудачи OK
async def get_dashboard(user_id: int) -> Dashboard:
    user, orders, balance = await asyncio.gather(
        fetch_user(user_id),
        fetch_orders(user_id),
        fetch_balance(user_id),
    )
    return Dashboard(user=user, orders=orders, balance=balance)


# Устойчивость к частичным падениям
async def aggregate_stats(user_ids: list[int]) -> list[UserStats | None]:
    """Если один user-сервис упал — остальные результаты сохраняются."""
    results = await asyncio.gather(
        *(fetch_stats(uid) for uid in user_ids),
        return_exceptions=True,
    )
    return [r if not isinstance(r, Exception) else None for r in results]


# TaskGroup (3.11+) — структурированная конкурентность
# При падении любой задачи — все остальные cancel
async def get_dashboard(user_id: int) -> Dashboard:
    async with asyncio.TaskGroup() as tg:
        user_task = tg.create_task(fetch_user(user_id))
        orders_task = tg.create_task(fetch_orders(user_id))
        balance_task = tg.create_task(fetch_balance(user_id))

    return Dashboard(
        user=user_task.result(),
        orders=orders_task.result(),
        balance=balance_task.result(),
    )


# Обработка ошибок группы — except*
try:
    dashboard = await get_dashboard(user_id)
except* DBError as eg:
    for err in eg.exceptions:
        logger.exception("db_error", error=str(err))
    raise
except* HTTPError as eg:
    logger.warning("upstream_failures", count=len(eg.exceptions))
    raise
```

**Правило выбора:**
- `gather` — независимые задачи, можем переварить частичные неудачи.
- `TaskGroup` — связанные задачи, нужно либо всё, либо ничего.
- `as_completed` — обработка результатов в порядке готовности.

⚠️ Без `return_exceptions=True` в gather: первое исключение прерывает gather, **но другие задачи продолжают работать в фоне** (могут оставлять ресурсы открытыми).

## 46. Semaphore — ограничение конкурентности

```python
# Ограничение параллельных вызовов внешнего API
class RateLimitedClient:
    def __init__(self, client: httpx.AsyncClient, max_concurrent: int = 10) -> None:
        self._client = client
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch(self, url: str) -> dict:
        async with self._semaphore:
            response = await self._client.get(url)
            return response.json()


# Параллельная обработка батча с лимитом
async def process_batch(items: list[Item], max_concurrent: int = 20) -> list[Result]:
    """Не более 20 параллельных обработок одновременно."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_one(item: Item) -> Result:
        async with semaphore:
            return await heavy_processing(item)

    return await asyncio.gather(*(process_one(item) for item in items))
```

## 47. Cancellation — CancelledError

В asyncio когда клиент закрывает соединение, FastAPI отменяет task → `asyncio.CancelledError`.

```python
# CRITICAL BAD: глотает CancelledError → задача не отменяется
async def process_request():
    try:
        await long_operation()
    except Exception:  # ❌ ловит CancelledError тоже
        logger.exception("error")
        return {"status": "error"}


# GOOD: явно пробрасываем CancelledError
async def process_request():
    try:
        await long_operation()
    except asyncio.CancelledError:
        logger.info("request_cancelled")
        raise  # ОБЯЗАТЕЛЬНО — иначе task не остановится
    except SomeBusinessError:
        logger.exception("business_error")
        return {"status": "error"}


# GOOD: cleanup при отмене через try/finally
async def process_with_cleanup():
    resource = await acquire_resource()
    try:
        return await use_resource(resource)
    finally:
        await resource.release()  # выполнится даже при CancelledError


# asyncio.shield() — защита от cancellation для критичных операций
async def transfer_money(from_id: int, to_id: int, amount: Decimal) -> None:
    """Перевод средств — нельзя отменить после начала commit."""
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("UPDATE accounts SET balance = balance - $1 WHERE id = $2",
                               amount, from_id)
            await conn.execute("UPDATE accounts SET balance = balance + $1 WHERE id = $2",
                               amount, to_id)
            # клиент отвалился — нельзя отменить commit
            await asyncio.shield(record_audit_log(from_id, to_id, amount))
```

## 48. Fire-and-forget tasks правильно

`asyncio.create_task()` без удержания ссылки → task может быть собран GC.

```python
# BAD: задача может потеряться
async def notify():
    asyncio.create_task(send_email())  # ❌ нет ссылки → возможен GC


# GOOD: TaskManager для fire-and-forget
class TaskManager:
    """Менеджер для fire-and-forget задач — гарантированный lifecycle."""

    def __init__(self) -> None:
        self._tasks: set[asyncio.Task] = set()

    def spawn(self, coro: Awaitable[None]) -> asyncio.Task:
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def shutdown(self, timeout: float = 30.0) -> None:
        if not self._tasks:
            return
        try:
            async with asyncio.timeout(timeout):
                await asyncio.gather(*self._tasks, return_exceptions=True)
        except TimeoutError:
            for task in self._tasks:
                if not task.done():
                    task.cancel()


# Использование
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.tasks = TaskManager()
    yield
    await app.state.tasks.shutdown()


@router.post("/orders")
async def create_order(body: OrderCreate, request: Request) -> OrderResponse:
    order = await order_service.create(body)
    request.app.state.tasks.spawn(send_confirmation_email(order))
    return order
```

⚠️ **BackgroundTasks vs fire-and-forget vs Celery:**
- `BackgroundTasks` — после ответа, в том же процессе. **Если процесс умрёт — задача потеряна**.
- `create_task` + TaskManager — то же, но без привязки к request.
- **Celery / Dramatiq / Arq / Taskiq** — для надёжности (persistent queue, retries). Используй для критичных задач (email подтверждения, биллинг).

## 49. Database в Async — правильная работа

```python
# session.py
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)

session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,  # критично для async
    autoflush=False,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
```

**Lazy loading запрещён** — `MissingGreenlet` или скрытое блокирование.

```python
# BAD: lazy loading в async
user = await session.get(User, user_id)
print(user.orders)  # ❌ implicit IO в async context


# GOOD: eager loading через selectinload (отдельный SELECT)
from sqlalchemy.orm import selectinload, joinedload

user = await session.scalar(
    select(User)
    .options(selectinload(User.orders))
    .where(User.id == user_id),
)


# joinedload — JOIN для one-to-one
user = await session.scalar(
    select(User)
    .options(joinedload(User.profile))
    .where(User.id == user_id),
)
```

**Стратегии eager loading:**
- `selectinload` — отдельный `SELECT WHERE id IN (...)`. Хорошо для one-to-many.
- `joinedload` — JOIN. Для one-to-one и small one-to-many.

**Транзакции:**
```python
async def transfer(session: AsyncSession, from_id: int, to_id: int, amount: Decimal) -> None:
    async with session.begin():
        from_account = await session.get(Account, from_id, with_for_update=True)
        to_account = await session.get(Account, to_id, with_for_update=True)

        if from_account.balance < amount:
            raise InsufficientFundsError()

        from_account.balance -= amount
        to_account.balance += amount
    # commit при выходе, rollback при exception
```

**Bulk операции:**
```python
# 10K записей
await session.execute(insert(OrderItem), [{...} for p in products])
await session.commit()


# Upsert (PostgreSQL)
from sqlalchemy.dialects.postgresql import insert as pg_insert

stmt = pg_insert(User).values(rows).on_conflict_do_update(
    index_elements=["email"],
    set_={"updated_at": func.now()},
)
await session.execute(stmt)
```

## 50. Race Conditions — async ≠ нет race

Async — concurrent, не parallel (один thread). Между `await` точками возможны переключения → race conditions.

```python
# BAD: classic check-then-act race
class CounterService:
    def __init__(self) -> None:
        self._count = 0

    async def increment_if_below(self, limit: int) -> None:
        if self._count < limit:        # ← переключение возможно здесь
            await asyncio.sleep(0)     # ← между check и act
            self._count += 1           # ← race! Может превысить limit


# GOOD: asyncio.Lock для критической секции
class CounterService:
    def __init__(self) -> None:
        self._count = 0
        self._lock = asyncio.Lock()

    async def increment_if_below(self, limit: int) -> bool:
        async with self._lock:
            if self._count >= limit:
                return False
            await asyncio.sleep(0)
            self._count += 1
            return True
```

**Распределённые блокировки** — для multi-pod через Redis:
```python
async def acquire_lock(redis: Redis, key: str, ttl: int = 30) -> str | None:
    """Возвращает токен если получили блокировку."""
    token = secrets.token_hex(16)
    acquired = await redis.set(key, token, nx=True, ex=ttl)
    return token if acquired else None


async def release_lock(redis: Redis, key: str, token: str) -> None:
    """Релизим только если токен совпадает (защита от чужой блокировки)."""
    lua = """
    if redis.call('GET', KEYS[1]) == ARGV[1] then
        return redis.call('DEL', KEYS[1])
    else
        return 0
    end
    """
    await redis.eval(lua, 1, key, token)
```

**Pessimistic vs Optimistic vs Idempotency keys:**

| Паттерн | Когда |
|---|---|
| Pessimistic (`SELECT FOR UPDATE`) | Высокая частота конфликтов, короткие транзакции |
| Optimistic (version column) | Редкие конфликты, не блокируем читателей |
| Idempotency keys | Внешние API, безопасный re-try |

```python
# Idempotency через ключ запроса
@router.post("/payments")
async def create_payment(
    body: PaymentCreate,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    db: DbSession,
    redis: RedisDep,
) -> PaymentResponse:
    """Если ключ уже обработан — возвращаем предыдущий результат."""
    cache_key = f"idempotency:payment:{idempotency_key}"
    if cached := await redis.get(cache_key):
        return PaymentResponse.model_validate_json(cached)

    payment = await payment_service.create(db, body)
    response = PaymentResponse.model_validate(payment)
    await redis.set(cache_key, response.model_dump_json(), ex=86400)
    return response
```

## 51. Context Propagation — contextvars

`threading.local` не работает в async — один thread обрабатывает много coroutine'ов.

```python
# BAD: threading.local — все coro видят одно значение
import threading
_request_context = threading.local()


# GOOD: contextvars — propagates через await, изолирован per-task
from contextvars import ContextVar

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_var: ContextVar[int | None] = ContextVar("user_id", default=None)
tenant_id_var: ContextVar[str | None] = ContextVar("tenant_id", default=None)


# Middleware устанавливает request_id для всего запроса
class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        token = request_id_var.set(request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_var.reset(token)


# structlog с contextvars — автоматически в каждой записи
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,  # подтягивает все ContextVar
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    cache_logger_on_first_use=True,  # существенный perf bonus
)


# В middleware биндим контекст
async def dispatch(self, request: Request, call_next):
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request.headers.get("X-Request-ID") or str(uuid4()),
        path=request.url.path,
        method=request.method,
    )
    # все логи в этом запросе автоматически получат request_id, path, method
```

## 52. Logging без блокировок

`FileHandler.emit()` делает sync `write()`. На загруженных дисках/сетевых fs — блок event loop.

```python
# BAD: запись в файл блокирует loop
logging.basicConfig(handlers=[logging.FileHandler("app.log")])


# GOOD: QueueHandler + QueueListener — асинхронная запись
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

log_queue: Queue = Queue(maxsize=10000)
queue_handler = QueueHandler(log_queue)

file_handler = logging.FileHandler("app.log")
listener = QueueListener(log_queue, file_handler, respect_handler_level=True)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    listener.start()
    yield
    listener.stop()


root_logger = logging.getLogger()
root_logger.addHandler(queue_handler)
```

⚠️ В Docker/k8s **stdout** обычно достаточно. FileHandler не нужен — оркестратор разруливает.

## 53. Streaming Responses

`return huge_dict` загрузит 1GB в память. Для больших данных — `StreamingResponse`.

```python
# BAD: материализуем 1млн записей в память
@router.get("/export/orders.csv")
async def export_csv(db: DbSession) -> Response:
    orders = await db.execute(select(Order))  # ❌ всё в память
    csv_text = render_csv(orders.scalars().all())
    return Response(csv_text, media_type="text/csv")


# GOOD: streaming через async generator
from fastapi.responses import StreamingResponse

async def stream_orders_csv(db: AsyncSession) -> AsyncIterator[str]:
    """Стримит CSV строки по мере получения из БД."""
    yield "id,customer_id,total,created_at\n"

    stmt = select(Order).execution_options(yield_per=1000)
    async for order in await db.stream_scalars(stmt):
        yield f"{order.id},{order.customer_id},{order.total},{order.created_at.isoformat()}\n"


@router.get("/export/orders.csv")
async def export_csv(db: DbSession) -> StreamingResponse:
    return StreamingResponse(
        stream_orders_csv(db),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders.csv"},
    )


# Upload больших файлов — чанками
import aiofiles

@router.post("/upload")
async def upload(file: UploadFile) -> dict:
    """Сохраняем файл потоково."""
    target = Path(f"/uploads/{file.filename}")
    async with aiofiles.open(target, "wb") as out:
        while chunk := await file.read(64 * 1024):  # 64KB
            await out.write(chunk)
    return {"filename": file.filename, "size": target.stat().st_size}
```

## 54. Workers & Deployment

| Профиль | Workers | Reasoning |
|---|---|---|
| **I/O-bound** (90% async) | 1-2 на pod, scale via replicas | Async масштабируется внутри одного worker'а |
| **Mix sync/async** | `cpu_count` | Sync endpoints в threadpool блокируют worker |
| **CPU-bound** | `cpu_count + 1` | Используй ProcessPool внутри или Celery |

```bash
# Production: gunicorn + uvicorn workers
gunicorn myservice.api:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    --timeout 60 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --max-requests 10000 \
    --max-requests-jitter 1000


# Direct uvicorn (container-based)
uvicorn myservice.api:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --loop uvloop \
    --http httptools \
    --limit-concurrency 1000 \
    --timeout-keep-alive 5
```

`--max-requests` обязателен — пересоздавать worker после N запросов чтобы избежать утечек памяти.

**Graceful shutdown** — при `SIGTERM`:
1. Перестать принимать новые соединения.
2. Дождаться in-flight запросов (с лимитом).
3. Закрыть pools в обратном порядке.

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup
    app.state.http_client = httpx.AsyncClient(...)
    app.state.db_pool = await asyncpg.create_pool(...)
    app.state.tasks = TaskManager()
    logger.info("app_started")

    yield

    # Shutdown — обратный порядок
    logger.info("app_shutting_down")
    await app.state.tasks.shutdown(timeout=30)        # 1. дождаться фоновых
    await app.state.http_client.aclose()              # 2. закрыть HTTP
    await app.state.db_pool.close()                   # 3. закрыть БД
    logger.info("app_stopped")
```

⚠️ В Kubernetes: `terminationGracePeriodSeconds` должен быть > graceful timeout.

**Health checks правильно:**
```python
@router.get("/health/liveness", include_in_schema=False)
async def liveness() -> dict[str, str]:
    """Жив ли процесс. БЕЗ проверок зависимостей.
    Если упадёт — k8s перезапустит pod."""
    return {"status": "ok"}


@router.get("/health/readiness", include_in_schema=False)
async def readiness(db: DbSession, redis: RedisDep) -> dict[str, object]:
    """Готов ли принимать трафик. Проверяем зависимости.
    Если упадёт — k8s выведет pod из service endpoints."""
    checks: dict[str, str] = {}
    overall_ok = True

    try:
        async with asyncio.timeout(2.0):
            await db.execute(text("SELECT 1"))
            checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"
        overall_ok = False

    try:
        async with asyncio.timeout(1.0):
            await redis.ping()
            checks["redis"] = "ok"
    except Exception as exc:
        checks["redis"] = f"error: {exc}"
        overall_ok = False

    if not overall_ok:
        raise HTTPException(status_code=503, detail=checks)
    return {"status": "ok", "checks": checks}
```

⚠️ **Не делай тяжёлые проверки в liveness** — каскадные restart'ы при флапе зависимости.

## 55. Backpressure & Resilience

```bash
# Concurrency limit на сервер
uvicorn myservice.api:app --limit-concurrency 1000
# При >1000 одновременных соединений — отвергает с 503
# Лучше быстрый отказ, чем медленный треш
```

**Rate limiting** через fastapi-limiter:
```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    redis_client = redis.asyncio.from_url(settings.redis_url, decode_responses=True)
    await FastAPILimiter.init(redis_client)
    yield
    await FastAPILimiter.close()


@router.post(
    "/expensive-operation",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],  # 10 req/min
)
async def expensive_op() -> dict: ...
```

**Circuit breaker** для нестабильных upstream:
```python
# pip install pybreaker
import pybreaker

payment_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30,
)

@payment_breaker
async def call_payment_gateway(amount: Decimal) -> PaymentResult:
    """После 5 фейлов подряд breaker откроется на 30s — быстрые отказы."""
    return await payment_client.charge(amount)
```

Альтернативы для async: `aiocircuitbreaker`, `purgatory`.

**Retries с экспоненциальным backoff:**
```python
# pip install tenacity
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.HTTPError),
    reraise=True,
)
async def fetch_with_retry(url: str) -> dict:
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
```

## 56. Anti-patterns Cheatsheet

```python
# ─── Sync клиент в async ────────────────────────────────────────
# ❌ NEVER:
async def handler():
    response = requests.get(url)            # блок event loop

# ✅ ALWAYS:
async def handler(client: HttpClient):
    response = await client.get(url)


# ─── Создание клиента в handler ─────────────────────────────────
# ❌ NEVER:
async def handler():
    async with httpx.AsyncClient() as c:    # новый pool каждый раз
        ...

# ✅ ALWAYS: singleton через lifespan


# ─── Запросы без таймаута ───────────────────────────────────────
# ❌ NEVER:
async with httpx.AsyncClient() as c:
    await c.get(url)

# ✅ ALWAYS:
async with httpx.AsyncClient(timeout=httpx.Timeout(30, connect=5)) as c:
    await c.get(url)


# ─── time.sleep ─────────────────────────────────────────────────
# ❌ NEVER:
async def retry():
    time.sleep(1)                           # блок event loop

# ✅ ALWAYS:
async def retry():
    await asyncio.sleep(1)


# ─── except Exception без re-raise CancelledError ────────────
# ❌ DANGEROUS:
try:
    await long()
except Exception:
    pass

# ✅ ALWAYS:
try:
    await long()
except asyncio.CancelledError:
    raise
except Exception:
    handle()


# ─── Lazy loading в async SQLAlchemy ────────────────────────────
# ❌ NEVER:
user = await session.get(User, uid)
print(user.orders)                          # MissingGreenlet

# ✅ ALWAYS:
user = await session.scalar(
    select(User).options(selectinload(User.orders)).where(User.id == uid)
)


# ─── threading.local в async ────────────────────────────────────
# ❌ NEVER:
_ctx = threading.local()
_ctx.user = current_user

# ✅ ALWAYS:
user_var: ContextVar[User] = ContextVar("user")
user_var.set(current_user)


# ─── fire-and-forget без удержания ссылки ───────────────────────
# ❌ NEVER:
asyncio.create_task(send_email())           # GC может убить

# ✅ ALWAYS: TaskManager с _tasks: set[Task]


# ─── Глобальный mutable state без Lock ──────────────────────────
# ❌ NEVER:
_counter = 0
async def inc():
    global _counter
    _counter += 1                           # race между await

# ✅ ALWAYS: asyncio.Lock или Redis INCR


# ─── Unbounded gather ───────────────────────────────────────────
# ❌ NEVER:
await asyncio.gather(*(fetch(u) for u in 100_000_users))  # 100K сокетов

# ✅ ALWAYS: Semaphore или batch


# ─── sync session в async endpoint ──────────────────────────────
# ❌ NEVER:
@router.get("/users")
async def get_users(db: Session = Depends(get_sync_db)):
    users = db.query(User).all()            # sync IO в async!

# ✅ ALWAYS:
async def get_users(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User))
    return result.scalars().all()


# ─── BackgroundTasks для критичных операций ─────────────────────
# ❌ NEVER:
@router.post("/payment")
async def pay(bg: BackgroundTasks):
    bg.add_task(charge_card, ...)           # потеряется если pod упадёт

# ✅ ALWAYS: Celery/Dramatiq/Arq с persistent queue
```

<!-- /section:concurrency -->

---

# Quick Checklist

Before submitting Python code:

**Project & Toolchain (rules 1–4):**
- [ ] `src/` layout, `pyproject.toml` единый конфиг
- [ ] Ruff (`select = ["ALL"]`), Pyright `strict=true`
- [ ] pre-commit гейт настроен

**Type System (rules 5–10):**
- [ ] `from __future__ import annotations` в каждом файле
- [ ] Все функции/параметры/возвраты типизированы
- [ ] Запрет `Any` — только с `# type: ignore[reason]`
- [ ] `Final`, `Literal`, `NewType`, `Self`, `@override` где уместно
- [ ] `Protocol` для DI, `ABC` только для template method
- [ ] `assert_never` для exhaustive `match`
- [ ] `TYPE_CHECKING` для разрыва циклов

**Data Modeling (rules 11–13):**
- [ ] `@dataclass(frozen=True, slots=True, kw_only=True)` по умолчанию
- [ ] Pydantic — на API границе, dataclass — внутри
- [ ] StrEnum/IntEnum, никаких магических строк

**Errors (rules 14–18):**
- [ ] Иерархия `AppError → DomainError/InfrastructureError → ...`
- [ ] `raise ... from exc` всегда — сохраняем причину
- [ ] `ExceptionGroup` для пачки ошибок (Python 3.11+)
- [ ] Никаких `except:` без `raise` или явного восстановления
- [ ] `assert` запрещён в production (только в тестах)

**Logging & I/O (rules 19–22):**
- [ ] `structlog` или stdlib `logging` с `%s` форматом
- [ ] `print()` — только в CLI entry points
- [ ] `pathlib.Path`, никогда `os.path`
- [ ] `with` для всех ресурсов, кастомные через `@contextmanager`

**Idioms (rules 23–26):**
- [ ] Comprehensions один уровень, вложенные → функции
- [ ] `match/case` для discriminated unions
- [ ] `@cache`/`@lru_cache`/`@cached_property`/`@singledispatch` где уместно
- [ ] `async` только для реального I/O, `gather`/`TaskGroup` для параллели

**FastAPI (rules 27–35):**
- [ ] APIRouter по доменам, `main.py` только сборка
- [ ] Pydantic v2: `field_validator`, `model_validator`, `computed_field`
- [ ] `Depends()` + `Annotated` type aliases для DI
- [ ] `response_model` и `status_code` явно
- [ ] Глобальный `exception_handler` для единого формата
- [ ] `lifespan` для startup/shutdown (НЕ `on_event`)
- [ ] `BackgroundTasks` для лёгких фоновых, Celery — для тяжёлых
- [ ] CORS/logging через middleware
- [ ] `pydantic-settings` BaseSettings, не `os.getenv`

**Async Concurrency (rules 36–56):**

*Event loop integrity:*
- [ ] В `async def` нет sync клиентов (`requests`, `psycopg2`, `boto3`, `redis-py` sync)
- [ ] Sync библиотеки обёрнуты в `asyncio.to_thread()` или endpoint объявлен `def`
- [ ] CPU-bound вынесен в ProcessPool / Celery
- [ ] `time.sleep()` → `asyncio.sleep()` везде
- [ ] uvloop включён в production

*Clients & Pools:*
- [ ] Все клиенты (httpx, db, redis) — singleton через `lifespan`
- [ ] httpx.Limits настроены (max_connections, keepalive)
- [ ] DB pool: `pool_size`, `max_overflow`, `pool_pre_ping=True`, `pool_recycle`
- [ ] AnyIO threadpool увеличен если используются sync endpoints

*Timeouts:*
- [ ] httpx.Timeout с разделением connect/read/write/pool
- [ ] DB `command_timeout` или PG `statement_timeout`
- [ ] `asyncio.timeout()` на критичные блоки
- [ ] Endpoint budget < сумма внутренних таймаутов

*Concurrency:*
- [ ] `asyncio.gather` для независимых, `TaskGroup` для связанных
- [ ] Semaphore для ограничения параллельных вызовов upstream
- [ ] Fire-and-forget через TaskManager (с удержанием ссылок)
- [ ] `asyncio.Lock` для критических секций in-memory state
- [ ] Распределённые блокировки через Redis для multi-pod

*Cancellation:*
- [ ] `except asyncio.CancelledError: raise` явно
- [ ] `try/finally` для cleanup
- [ ] `asyncio.shield()` для атомарных операций
- [ ] Никогда не глотать `CancelledError`

*Database:*
- [ ] SQLAlchemy 2.x async + `expire_on_commit=False`
- [ ] `selectinload`/`joinedload` вместо lazy loading
- [ ] Транзакции через `session.begin()` контекст
- [ ] Optimistic locking (version column) или idempotency keys

*Context & Logging:*
- [ ] `contextvars` для request_id, user_id, tenant_id (НЕ `threading.local`)
- [ ] `structlog.contextvars.merge_contextvars` в processors
- [ ] QueueHandler если пишем в файл; stdout-only в Docker/k8s

*Streaming:*
- [ ] `StreamingResponse` для больших ответов
- [ ] `UploadFile.read(chunk_size)` для больших uploads
- [ ] `aiofiles` или `to_thread` для файлового I/O

*Deployment:*
- [ ] `--workers` подобраны под профиль (I/O = меньше, CPU = больше)
- [ ] `--max-requests` для пересоздания worker'ов
- [ ] Graceful shutdown через lifespan (закрытие pools в обратном порядке)
- [ ] `terminationGracePeriodSeconds` в k8s > graceful timeout
- [ ] `/health/liveness` без зависимостей, `/health/readiness` с проверками
- [ ] `--limit-concurrency` для backpressure

*Resilience:*
- [ ] Rate limiting на тяжёлые эндпоинты (fastapi-limiter)
- [ ] Circuit breaker для нестабильных upstream
- [ ] Retries с экспоненциальным backoff (tenacity)
- [ ] Idempotency keys на write эндпоинты
