# Java Code Standards

<!-- section:basics -->

## 1. No-Nest Rule

Maximum ONE level of nesting inside a function. Extract nested logic to separate methods.

```java
// BAD: Multiple nesting levels
public void process(List<Order> orders) {
    for (Order order : orders) {
        if (order.isValid()) {
            for (Item item : order.getItems()) {
                if (item.getPrice() > 0) {
                    // deep nesting = hard to read
                }
            }
        }
    }
}

// GOOD: Flat, extracted methods
public void process(List<Order> orders) {
    orders.stream()
        .filter(Order::isValid)
        .forEach(this::processOrder);
}

private void processOrder(Order order) {
    order.getItems().stream()
        .filter(item -> item.getPrice() > 0)
        .forEach(this::processItem);
}
```

## 2. Atomic & Readable Code

Each method does ONE thing. Name describes WHAT it does.

```java
// BAD: Does multiple things
public void handleUser(User user) {
    // validates, saves, sends email, logs... 100 lines
}

// GOOD: Single responsibility
public void registerUser(User user) {
    validateUser(user);
    User saved = userRepository.save(user);
    notificationService.sendWelcomeEmail(saved);
}
```

## 3. Fail-Fast Validation

Check inputs FIRST. Use Spring Assert. No deep validation inside logic.

```java
// BAD: Validation mixed with logic
public Order createOrder(String userId, List<Item> items) {
    Order order = new Order();
    if (userId != null && !userId.isEmpty()) {
        order.setUserId(userId);
        if (items != null && !items.isEmpty()) {
            // deep nesting...
        }
    }
    return order;
}

// BAD: Ручные if/throw
public Order createOrder(String userId, List<Item> items) {
    if (userId == null || userId.isBlank()) {
        throw new IllegalArgumentException("userId cannot be blank");
    }
    if (items == null || items.isEmpty()) {
        throw new IllegalArgumentException("items cannot be empty");
    }
    return Order.builder().build();
}

// GOOD: Spring Assert — чисто и читаемо
import org.springframework.util.Assert;

public Order createOrder(final String userId, final List<Item> items) {
    Assert.hasText(userId, "userId cannot be blank");
    Assert.notEmpty(items, "items cannot be empty");

    return Order.builder()
        .userId(userId)
        .items(items)
        .build();
}
```

**Spring Assert методы:**
```java
Assert.notNull(obj, "obj cannot be null");           // != null
Assert.hasText(str, "str cannot be blank");          // not null, not empty, not whitespace
Assert.hasLength(str, "str cannot be empty");        // not null, not empty
Assert.notEmpty(collection, "list cannot be empty"); // not null, not empty
Assert.notEmpty(map, "map cannot be empty");         // not null, not empty
Assert.notEmpty(array, "array cannot be empty");     // not null, not empty
Assert.isTrue(condition, "condition must be true");  // boolean check
Assert.state(condition, "invalid state");            // IllegalStateException
```

## 4. No `var` - Explicit Types

Java is not Python. Types improve readability and IDE support.

```java
// BAD: var hides type
var result = service.process(data);
var items = getItems();

// GOOD: Explicit types
ProcessResult result = service.process(data);
List<OrderItem> items = getItems();
```

## 4.1. Always `final` — Immutable by Default

Если переменная не переопределяется — она ДОЛЖНА быть `final`. Включая параметры методов.

```java
// BAD: Непонятно, меняется ли переменная ниже по коду
public String processOrder(Order order, String userId) {
    Order saved = orderRepository.save(order);
    String notification = buildNotification(saved);
    notificationService.send(notification);
    return saved.getId();
    // А вдруг где-то ниже: order = modifyOrder(order); ???
}

// GOOD: final явно показывает — переменная не меняется
public String processOrder(final Order order, final String userId) {
    final Order saved = orderRepository.save(order);
    final String notification = buildNotification(saved);
    notificationService.send(notification);
    return saved.getId();
}

// GOOD: Lambda параметры — effectively final (компилятор проверит)
orders.stream()
    .filter(order -> order.isValid())  // order effectively final
    .map(order -> order.getId())
    .toList();
```

**Правило:** Всё `final` по умолчанию. Если кажется что нужен не-final — рефактори код.

