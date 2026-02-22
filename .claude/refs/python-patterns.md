# Python Code Standards

<!-- section:core -->

## 1. Type Hints Everywhere

Все функции, переменные, параметры — с аннотациями типов. Без исключений.

```python
# BAD: Нет типов — агент не понимает контракт
def process_order(order, items):
    total = 0
    for item in items:
        total += item["price"] * item["qty"]
    return {"order_id": order["id"], "total": total}


# GOOD: Явные типы — контракт виден сразу
from decimal import Decimal

def process_order(order: Order, items: list[OrderItem]) -> OrderResult:
    total: Decimal = sum(
        item.price * item.quantity for item in items
    )
    return OrderResult(order_id=order.id, total=total)
```

**Правила:**
```python
# Коллекции — встроенные generic (Python 3.9+)
names: list[str] = []
config: dict[str, int] = {}
unique_ids: set[int] = set()

# Optional — через union (Python 3.10+)
description: str | None = None

# Callable
handler: Callable[[Request], Response]

# Возвращаемый тип — ВСЕГДА
def get_name() -> str: ...
def save(item: Item) -> None: ...
async def fetch(url: str) -> bytes: ...
```

## 2. Dataclasses for Data Containers

`dataclass` для внутренних данных, Pydantic для API-границ.

```python
# BAD: Голые dict'ы — нет автодополнения, нет валидации
def create_user(name, email):
    return {"name": name, "email": email, "created_at": datetime.now()}

user = create_user("Ivan", "ivan@test.com")
print(user["nmae"])  # KeyError в рантайме, опечатка не поймана


# GOOD: dataclass — типизированный контейнер
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class User:
    """Пользователь системы."""
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)

user = User(name="Ivan", email="ivan@test.com")
print(user.nmae)  # AttributeError сразу в IDE!
```

**Когда что использовать:**
```python
# dataclass — внутренние данные, DTO между слоями
@dataclass(frozen=True)
class OrderCalculation:
    """Результат расчёта стоимости заказа."""
    subtotal: Decimal
    tax: Decimal
    total: Decimal

# Pydantic BaseModel — входные/выходные данные API (см. section:fastapi)
# NamedTuple — лёгкие неизменяемые кортежи
class Point(NamedTuple):
    x: float
    y: float
```

## 3. Enum for Constants

Никаких магических строк. Enum для всех перечислений.

```python
# BAD: Магические строки — опечатка = баг
def set_status(order, status: str) -> None:
    order.status = status  # "active"? "Active"? "ACTIVE"?

set_status(order, "actve")  # Опечатка, баг в продакшне


# GOOD: Enum — компилятор/линтер поймает ошибку
from enum import StrEnum

class OrderStatus(StrEnum):
    """Статусы заказа в жизненном цикле."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

def set_status(order: Order, status: OrderStatus) -> None:
    order.status = status

set_status(order, OrderStatus.CONFIRMED)  # Автодополнение, безопасность
```

**StrEnum vs Enum:**
```python
# StrEnum (Python 3.11+) — сериализуется в строку автоматически
class Color(StrEnum):
    RED = "red"
    GREEN = "green"

print(Color.RED)  # "red" — можно использовать в JSON напрямую

# IntEnum — для числовых констант
class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
```

## 4. Async/Await Patterns

Async — только для реального I/O. Не для CPU-bound задач.

```python
# BAD: async без причины — добавляет overhead
async def calculate_tax(amount: Decimal) -> Decimal:
    return amount * Decimal("0.20")  # Чистый расчёт, async не нужен


# GOOD: async для реального I/O
async def fetch_user(user_id: int) -> User:
    """Загрузка пользователя из БД (реальный I/O)."""
    async with async_session() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none()

# GOOD: sync для вычислений
def calculate_tax(amount: Decimal) -> Decimal:
    """Расчёт налога (чистая функция, без I/O)."""
    return amount * Decimal("0.20")
```

**Параллельный I/O:**
```python
# BAD: Последовательные запросы
async def get_dashboard(user_id: int) -> Dashboard:
    user = await fetch_user(user_id)
    orders = await fetch_orders(user_id)    # Ждёт user!
    balance = await fetch_balance(user_id)  # Ждёт orders!

# GOOD: Параллельное выполнение через gather
async def get_dashboard(user_id: int) -> Dashboard:
    user, orders, balance = await asyncio.gather(
        fetch_user(user_id),
        fetch_orders(user_id),
        fetch_balance(user_id),
    )
    return Dashboard(user=user, orders=orders, balance=balance)
```

## 5. Error Handling

Кастомные исключения с контекстом. ExceptionGroup для Python 3.11+.