```java
// BAD: Мутабельные переменные, break, обращение к глобальной константе
public void processWithRetry(final Request request) {
    Response response = null;  // ❌ Мутабельная
    int attempt = 0;           // ❌ Мутабельная

    while (attempt < MAX_RETRY_ATTEMPTS) {  // ❌ Обращение к внешней переменной
        attempt++;
        response = client.send(request);
        if (response.isSuccess()) {
            break;  // ❌ break — плохо читается
        }
    }
    handleResponse(response);
}

// GOOD: Метод просто возвращает результат, не обрабатывает
/** Выполняет запрос с повторами. */
public Optional<Response> executeWithRetry(final Request request, final int maxRetries) {
    for (int attempt = 1; attempt <= maxRetries; attempt++) {
        final Response response = client.send(request);
        if (response.isSuccess()) {
            return Optional.of(response);
        }
        log.warn("Попытка {} из {} не удалась", attempt, maxRetries);
    }
    return Optional.empty();
}

// Вызывающий код сам решает что делать с результатом:
final Optional<Response> response = service.executeWithRetry(request, 3);
if (response.isEmpty()) {
    throw new RetryExhaustedException("Не удалось выполнить запрос");
}
processResponse(response.get());
```

**Параметры методов — ВСЕГДА final:**
```java
// BAD: Параметр можно случайно переопределить
public void process(Order order) {
    order = enrichOrder(order);  // Опасно! Изменили входной параметр
    save(order);
}

// GOOD: Компилятор не даст переопределить
public void process(final Order order) {
    order = enrichOrder(order);  // ❌ Compilation error!

    final Order enrichedOrder = enrichOrder(order);  // ✅ Новая переменная
    save(enrichedOrder);
}
```

## 5. Lombok Annotations

Use Lombok to reduce boilerplate. More business logic, less noise.

```java
// BAD: Manual boilerplate
public class User {
    private String id;
    private String name;

    public User() {}
    public User(String id, String name) { ... }
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    // ... 50 more lines
}

// GOOD: Lombok
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class User {
    private String id;
    private String name;
}

// Common Lombok annotations:
@Data           // @Getter + @Setter + @ToString + @EqualsAndHashCode
@Builder        // Builder pattern
@Slf4j          // private static final Logger log = ...
@RequiredArgsConstructor // Constructor for final fields
@Value          // Immutable class (@Getter + final fields + @AllArgsConstructor)
```

## 6. Comments: Concise & Purposeful

No essays. State: WHY, WHERE used, WHAT for. **Javadoc можно на русском.**

**Комментарии обязательны для:**
- Классов
- Публичных методов
- **Всех полей класса** (включая private)

```java
// BAD: Портянка
/**
 * This method is responsible for processing the user data that comes
 * from the external API. It was created because we needed to handle
 * the transformation of data from the legacy format to the new format...
 */
public User processUser(UserDTO dto) { ... }

// BAD: Поля без комментариев
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;
    private final NotificationService notificationService;
    private final MeterRegistry meterRegistry;
}

// GOOD: Кратко и по делу (русский OK)
/** Преобразует UserDTO из внешнего API в доменную сущность User. */
public User processUser(UserDTO dto) { ... }

/**
 * Сервис обработки заказов.
 * Используется в OrderController для REST API.
 */
@Service
@RequiredArgsConstructor
public class OrderService {

    /** Репозиторий для работы с заказами в БД. */
    private final OrderRepository orderRepository;

    /** Сервис отправки уведомлений (email, push). */
    private final NotificationService notificationService;

    /** Метрики для мониторинга (Prometheus/Grafana). */
    private final MeterRegistry meterRegistry;

    /** Максимальное количество попыток обработки заказа. */
    private static final int MAX_RETRY_ATTEMPTS = 3;

    /** Задержка между попытками. */
    private static final Duration RETRY_DELAY = Duration.ofSeconds(5);
}
```

**Для Lombok @Data/@Value классов — тоже:**
```java
/** Данные пользователя для REST API. */
@Data
@Builder
public class UserDto {

    /** Уникальный идентификатор пользователя (UUID). */
    private String id;

    /** Email для авторизации и уведомлений. */
    private String email;

    /** Отображаемое имя в интерфейсе. */
    private String displayName;

    /** Роли пользователя для RBAC. */
    private List<String> roles;
}
```

### Spring Boot Auto-Configuration Comments

For `@ConfigurationProperties` classes, include YAML example with ALL properties:

```java
/**
 * GigaChat API configuration.
 *
 * Example application.yml:
 * ```yaml
 * gigachat:
 *   api:
 *     base-url: https://gigachat.devices.sberbank.ru/api/v1
 *     auth-url: https://ngw.devices.sberbank.ru:9443/api/v2/oauth
 *     scope: GIGACHAT_API_PERS
 *     model: GigaChat
 *     timeout: 30s
 *     max-retries: 3
 *   credentials:
 *     client-id: ${GIGACHAT_CLIENT_ID}
 *     client-secret: ${GIGACHAT_CLIENT_SECRET}
 * ```
 */
@Data
@ConfigurationProperties(prefix = "gigachat")
public class GigaChatProperties {
    private Api api = new Api();
    private Credentials credentials = new Credentials();

    @Data
    public static class Api {
        private String baseUrl = "https://gigachat.devices.sberbank.ru/api/v1";
        private String authUrl = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth";
        private String scope = "GIGACHAT_API_PERS";
        private String model = "GigaChat";
        private Duration timeout = Duration.ofSeconds(30);
        private int maxRetries = 3;
    }

    @Data
    public static class Credentials {
        private String clientId;
        private String clientSecret;
    }
}
```

## 7. No Global State

Static logger is OK. Mutable static state is NOT OK.

```java
// OK: Static logger (immutable)
@Slf4j
public class OrderService {
    // Lombok adds: private static final Logger log = LoggerFactory.getLogger(OrderService.class);
}

// BAD: Mutable global state
public class OrderService {
    private static AtomicInteger counter = new AtomicInteger(0);
    private static List<Order> cache = new ArrayList<>();  // Shared mutable state!

    public void process() {
        counter.incrementAndGet();  // Side effect!
        cache.add(order);           // Mutating global state!
    }
}

// GOOD: Instance state, injected dependencies
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;  // Injected
    private final MeterRegistry meterRegistry;      // For metrics

    public void process(Order order) {
        orderRepository.save(order);
        meterRegistry.counter("orders.processed").increment();
    }
}
```

## 8. Code Search with Serena

Before implementing, search existing code patterns using Serena MCP.

```
# If Serena is available, use it for semantic code search:
mcp__serena__search_symbols("OrderService")
mcp__serena__find_references("processOrder")
mcp__serena__get_hover_info("/path/to/File.java", line, column)

# If Serena is disabled:
1. Check MCP server status
2. Enable Serena in settings
3. Retry search

# Fallback to Grep if Serena unavailable:
Grep("class.*Service", type="java")
Grep("@RestController", type="java")
```

<!-- /section:basics -->

---

<!-- section:java17 -->

# Modern Java Features (17+)

## 9. Records — Immutable Data Classes

Используй records для DTO, value objects. Заменяет Lombok @Value.

```java
// GOOD: Record для DTO
/** Данные заказа для REST API. */
public record OrderDto(
    String id,
    String customerId,
    List<ItemDto> items,
    BigDecimal total
) {
    // Compact constructor для валидации (fail-fast!)
    public OrderDto {
        if (id == null || id.isBlank()) {
            throw new IllegalArgumentException("id cannot be blank");
        }
        if (items == null) {
            items = List.of();
        }
    }
}

// Использование:
OrderDto order = new OrderDto("123", "customer-1", items, total);
String id = order.id();  // Accessor без get-prefix
```

## 10. Pattern Matching для instanceof

Убирает явный cast после instanceof.

```java
// BAD: Старый стиль с cast
public String describe(Object obj) {
    if (obj instanceof String) {
        String str = (String) obj;  // Лишний cast
        return "String length: " + str.length();
    }
    return "Unknown";
}

// GOOD: Pattern matching (Java 16+)
public String describe(Object obj) {
    if (obj instanceof String str) {
        return "String length: " + str.length();
    }
    if (obj instanceof List<?> list) {
        return "List size: " + list.size();
    }
    return "Unknown: " + obj.getClass().getSimpleName();
}
```

## 11. Switch Expressions

Expression вместо statement. Возвращает значение.