```python
# BAD: Голые Exception без контекста
def get_user(user_id: int):
    user = db.find(user_id)
    if not user:
        raise Exception("not found")  # Какой user? Что делать?


# GOOD: Кастомные исключения с контекстом
class AppError(Exception):
    """Базовое исключение приложения."""
    def __init__(self, message: str, code: str = "UNKNOWN") -> None:
        self.message = message
        self.code = code
        super().__init__(message)

class NotFoundError(AppError):
    """Сущность не найдена."""
    def __init__(self, entity: str, entity_id: str | int) -> None:
        super().__init__(
            message=f"{entity} с id={entity_id} не найден",
            code="NOT_FOUND",
        )
        self.entity = entity
        self.entity_id = entity_id

class ValidationError(AppError):
    """Ошибка валидации входных данных."""
    def __init__(self, field: str, reason: str) -> None:
        super().__init__(
            message=f"Поле '{field}': {reason}",
            code="VALIDATION_ERROR",
        )

# Использование — информативно
def get_user(user_id: int) -> User:
    user = db.find(user_id)
    if user is None:
        raise NotFoundError("User", user_id)
    return user
```

**ExceptionGroup (Python 3.11+):**
```python
# Сбор нескольких ошибок валидации
def validate_order(order: OrderInput) -> None:
    errors: list[ValidationError] = []
    if not order.customer_id:
        errors.append(ValidationError("customer_id", "обязательное поле"))
    if order.total < 0:
        errors.append(ValidationError("total", "не может быть отрицательным"))
    if errors:
        raise ExceptionGroup("Ошибки валидации заказа", errors)
```

## 6. Logging with structlog

Структурированные логи. Никогда print() в production.

```python
# BAD: print — не видно в логах, нет уровней, нет контекста
def process_payment(order_id: str, amount: float):
    print(f"Processing payment for {order_id}")
    print(f"Amount: {amount}")
    print("Done!")


# GOOD: structlog — структурированные логи с контекстом
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
        log.error("payment_failed", error=str(exc), gateway=gateway.name)
        raise
```

**Если structlog не доступен — стандартный logging:**
```python
import logging

logger = logging.getLogger(__name__)

def process_payment(order_id: str, amount: Decimal) -> PaymentResult:
    logger.info("Обработка платежа: order=%s, amount=%s", order_id, amount)
    # НЕ: logger.info(f"Обработка платежа: order={order_id}")  # f-string расходует CPU даже если лог выключен
```

## 7. pathlib over os.path

`pathlib.Path` — единственный правильный способ работы с путями.

```python
# BAD: os.path — строковые операции, нечитаемо
import os

config_path = os.path.join(os.path.dirname(__file__), "..", "config", "app.yaml")
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        data = f.read()


# GOOD: pathlib — объектный API, кроссплатформенный
from pathlib import Path

CONFIG_DIR: Path = Path(__file__).parent.parent / "config"

def load_config(name: str = "app.yaml") -> str:
    config_path: Path = CONFIG_DIR / name
    if not config_path.exists():
        raise FileNotFoundError(f"Конфиг не найден: {config_path}")
    return config_path.read_text(encoding="utf-8")
```

**Полезные методы pathlib:**
```python
path = Path("/data/reports/2024")

path.mkdir(parents=True, exist_ok=True)  # Создать с родителями
path.iterdir()                            # Итерация по содержимому
path.glob("*.csv")                        # Поиск файлов
path.suffix                               # ".csv"
path.stem                                 # "report"
path.with_suffix(".json")                 # Замена расширения
path.read_text(encoding="utf-8")          # Чтение
path.write_text(data, encoding="utf-8")   # Запись
```

## 8. Comprehensions: Readable, Not Nested

Одна операция на comprehension. Вложенные — разбить на функции.

```python
# BAD: Вложенный comprehension — нечитаемо
result = [
    transform(item)
    for group in data
    if group.is_active
    for item in group.items
    if item.price > 0 and item.category in allowed_categories
]


# GOOD: Разбить на шаги или использовать функции
active_items: list[Item] = [
    item
    for group in data if group.is_active
    for item in group.items
]

def is_eligible(item: Item) -> bool:
    """Проверяет, подходит ли товар по цене и категории."""
    return item.price > 0 and item.category in allowed_categories

result: list[TransformedItem] = [
    transform(item)
    for item in active_items
    if is_eligible(item)
]
```

**Словарные comprehensions:**
```python
# GOOD: dict comprehension для трансформации
users_by_id: dict[int, User] = {
    user.id: user for user in users
}

# GOOD: set comprehension для уникальных значений
unique_emails: set[str] = {
    user.email.lower() for user in users
}
```

## 9. Context Managers

`with` для любых ресурсов. contextlib для простых случаев.

```python
# BAD: Ручное управление ресурсами
def export_data(data: list[dict], path: Path) -> None:
    f = open(path, "w")
    try:
        json.dump(data, f)
    finally:
        f.close()  # Можно забыть!


# GOOD: Context manager
def export_data(data: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

**Кастомный context manager через contextlib:**
```python
from contextlib import contextmanager, asynccontextmanager
import time

@contextmanager
def measure_time(operation: str):
    """Замер времени выполнения операции."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info("operation_completed", operation=operation, elapsed_ms=elapsed * 1000)

# Использование
with measure_time("db_query"):
    results = db.execute(query)

# Async вариант
@asynccontextmanager
async def db_transaction(session: AsyncSession):
    """Транзакция с автоматическим rollback при ошибке."""
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
```

## 10. ABC/Protocol for Interfaces

Protocol для duck typing, ABC для строгих контрактов.

```python
# BAD: Неявный контракт — надо читать код чтобы понять интерфейс
class EmailSender:
    def send(self, to, subject, body):
        ...

class SmsSender:
    def send_message(self, phone, text):  # Другое имя метода!
        ...


# GOOD: Protocol — структурная типизация (duck typing с проверкой)
from typing import Protocol

class NotificationSender(Protocol):
    """Контракт для отправки уведомлений."""
    def send(self, recipient: str, message: str) -> bool: ...

class EmailSender:
    """Отправка через email. Реализует NotificationSender неявно."""
    def send(self, recipient: str, message: str) -> bool:
        # smtp.send_mail(...)
        return True

class SmsSender:
    """Отправка через SMS. Реализует NotificationSender неявно."""
    def send(self, recipient: str, message: str) -> bool:
        # sms_gateway.send(...)
        return True

def notify(sender: NotificationSender, recipient: str, message: str) -> bool:
    return sender.send(recipient, message)

# Оба класса подходят — проверка в mypy/pyright
notify(EmailSender(), "user@test.com", "Hello")
notify(SmsSender(), "+79001234567", "Hello")
```

**ABC — когда нужен строгий контракт с общей логикой:**
```python
from abc import ABC, abstractmethod

class BaseRepository(ABC):
    """Базовый репозиторий с общей логикой."""

    @abstractmethod
    async def find_by_id(self, entity_id: int) -> dict | None:
        """Найти сущность по ID."""
        ...

    @abstractmethod
    async def save(self, entity: dict) -> dict:
        """Сохранить сущность."""
        ...

    async def find_or_raise(self, entity_id: int) -> dict:
        """Найти или бросить NotFoundError (общая логика)."""
        result = await self.find_by_id(entity_id)
        if result is None:
            raise NotFoundError(self.__class__.__name__, entity_id)
        return result
```

<!-- /section:core -->

---

<!-- section:fastapi -->

## 11. APIRouter for Modular Endpoints

Все эндпоинты по роутерам. main.py только собирает приложение.

```python
# BAD: Всё в одном файле
# main.py — 500 строк эндпоинтов
app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int): ...

@app.post("/users")
async def create_user(user: UserCreate): ...

@app.get("/orders/{order_id}")
async def get_order(order_id: int): ...

# ... ещё 50 эндпоинтов


# GOOD: Роутеры по доменам
# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Получение пользователя по ID."""
    return await service.get_by_id(user_id)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Создание нового пользователя."""
    return await service.create(body)

# app/main.py — только сборка
from fastapi import FastAPI
from app.routers import users, orders, payments

app = FastAPI(title="My Service")
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(payments.router)
```

## 12. Pydantic v2 BaseModel

Валидация на границе API. field_validator, model_validator, computed_field.

```python
# BAD: Ручная валидация в эндпоинте
@router.post("/orders")
async def create_order(data: dict):
    if "customer_id" not in data:
        raise HTTPException(400, "customer_id required")
    if data.get("total", 0) < 0:
        raise HTTPException(400, "total must be positive")
    # ... ещё 20 строк валидации


# GOOD: Pydantic v2 — валидация декларативно
from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
from typing_extensions import Self

class OrderCreate(BaseModel):
    """Данные для создания заказа."""
    customer_id: int = Field(..., gt=0, description="ID покупателя")
    items: list[OrderItemCreate] = Field(..., min_length=1, description="Позиции заказа")
    discount_percent: float = Field(default=0, ge=0, le=100)
    comment: str | None = Field(default=None, max_length=500)

    @field_validator("items")
    @classmethod
    def validate_unique_products(cls, v: list[OrderItemCreate]) -> list[OrderItemCreate]:
        """Проверяет уникальность товаров в заказе."""
        product_ids = [item.product_id for item in v]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Дублирующиеся товары в заказе")
        return v

    @computed_field
    @property
    def total_items(self) -> int:
        """Общее количество позиций (вычисляемое поле)."""
        return len(self.items)

class OrderItemCreate(BaseModel):
    """Позиция заказа."""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=10000)
    price: Decimal = Field(..., gt=0, decimal_places=2)
```

**model_validator — проверка связей между полями:**
```python
class DateRange(BaseModel):
    """Диапазон дат."""
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        """end_date должна быть после start_date."""
        if self.end_date <= self.start_date:
            raise ValueError("end_date должна быть позже start_date")
        return self
```

## 13. Depends() for Dependency Injection

Depends — единственный способ внедрения зависимостей в FastAPI.

```python
# BAD: Глобальные объекты, импорты сервисов напрямую
from app.database import db_session  # Глобальный объект!

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = db_session.query(User).get(user_id)  # Нетестируемо
    return user


# GOOD: Depends() — тестируемо, заменяемо
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Сессия БД с автоматическим закрытием."""
    async with async_session_factory() as session:
        yield session