```java
// BAD: Switch statement с break
public String getDayType(DayOfWeek day) {
    String result;
    switch (day) {
        case MONDAY:
        case TUESDAY:
        case WEDNESDAY:
        case THURSDAY:
        case FRIDAY:
            result = "Рабочий день";
            break;
        case SATURDAY:
        case SUNDAY:
            result = "Выходной";
            break;
        default:
            result = "Неизвестно";
    }
    return result;
}

// GOOD: Switch expression (Java 14+)
public String getDayType(DayOfWeek day) {
    return switch (day) {
        case MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY -> "Рабочий день";
        case SATURDAY, SUNDAY -> "Выходной";
    };  // Компилятор проверит exhaustiveness для enum!
}
```

## 12. Text Blocks

Для многострочных строк: SQL, JSON, YAML.

```java
// BAD: Конкатенация
String sql = "SELECT u.id, u.name " +
    "FROM users u " +
    "WHERE u.status = 'ACTIVE' " +
    "ORDER BY u.name";

// GOOD: Text block (Java 15+)
String sql = """
    SELECT u.id, u.name
    FROM users u
    WHERE u.status = 'ACTIVE'
    ORDER BY u.name
    """;

// JSON template
String json = """
    {
        "userId": "%s",
        "action": "%s",
        "timestamp": "%s"
    }
    """.formatted(userId, action, Instant.now());
```

<!-- /section:java17 -->

<!-- section:errors -->

## 13. Обработка ошибок в Spring Boot

**Sealed classes / Result pattern НЕ нужны.** Spring Boot обрабатывает исключения автоматически.

### Кастомные исключения с `@ResponseStatus`:

```java
/** Сущность не найдена → 404. */
@ResponseStatus(HttpStatus.NOT_FOUND)
public class NotFoundException extends RuntimeException {
    public NotFoundException(final String message) {
        super(message);
    }
}

/** Конфликт бизнес-логики → 409. */
@ResponseStatus(HttpStatus.CONFLICT)
public class ConflictException extends RuntimeException {
    public ConflictException(final String message) {
        super(message);
    }
}
```

### `@ControllerAdvice` для глобальной обработки:

```java
/** Глобальный обработчик исключений. */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    /** Assert.xxx() бросает IllegalArgumentException → 400. */
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleIllegalArgument(final IllegalArgumentException e) {
        log.warn("Ошибка валидации: {}", e.getMessage());
        return ResponseEntity.badRequest()
            .body(new ErrorResponse("VALIDATION_ERROR", e.getMessage()));
    }

    /** Bean Validation ошибки → 400. */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(final MethodArgumentNotValidException e) {
        final String message = e.getBindingResult().getFieldErrors().stream()
            .map(FieldError::getDefaultMessage)
            .collect(Collectors.joining(", "));
        return ResponseEntity.badRequest()
            .body(new ErrorResponse("VALIDATION_ERROR", message));
    }
}

/** Ответ с ошибкой. */
public record ErrorResponse(String code, String message) {}
```

### Сервис — просто бросает исключения:

```java
/** Находит заказ по ID. */
public Order findById(final String id) {
    Assert.hasText(id, "id cannot be blank");  // → 400 через @ControllerAdvice

    return orderRepository.findById(id)
        .orElseThrow(() -> new NotFoundException("Заказ не найден: " + id));  // → 404
}

/** Отменяет заказ. */
public Order cancel(final String id) {
    final Order order = findById(id);

    if (order.getStatus() == OrderStatus.SHIPPED) {
        throw new ConflictException("Нельзя отменить отправленный заказ");  // → 409
    }

    order.setStatus(OrderStatus.CANCELLED);
    return orderRepository.save(order);
}
```

### Контроллер — чистый, без try/catch:

```java
@PostMapping
public Order create(@Valid @RequestBody final OrderDto dto) {
    return orderService.createOrder(dto);  // @Valid → 400 если невалидно
}

@GetMapping("/{id}")
public Order getById(@PathVariable final String id) {
    return orderService.findById(id);  // NotFoundException → 404
}
```

<!-- /section:errors -->

<!-- section:java17 -->

## 14. Named Constants

Никаких magic numbers/strings.

```java
// BAD: Magic values
if (retryCount > 3) { ... }
Thread.sleep(5000);
if (status.equals("ACTIVE")) { ... }

// GOOD: Named constants
private static final int MAX_RETRY_ATTEMPTS = 3;
private static final Duration RETRY_DELAY = Duration.ofSeconds(5);

public static final String STATUS_ACTIVE = "ACTIVE";
public static final String STATUS_INACTIVE = "INACTIVE";

if (retryCount > MAX_RETRY_ATTEMPTS) { ... }
Thread.sleep(RETRY_DELAY.toMillis());
if (STATUS_ACTIVE.equals(status)) { ... }  // null-safe!
```