async def get_user_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserService:
    """Сервис пользователей с внедрённой сессией."""
    return UserService(db)

# Annotated для переиспользования
DbSession = Annotated[AsyncSession, Depends(get_db)]

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Получение пользователя — зависимости внедряются автоматически."""
    return await service.get_by_id(user_id)
```

## 14. Response Models and Status Codes

Явные response_model и status_code на каждом эндпоинте.

```python
# BAD: Нет response_model — клиент не знает формат ответа
@router.post("/users")
async def create_user(data: UserCreate):
    user = await service.create(data)
    return user  # Что вернётся? Какие поля?


# GOOD: Явный контракт — документация генерируется автоматически
from fastapi import status

class UserResponse(BaseModel):
    """Ответ с данными пользователя."""
    id: int
    email: str
    display_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # Позволяет из ORM-модели

class UserListResponse(BaseModel):
    """Список пользователей с пагинацией."""
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
async def create_user(
    body: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Создаёт нового пользователя и возвращает его данные."""
    return await service.create(body)

@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: Annotated[UserService, Depends(get_user_service)] = ...,
) -> UserListResponse:
    """Список пользователей с пагинацией."""
    return await service.list(page=page, page_size=page_size)
```

## 15. HTTPException with Detail

Информативные HTTP-ошибки. Кастомный exception handler для единого формата.

```python
# BAD: Скудные ошибки — клиент не понимает что пошло не так
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.find(user_id)
    if not user:
        raise HTTPException(404)  # Что не найдено?


# GOOD: Информативные ошибки + единый обработчик
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

# Кастомные исключения приложения
class AppError(Exception):
    """Базовая ошибка приложения."""
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

# Глобальный обработчик — единый формат ответов
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

## 16. Middleware Patterns

CORS, логирование, аутентификация — через middleware.

```python
# BAD: CORS/логирование в каждом эндпоинте вручную
@router.get("/data")
async def get_data(request: Request):
    logger.info(f"Request: {request.method} {request.url}")  # Копипаста
    response = ...
    response.headers["Access-Control-Allow-Origin"] = "*"    # Копипаста
    return response


# GOOD: Middleware — один раз для всех эндпоинтов
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Кастомный middleware для логирования запросов
import time
from starlette.middleware.base import BaseHTTPMiddleware

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

## 17. Lifespan for Startup/Shutdown

`lifespan` context manager, НЕ `on_event` (deprecated).

```python
# BAD: Deprecated on_event — удалён в новых версиях FastAPI
@app.on_event("startup")
async def startup():
    app.state.db = await create_engine()

@app.on_event("shutdown")
async def shutdown():
    await app.state.db.dispose()