## 15. Try-with-resources

Автоматическое закрытие ресурсов. Всегда использовать для I/O.

```java
// BAD: Ручное закрытие
public List<String> readLines(Path path) {
    BufferedReader reader = null;
    try {
        reader = Files.newBufferedReader(path);
        return reader.lines().toList();
    } finally {
        if (reader != null) {
            reader.close();  // Может выбросить exception!
        }
    }
}

// GOOD: Try-with-resources
public List<String> readLines(Path path) throws IOException {
    try (BufferedReader reader = Files.newBufferedReader(path)) {
        return reader.lines().toList();
    }
}

// Несколько ресурсов
public void copyData(Path source, Path target) throws IOException {
    try (InputStream in = Files.newInputStream(source);
         OutputStream out = Files.newOutputStream(target)) {
        in.transferTo(out);
    }
}
```

<!-- /section:java17 -->

---

<!-- section:java21 -->

# Java 21+ Features (⚠️ Требует Java 21)

## 16. Pattern Matching в Switch ⚠️ Java 21

Полноценный pattern matching с exhaustiveness check.

```java
// Java 21: Pattern matching + record patterns
public String handleResult(Result<Order> result) {
    return switch (result) {
        case Success<Order>(Order order) -> "Заказ создан: " + order.id();
        case Failure<Order>(String msg, Throwable cause) -> {
            log.error("Ошибка: {}", msg, cause);
            yield "Ошибка: " + msg;
        }
    };  // Компилятор проверит ВСЕ cases!
}

// Guard clauses в switch
public String describeNumber(Object obj) {
    return switch (obj) {
        case Integer i when i > 0 -> "Положительное: " + i;
        case Integer i when i < 0 -> "Отрицательное: " + i;
        case Integer i -> "Ноль";
        case null -> "null";
        default -> "Не число";
    };
}
```

## 17. Virtual Threads ⚠️ Java 21

Легковесные потоки для I/O-bound задач.

```java
// Spring Boot 3.2+: application.yml
// spring.threads.virtual.enabled: true

// Программно
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();

List<CompletableFuture<Response>> futures = requests.stream()
    .map(request -> CompletableFuture.supplyAsync(
        () -> httpClient.send(request),
        executor
    ))
    .toList();

List<Response> responses = futures.stream()
    .map(CompletableFuture::join)
    .toList();
```

## 18. Sequenced Collections ⚠️ Java 21

Единый API для first/last элементов.

```java
// Java 21: Новые методы для всех коллекций
List<String> list = new ArrayList<>(List.of("a", "b", "c"));

String first = list.getFirst();      // "a"
String last = list.getLast();        // "c"
list.addFirst("start");              // ["start", "a", "b", "c"]
list.addLast("end");                 // ["start", "a", "b", "c", "end"]

List<String> reversed = list.reversed();  // View, не копия
```

<!-- /section:java21 -->

---

# Quick Checklist

Before submitting Java code:

**Обязательно (все версии):**
- [ ] No more than 1 nesting level per method
- [ ] Each method does ONE thing
- [ ] Fail-fast: Spring Assert на входе метода
- [ ] No `var` - explicit types everywhere
- [ ] `final` everywhere - переменные и параметры методов
- [ ] Lombok annotations for boilerplate
- [ ] Comments: классы, методы, ВСЕ поля (русский OK)
- [ ] No mutable static state
- [ ] Named constants, no magic values
- [ ] Try-with-resources for I/O
- [ ] Searched existing patterns with Serena/Grep

**Java 17+:**
- [ ] Records for DTOs и value objects
- [ ] Pattern matching для instanceof
- [ ] Switch expressions (без pattern matching)
- [ ] Text blocks для SQL/JSON
- [ ] Spring Boot error handling: @ResponseStatus + @ControllerAdvice

**Java 21+ (если JAVA_VERSION >= 21):**
- [ ] Pattern matching в switch
- [ ] Virtual threads для I/O-bound
- [ ] Sequenced collections API

**Testing:** см. `.claude/refs/java-testing.md`