# GOOD: lifespan — современный подход
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Жизненный цикл приложения: инициализация и очистка ресурсов."""
    # Startup: инициализация
    engine = create_async_engine(settings.database_url)
    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
    app.state.db_engine = engine
    app.state.session_factory = async_session_factory
    logger.info("app_started", database=settings.database_url)

    yield  # Приложение работает

    # Shutdown: очистка
    await engine.dispose()
    logger.info("app_stopped")

app = FastAPI(title="My Service", lifespan=lifespan)
```

## 18. BackgroundTasks

Лёгкие фоновые задачи после ответа клиенту.

```python
# BAD: Блокируем ответ клиента отправкой email
@router.post("/orders", response_model=OrderResponse)
async def create_order(body: OrderCreate) -> OrderResponse:
    order = await service.create(body)
    await send_confirmation_email(order)  # Клиент ждёт 3-5 секунд!
    return order


# GOOD: BackgroundTasks — клиент получает ответ сразу
from fastapi import BackgroundTasks

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: OrderCreate,
    background_tasks: BackgroundTasks,
    service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    """Создание заказа. Email-подтверждение отправляется в фоне."""
    order = await service.create(body)
    background_tasks.add_task(send_confirmation_email, order.id, order.customer_email)
    return order

async def send_confirmation_email(order_id: int, email: str) -> None:
    """Фоновая отправка email-подтверждения."""
    try:
        await email_service.send(to=email, template="order_confirmation", order_id=order_id)
    except Exception:
        logger.error("email_send_failed", order_id=order_id, email=email)
        # Не перебрасываем — фоновая задача не должна ломать основной flow
```

## 19. Path/Query/Body Parameter Validation

Декларативная валидация параметров — Field, Query, Path, Body.

```python
# BAD: Ручные проверки в теле функции
@router.get("/search")
async def search(q: str = None, page: int = 0):
    if not q or len(q) < 2:
        raise HTTPException(400, "query too short")
    if page < 0:
        raise HTTPException(400, "invalid page")


# GOOD: Валидация в сигнатуре — ошибки 422 автоматически
from fastapi import Query, Path

@router.get("/search", response_model=SearchResponse)
async def search(
    q: Annotated[str, Query(min_length=2, max_length=100, description="Поисковый запрос")],
    page: Annotated[int, Query(ge=1, le=1000, description="Номер страницы")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Размер страницы")] = 20,
    sort_by: Annotated[SortField, Query(description="Поле сортировки")] = SortField.CREATED_AT,
) -> SearchResponse:
    """Поиск с пагинацией и сортировкой."""
    return await service.search(q=q, page=page, page_size=page_size, sort_by=sort_by)

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: Annotated[int, Path(gt=0, description="ID пользователя")],
) -> UserResponse:
    """Получение пользователя по ID."""
    return await service.get_by_id(user_id)
```

## 20. Settings with pydantic-settings

Конфигурация через BaseSettings. Не через os.getenv() напрямую.

```python
# BAD: Разбросанные os.getenv по всему коду
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
SECRET_KEY = os.getenv("SECRET_KEY")  # None если забыли — баг в рантайме
DEBUG = os.getenv("DEBUG") == "true"  # Строковое сравнение


# GOOD: pydantic-settings — типизация, валидация, документация
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

class Settings(BaseSettings):
    """Конфигурация приложения. Читается из переменных окружения и .env файла."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Обязательные — приложение не запустится без них
    database_url: str = Field(..., description="URL подключения к БД")
    secret_key: SecretStr = Field(..., description="Секретный ключ для JWT")

    # С дефолтами и валидацией
    debug: bool = Field(default=False, description="Режим отладки")
    app_name: str = Field(default="My Service", description="Название сервиса")
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")

    # Вложенные настройки через prefix
    redis_url: str = Field(default="redis://localhost:6379/0")
    cors_origins: list[str] = Field(default=["http://localhost:3000"])

# Синглтон через functools.lru_cache
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    """Загрузка настроек (кешируется)."""
    return Settings()

# Использование в FastAPI через Depends
@router.get("/health")
async def health(settings: Annotated[Settings, Depends(get_settings)]) -> dict:
    return {"app": settings.app_name, "debug": settings.debug}
```

<!-- /section:fastapi -->

---

<!-- section:testing -->

## 21. Fixture Scopes

Правильный scope фикстуры = быстрые тесты.

```python
# BAD: Тяжёлая фикстура пересоздаётся на каждый тест
@pytest.fixture
def db_engine():
    """Создаёт движок БД — вызывается для КАЖДОГО теста."""
    engine = create_engine(TEST_DB_URL)  # 500ms каждый раз
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


# GOOD: Правильные scope'ы — тяжёлые ресурсы создаются один раз
@pytest.fixture(scope="session")
def db_engine():
    """Движок БД — один на всю сессию тестов."""
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Сессия БД — новая для каждого теста, с откатом."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()  # Откат — тесты изолированы
    connection.close()
```

**Справочник scope'ов:**
```python
# scope="session"   — один раз на весь запуск pytest (движок БД, Docker-контейнеры)
# scope="module"    — один раз на файл с тестами
# scope="class"     — один раз на тестовый класс
# scope="function"  — на каждый тест (по умолчанию) — для данных, сессий
```

## 22. conftest.py Organization

Один conftest.py на уровень. Не всё в корневом.

```python
# BAD: Один гигантский conftest.py на 500 строк
# tests/conftest.py — всё здесь: БД, фикстуры, фабрики, утилиты...


# GOOD: Иерархия conftest.py по ответственности

# tests/conftest.py — общие фикстуры (БД, настройки, клиент)
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.config import Settings

@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Настройки для тестового окружения."""
    return Settings(database_url="sqlite+aiosqlite:///test.db", debug=True)

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP-клиент для тестирования API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# tests/api/conftest.py — фикстуры для API-тестов
@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """Заголовки авторизации для защищённых эндпоинтов."""
    response = await client.post("/auth/login", json={"email": "test@test.com", "password": "secret"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# tests/services/conftest.py — фикстуры для unit-тестов сервисов
@pytest.fixture
def user_repo() -> Mock:
    """Мок репозитория пользователей."""
    return Mock(spec=UserRepository)
```

## 23. Parametrize for Data-Driven Tests

`@pytest.mark.parametrize` вместо копирования тестов.

```python
# BAD: Копипаста — 5 одинаковых тестов с разными данными
def test_validate_email_valid():
    assert validate_email("user@example.com") is True

def test_validate_email_invalid_no_at():
    assert validate_email("userexample.com") is False

def test_validate_email_invalid_empty():
    assert validate_email("") is False

# ... ещё 10 таких же


# GOOD: parametrize — данные отделены от логики
@pytest.mark.parametrize(
    ("email", "expected"),
    [
        ("user@example.com", True),
        ("admin@corp.io", True),
        ("a@b.co", True),
        ("userexample.com", False),  # нет @
        ("@example.com", False),     # нет имени
        ("user@", False),            # нет домена
        ("", False),                 # пустая строка
    ],
    ids=[
        "valid-standard",
        "valid-short-domain",
        "valid-minimal",
        "missing-at-sign",
        "missing-local-part",
        "missing-domain",
        "empty-string",
    ],
)
def test_validate_email(email: str, expected: bool) -> None:
    """Проверяет валидацию email для разных входных данных."""
    assert validate_email(email) is expected
```

**parametrize для API-тестов:**
```python
@pytest.mark.parametrize(
    ("payload", "expected_status", "expected_code"),
    [
        ({"name": "", "email": "a@b.com"}, 422, "VALIDATION_ERROR"),
        ({"name": "Ivan", "email": "not-email"}, 422, "VALIDATION_ERROR"),
        ({"name": "Ivan"}, 422, "VALIDATION_ERROR"),  # email обязателен
    ],
    ids=["empty-name", "invalid-email", "missing-email"],
)
async def test_create_user_validation(
    client: AsyncClient,
    payload: dict,
    expected_status: int,
    expected_code: str,
) -> None:
    response = await client.post("/users", json=payload)
    assert response.status_code == expected_status
```

## 24. httpx AsyncClient for FastAPI Testing

httpx AsyncClient, НЕ requests. TestClient — только для sync.

```python
# BAD: requests + внешний сервер
import requests

def test_get_user():
    resp = requests.get("http://localhost:8000/users/1")  # Нужен запущенный сервер!
    assert resp.status_code == 200


# GOOD: httpx AsyncClient — in-process, быстро, без сервера
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.anyio
async def test_get_user(client: AsyncClient) -> None:
    """Тест получения пользователя через API."""
    response = await client.get("/users/1")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 1
    assert "email" in data

@pytest.mark.anyio
async def test_create_user(client: AsyncClient) -> None:
    """Тест создания пользователя."""
    payload = {"name": "Ivan", "email": "ivan@test.com"}
    response = await client.post("/users", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Ivan"
    assert data["email"] == "ivan@test.com"
    assert "id" in data
```

## 25. Mock/Patch Patterns

Mock — только для внешних зависимостей. Не мокай свой код.

```python
# BAD: Мокаем всё подряд — тест ничего не проверяет
def test_create_order():
    mock_service = Mock()
    mock_service.create.return_value = Mock(id=1)
    mock_repo = Mock()
    mock_validator = Mock()

    result = mock_service.create(Mock())  # Тестируем мок мока!
    assert result.id == 1  # Бессмысленно


# GOOD: Мокаем только внешние зависимости (БД, HTTP, email)
from unittest.mock import AsyncMock, patch

@pytest.mark.anyio
async def test_create_order_sends_notification() -> None:
    """Проверяет что при создании заказа отправляется уведомление."""
    # Arrange: мокаем только внешний сервис email
    mock_repo = AsyncMock(spec=OrderRepository)
    mock_repo.save.return_value = Order(id=1, status=OrderStatus.PENDING)

    mock_email = AsyncMock(spec=EmailService)

    service = OrderService(repo=mock_repo, email=mock_email)

    # Act: реальная бизнес-логика
    order = await service.create(OrderCreate(customer_id=1, items=[...]))

    # Assert: проверяем поведение
    mock_repo.save.assert_called_once()
    mock_email.send.assert_called_once_with(
        to="customer@test.com",
        template="order_confirmation",
        order_id=1,
    )
```

**patch — для замены зависимости в модуле:**
```python
# GOOD: patch для замены внешнего вызова
@pytest.mark.anyio
async def test_fetch_exchange_rate() -> None:
    """Проверяет получение курса валюты (без реального HTTP)."""
    mock_response = {"rate": 92.5, "currency": "USD/RUB"}

    with patch("app.services.currency.httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = Mock(status_code=200, json=lambda: mock_response)

        rate = await currency_service.get_rate("USD", "RUB")
        assert rate == Decimal("92.5")
```

## 26. Factory Fixtures

Фабрики вместо фикстуры на каждую комбинацию данных.

```python
# BAD: Отдельная фикстура для каждого случая
@pytest.fixture
def active_user():
    return User(name="Ivan", status="active")

@pytest.fixture
def inactive_user():
    return User(name="Petr", status="inactive")

@pytest.fixture
def admin_user():
    return User(name="Admin", status="active", role="admin")

# 20 фикстур для 20 комбинаций...


# GOOD: Фабричная фикстура — гибкая, компактная
@pytest.fixture
def make_user():
    """Фабрика пользователей с дефолтами."""
    created_count = 0

    def _make_user(
        name: str = "Test User",
        email: str | None = None,
        status: str = "active",
        role: str = "user",
    ) -> User:
        nonlocal created_count
        created_count += 1
        return User(
            id=created_count,
            name=name,
            email=email or f"user{created_count}@test.com",
            status=status,
            role=role,
        )

    return _make_user


# Использование в тестах — чисто и гибко
def test_admin_can_delete_user(make_user) -> None:
    admin = make_user(role="admin")
    target = make_user(name="To Delete")
    assert admin.can_delete(target) is True

def test_regular_user_cannot_delete(make_user) -> None:
    user = make_user(role="user")
    target = make_user(name="Protected")
    assert user.can_delete(target) is False
```

## 27. Markers for Test Categorization

Маркеры для группировки и фильтрации тестов.

```python
# pyproject.toml — регистрация маркеров
# [tool.pytest.ini_options]
# markers = [
#     "slow: тесты выполняющиеся > 5 секунд",
#     "integration: интеграционные тесты (нужна БД)",
#     "e2e: end-to-end тесты",
# ]

# BAD: Все тесты в одной куче — CI выполняется 20 минут
def test_quick_validation(): ...
def test_database_migration(): ...  # 30 секунд
def test_full_workflow(): ...        # 2 минуты


# GOOD: Маркеры — запускай что нужно
import pytest

@pytest.mark.slow
@pytest.mark.integration
async def test_database_migration(db_engine) -> None:
    """Интеграционный тест миграции БД (медленный)."""
    await run_migrations(db_engine)
    assert await check_schema(db_engine) is True

@pytest.mark.e2e
async def test_full_order_workflow(client: AsyncClient) -> None:
    """E2E: создание заказа -> оплата -> доставка."""
    ...

# Без маркера — быстрый unit-тест
def test_calculate_tax() -> None:
    assert calculate_tax(Decimal("100")) == Decimal("20")
```

**Запуск по маркерам:**
```bash
# Только быстрые тесты (без slow)
pytest -m "not slow"

# Только интеграционные
pytest -m integration

# Всё кроме e2e
pytest -m "not e2e"
```

## 28. Assert Patterns

Конкретные assert'ы с понятными сообщениями.

```python
# BAD: Неинформативный assert — при падении непонятно что случилось
def test_create_order(service) -> None:
    result = service.create(order_data)
    assert result  # AssertionError — и что?
    assert result.status  # AssertionError — ???


# GOOD: Конкретные assert'ы с сообщениями
def test_create_order(service) -> None:
    result = service.create(order_data)

    assert result is not None, "create() вернул None"
    assert result.id > 0, f"Невалидный ID заказа: {result.id}"
    assert result.status == OrderStatus.PENDING, (
        f"Ожидался статус PENDING, получен {result.status}"
    )
    assert len(result.items) == 2, (
        f"Ожидалось 2 позиции, получено {len(result.items)}"
    )


# GOOD: pytest.raises для проверки исключений
def test_duplicate_email_raises(service) -> None:
    """Попытка создания пользователя с существующим email вызывает ConflictError."""
    service.create(UserCreate(email="test@test.com", name="First"))

    with pytest.raises(ConflictError, match="уже существует"):
        service.create(UserCreate(email="test@test.com", name="Second"))


# GOOD: pytest.approx для чисел с плавающей точкой
def test_calculate_discount() -> None:
    result = calculate_discount(price=99.99, percent=15)
    assert result == pytest.approx(84.99, abs=0.01)
```

## 29. Async Test Patterns

pytest-asyncio / anyio для асинхронных тестов.

```python
# pyproject.toml
# [tool.pytest.ini_options]
# asyncio_mode = "auto"  # Все async тесты запускаются автоматически

# BAD: Запуск async через asyncio.run — ломает event loop
def test_fetch_user():
    result = asyncio.run(service.get_user(1))  # Проблемы с event loop
    assert result.id == 1


# GOOD: pytest-asyncio — нативная поддержка async
import pytest

# С asyncio_mode = "auto" — маркер не нужен
async def test_fetch_user(db_session) -> None:
    """Тест получения пользователя из БД."""
    repo = UserRepository(db_session)
    await repo.save(User(id=1, name="Ivan", email="ivan@test.com"))

    user = await repo.find_by_id(1)
    assert user is not None
    assert user.name == "Ivan"

# Async фикстуры — работают так же
@pytest.fixture
async def populated_db(db_session) -> AsyncGenerator[AsyncSession, None]:
    """БД с тестовыми данными."""
    users = [
        User(id=i, name=f"User {i}", email=f"user{i}@test.com")
        for i in range(1, 6)
    ]
    db_session.add_all(users)
    await db_session.commit()
    yield db_session

async def test_list_users(populated_db) -> None:
    """Тест списка пользователей из заполненной БД."""
    repo = UserRepository(populated_db)
    users = await repo.list_all()
    assert len(users) == 5
```

**anyio вместо asyncio (рекомендуется для FastAPI):**
```python
# pyproject.toml
# [tool.pytest.ini_options]
# asyncio_mode = "auto"

# Или с явным маркером:
@pytest.mark.anyio
async def test_concurrent_requests(client: AsyncClient) -> None:
    """Тест параллельных запросов к API."""
    import anyio

    results: list[int] = []

    async def make_request(user_id: int) -> None:
        response = await client.get(f"/users/{user_id}")
        results.append(response.status_code)

    async with anyio.create_task_group() as tg:
        for uid in range(1, 6):
            tg.start_soon(make_request, uid)

    assert all(s == 200 for s in results)
```

## 30. Coverage Configuration

Осмысленные пороги покрытия. Исключение шаблонного кода.

```python
# pyproject.toml
# [tool.coverage.run]
# source = ["app"]
# omit = [
#     "app/migrations/*",
#     "app/config.py",
#     "*/conftest.py",
# ]
#
# [tool.coverage.report]
# fail_under = 80
# exclude_lines = [
#     "pragma: no cover",
#     "if TYPE_CHECKING:",
#     "if __name__ == .__main__.:",
#     "@abstractmethod",
#     "raise NotImplementedError",
# ]
# show_missing = true


# BAD: 100% покрытие — тестируем геттеры и конфиги
def test_settings_defaults():
    s = Settings()
    assert s.app_name == "My Service"  # Тестируем значение по умолчанию...


# GOOD: Тестируем бизнес-логику, не бойлерплейт
def test_order_total_with_discount() -> None:
    """Тест расчёта итога заказа со скидкой."""
    order = Order(
        items=[
            OrderItem(product_id=1, quantity=2, price=Decimal("100")),
            OrderItem(product_id=2, quantity=1, price=Decimal("50")),
        ],
        discount_percent=10,
    )
    # 250 - 10% = 225
    assert order.calculate_total() == Decimal("225.00")

def test_order_total_without_discount() -> None:
    """Тест расчёта итога без скидки."""
    order = Order(
        items=[OrderItem(product_id=1, quantity=1, price=Decimal("100"))],
        discount_percent=0,
    )
    assert order.calculate_total() == Decimal("100.00")
```

**Запуск с покрытием:**
```bash
# Запуск тестов с отчётом покрытия
pytest --cov=app --cov-report=term-missing --cov-fail-under=80

# HTML-отчёт для детального анализа
pytest --cov=app --cov-report=html
```

<!-- /section:testing -->

---

# Quick Checklist

Before submitting Python code:

**Core Python (rules 1-10):**
- [ ] Type hints на всех функциях, параметрах, переменных
- [ ] dataclass для внутренних данных (frozen=True для иммутабельных)
- [ ] Enum/StrEnum для констант — никаких магических строк
- [ ] async только для реального I/O, gather для параллельности
- [ ] Кастомные исключения с контекстом (entity, id, code)
- [ ] structlog/logging — никогда print()
- [ ] pathlib.Path — никогда os.path
- [ ] Comprehensions читаемые, максимум один уровень вложенности
- [ ] Context managers (with) для всех ресурсов
- [ ] Protocol/ABC для интерфейсов

**FastAPI + Pydantic (rules 11-20):**
- [ ] APIRouter по доменам, main.py только сборка
- [ ] Pydantic v2: field_validator, model_validator, computed_field
- [ ] Depends() для всех зависимостей, Annotated для переиспользования
- [ ] response_model и status_code на каждом эндпоинте
- [ ] Единый exception handler через @app.exception_handler
- [ ] Middleware для CORS, логирования, аутентификации
- [ ] lifespan для startup/shutdown (НЕ on_event!)
- [ ] BackgroundTasks для фоновых операций
- [ ] Query/Path/Body с валидацией в сигнатуре
- [ ] BaseSettings для конфигурации из env

**Testing (rules 21-30):**
- [ ] Правильные scope фикстур (session для тяжёлых ресурсов)
- [ ] conftest.py по уровням, не один гигантский файл
- [ ] parametrize для data-driven тестов с ids
- [ ] httpx AsyncClient для FastAPI тестов (не requests!)
- [ ] Mock только для внешних зависимостей (БД, HTTP, email)
- [ ] Factory fixtures вместо фикстуры на каждый случай
- [ ] Маркеры: slow, integration, e2e — для фильтрации
- [ ] Конкретные assert'ы с сообщениями
- [ ] pytest-asyncio/anyio для async тестов
- [ ] Coverage >= 80%, исключая бойлерплейт
