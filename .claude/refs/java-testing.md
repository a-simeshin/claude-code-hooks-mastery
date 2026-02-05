# Java Testing Standards

<!-- section:philosophy -->

## Философия тестирования

```
┌─────────────────────────────────────────────────────────────────┐
│           РЕАЛЬНЫЕ ИНТЕГРАЦИОННЫЕ ТЕСТЫ                        │
│         (HTTP, Kafka, JDBC с Testcontainers)                    │
│                                                                 │
│    → Основная корзина базовых сценариев                        │
│    → Максимальная стабильность в агентной разработке           │
│    → Ловят РЕАЛЬНЫЕ баги                                       │
└─────────────────────────────────────────────────────────────────┘
                            +
┌─────────────────────────────────────────────────────────────────┐
│              UNIT ТЕСТЫ С МОКАМИ                                │
│            (Mockito, edge cases)                                │
│                                                                 │
│    → Добить coverage до 80/80 JaCoCo                           │
│    → Edge cases, которые сложно воспроизвести                  │
│    → Быстрый feedback loop                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Правила написания интеграционных тестов

### 1. Исследуй реальное использование API

Для **medium/hard** функциональности — **пойми как API будут использовать**:

```
Типичный код (CRUD, REST)?
  → Используй стандартные тестовые корзины (см. ниже)

Нетипичный код (интеграции, сложная логика)?
  → Context7: найди документацию библиотеки и примеры тестов
  → Пойми реальные сценарии использования
```

**Пример: интеграция с Kafka**
```bash
# Нетипичный код → ищем как правильно тестировать в Context7
mcp__context7__resolve-library-id(libraryName="spring-kafka", query="testing")
mcp__context7__query-docs(libraryId="...", query="integration test consumer producer")
```

**Цель:** Создать оптимальные тестовые сценарии, которые отражают реальное использование, а не просто покрывают код.

### 2. Приоритет сценариев

```
┌─────────────────────────────────────────────────────────────────┐
│  1. ПОЗИТИВНЫЕ СЦЕНАРИИ (сначала!)                             │
│     → Happy path: валидный запрос → успешный ответ              │
│     → Основной бизнес-флоу работает                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. КРИТИЧЕСКИЕ НЕГАТИВНЫЕ                                      │
│     → 404: ресурс не найден                                     │
│     → 400: невалидные данные (пустой ID, null)                 │
│     → 409: конфликт бизнес-логики                              │
│     → 401/403: unauthorized/forbidden (если есть auth)         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. EDGE CASES (unit тесты с моками)                           │
│     → Граничные значения                                        │
│     → Concurrent updates                                        │
│     → Retry логика                                              │
└─────────────────────────────────────────────────────────────────┘
```

### 3. НЕ пиши в интеграционных тестах

```java
// ❌ НЕ пиши бенчмарки производительности
@Test
void createOrder_performanceTest() {
    long start = System.currentTimeMillis();
    for (int i = 0; i < 1000; i++) {
        orderService.createOrder(request);
    }
    long duration = System.currentTimeMillis() - start;
    assertThat(duration).isLessThan(5000);  // ❌ Flaky!
}

// ❌ НЕ тестируй throughput
@Test
void api_shouldHandle100RequestsPerSecond() { ... }  // ❌ Для JMeter/Gatling

// ✅ Тестируй функциональность, не скорость
@Test
void createOrder_withValidRequest_returns201() {
    // given
    final CreateOrderRequest request = createValidRequest();

    // when
    final ResponseEntity<Order> response = restTemplate.postForEntity(
        "/api/orders", request, Order.class);

    // then
    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
}
```

<!-- /section:philosophy -->

---

<!-- section:structure -->

# Part 1: Базовые паттерны

## 1. Naming Convention

```java
// Формат: method_condition_expectedResult
@Test
void createOrder_withValidItems_returnsOrderWithCorrectTotal() { ... }

@Test
void createOrder_withEmptyItems_throwsIllegalArgumentException() { ... }

@Test
void findById_whenOrderNotFound_throwsNotFoundException() { ... }
```

## 2. Given-When-Then Structure

Комментарии `// given`, `// when`, `// then` **обязательны**.

```java
@Test
void createOrder_withValidItems_calculatesCorrectTotal() {
    // given
    final CreateOrderRequest request = createValidRequest();

    // when
    final Order result = orderService.createOrder(request);

    // then
    assertThat(result.getTotal()).isEqualByComparingTo(BigDecimal.valueOf(300));
}
```

## 3. AssertJ — Fluent Assertions

```java
// Коллекции
assertThat(orders)
    .hasSize(2)
    .extracting(Order::getStatus)
    .containsExactly(OrderStatus.CREATED, OrderStatus.SHIPPED);

// Исключения
assertThatThrownBy(() -> service.findById(null))
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessageContaining("id cannot be blank");

// Объекты
assertThat(result)
    .isNotNull()
    .satisfies(order -> {
        assertThat(order.getId()).isNotBlank();
        assertThat(order.getTotal()).isPositive();
    });
```

## 4. Allure Annotations

```java
@Epic("Заказы")
@Feature("Создание заказа")
class OrderServiceIntegrationTest {

    @Test
    @Story("Успешное создание")
    @Description("Проверяет создание заказа с валидными данными и расчёт итоговой суммы")
    @Severity(SeverityLevel.CRITICAL)
    void createOrder_withValidItems_success() {
        // ...
    }

    @Test
    @Story("Валидация")
    @Description("Проверяет отклонение заказа без товаров")
    @Severity(SeverityLevel.NORMAL)
    void createOrder_withEmptyItems_throwsException() {
        // ...
    }
}
```

### Allure @Step для читаемых отчётов

```java
@Test
@Story("Полный цикл заказа")
void orderLifecycle_fromCreationToDelivery() {
    // given
    final String orderId = createOrder();

    // when
    payForOrder(orderId);
    shipOrder(orderId);
    deliverOrder(orderId);

    // then
    assertOrderStatus(orderId, OrderStatus.DELIVERED);
}

@Step("Создаём заказ")
private String createOrder() {
    final CreateOrderRequest request = createValidRequest();
    final Order order = orderService.createOrder(request);
    return order.getId();
}

@Step("Оплачиваем заказ {orderId}")
private void payForOrder(final String orderId) {
    paymentService.processPayment(orderId);
}

@Step("Отправляем заказ {orderId}")
private void shipOrder(final String orderId) {
    shippingService.ship(orderId);
}

@Step("Доставляем заказ {orderId}")
private void deliverOrder(final String orderId) {
    deliveryService.deliver(orderId);
}

@Step("Проверяем статус заказа {orderId} = {expectedStatus}")
private void assertOrderStatus(final String orderId, final OrderStatus expectedStatus) {
    final Order order = orderService.findById(orderId);
    assertThat(order.getStatus()).isEqualTo(expectedStatus);
}
```

## 5. Nested Test Classes

Группировка тестов по сценариям. Улучшает читаемость в Allure.

```java
@Epic("Заказы")
@Feature("OrderService")
class OrderServiceIntegrationTest extends BaseIntegrationTest {

    @Nested
    @DisplayName("createOrder()")
    class CreateOrder {

        @Test
        @Story("Успешное создание")
        void withValidItems_returnsOrderWithCorrectTotal() {
            // given
            final CreateOrderRequest request = createValidRequest();

            // when
            final Order result = orderService.createOrder(request);

            // then
            assertThat(result.getId()).isNotBlank();
            assertThat(result.getTotal()).isEqualByComparingTo(BigDecimal.valueOf(300));
        }

        @Test
        @Story("Валидация")
        void withEmptyItems_throwsIllegalArgumentException() {
            // given
            final CreateOrderRequest request = CreateOrderRequest.builder()
                .customerId("customer-1")
                .items(List.of())
                .build();

            // when & then
            assertThatThrownBy(() -> orderService.createOrder(request))
                .isInstanceOf(IllegalArgumentException.class);
        }

        @Test
        @Story("Валидация")
        void withNullCustomerId_throwsIllegalArgumentException() {
            // given
            final CreateOrderRequest request = CreateOrderRequest.builder()
                .customerId(null)
                .items(List.of(createValidItem()))
                .build();

            // when & then
            assertThatThrownBy(() -> orderService.createOrder(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("customerId");
        }
    }

    @Nested
    @DisplayName("findById()")
    class FindById {

        @Test
        @Story("Успешный поиск")
        void whenExists_returnsOrder() {
            // given
            final Order created = orderService.createOrder(createValidRequest());

            // when
            final Order found = orderService.findById(created.getId());

            // then
            assertThat(found.getId()).isEqualTo(created.getId());
        }

        @Test
        @Story("Обработка ошибок")
        void whenNotFound_throwsNotFoundException() {
            // when & then
            assertThatThrownBy(() -> orderService.findById("non-existent"))
                .isInstanceOf(NotFoundException.class);
        }
    }

    @Nested
    @DisplayName("cancel()")
    class Cancel {

        @Test
        @Story("Успешная отмена")
        void whenCreated_cancelsSuccessfully() {
            // given
            final Order order = orderService.createOrder(createValidRequest());

            // when
            final Order cancelled = orderService.cancel(order.getId());

            // then
            assertThat(cancelled.getStatus()).isEqualTo(OrderStatus.CANCELLED);
        }

        @Test
        @Story("Бизнес-правила")
        void whenShipped_throwsConflictException() {
            // given
            final Order order = createShippedOrder();

            // when & then
            assertThatThrownBy(() -> orderService.cancel(order.getId()))
                .isInstanceOf(ConflictException.class)
                .hasMessageContaining("отправленный");
        }
    }
}
```

<!-- /section:structure -->

---

<!-- section:integration -->

# Part 2: Реальные интеграционные тесты

## 6. Podman + Testcontainers

**Используй Podman вместо Docker.** Настройка для разных ОС:

### Linux

```bash
# ~/.bashrc или ~/.zshrc
export DOCKER_HOST=unix://${XDG_RUNTIME_DIR}/podman/podman.sock
```

### MacOS

```bash
# ~/.bashrc или ~/.zshrc
export DOCKER_HOST=unix://$(podman machine inspect --format '{{.ConnectionInfo.PodmanSocket.Path}}')
export TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock
```

### Rootless режим (отключить Ryuk)

```bash
# Ryuk не работает в rootless режиме
export TESTCONTAINERS_RYUK_DISABLED=true
```

### Проверка

```bash
# Podman запущен?
podman info

# Testcontainers видит Podman?
mvn test -Dtest=SomeIT -X | grep -i "docker\|podman"
```

## 7. Base Integration Test Class (Testcontainers)

```java
/**
 * Базовый класс для интеграционных тестов.
 * Поднимает реальные PostgreSQL и Kafka через Testcontainers.
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@ActiveProfiles("test")
public abstract class BaseIntegrationTest {

    /** PostgreSQL контейнер — один на все тесты. */
    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    /** Kafka контейнер — один на все тесты. */
    @Container
    @ServiceConnection
    static KafkaContainer kafka = new KafkaContainer(
        DockerImageName.parse("confluentinc/cp-kafka:7.5.0")
    );

    /** HTTP клиент для тестирования REST API. */
    @Autowired
    protected TestRestTemplate restTemplate;

    /** Kafka consumer для проверки отправленных сообщений. */
    @Autowired
    protected KafkaTemplate<String, String> kafkaTemplate;

    /** Репозиторий для подготовки тестовых данных. */
    @Autowired
    protected OrderRepository orderRepository;

    @BeforeEach
    void cleanUp() {
        orderRepository.deleteAll();
    }
}
```

### application-test.yml

```yaml
spring:
  # Testcontainers настроит автоматически через @ServiceConnection
  datasource:
    # Будет переопределено Testcontainers
  kafka:
    # Будет переопределено Testcontainers

  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true

logging:
  level:
    org.springframework.test: DEBUG
    org.testcontainers: INFO
```

<!-- /section:integration -->

<!-- section:http -->

## 8. HTTP Integration Tests

```java
@Epic("REST API")
@Feature("Orders API")
class OrderControllerIntegrationTest extends BaseIntegrationTest {

    @Nested
    @DisplayName("POST /api/orders")
    class CreateOrderEndpoint {

        @Test
        @Story("Успешное создание")
        @Severity(SeverityLevel.CRITICAL)
        void withValidRequest_returns201AndOrder() {
            // given
            final CreateOrderRequest request = CreateOrderRequest.builder()
                .customerId("customer-1")
                .items(List.of(
                    new ItemDto("product-1", BigDecimal.valueOf(100)),
                    new ItemDto("product-2", BigDecimal.valueOf(200))
                ))
                .build();

            // when
            final ResponseEntity<Order> response = restTemplate.postForEntity(
                "/api/orders",
                request,
                Order.class
            );

            // then
            assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
            assertThat(response.getBody()).isNotNull();
            assertThat(response.getBody().getId()).isNotBlank();
            assertThat(response.getBody().getTotal()).isEqualByComparingTo(BigDecimal.valueOf(300));

            // verify persisted in DB
            final Optional<Order> fromDb = orderRepository.findById(response.getBody().getId());
            assertThat(fromDb).isPresent();
        }

        @Test
        @Story("Валидация")
        void withEmptyItems_returns400() {
            // given
            final CreateOrderRequest request = CreateOrderRequest.builder()
                .customerId("customer-1")
                .items(List.of())
                .build();

            // when
            final ResponseEntity<ErrorResponse> response = restTemplate.postForEntity(
                "/api/orders",
                request,
                ErrorResponse.class
            );

            // then
            assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
            assertThat(response.getBody().code()).isEqualTo("VALIDATION_ERROR");
        }
    }

    @Nested
    @DisplayName("GET /api/orders/{id}")
    class GetOrderEndpoint {

        @Test
        @Story("Успешный запрос")
        void whenExists_returns200AndOrder() {
            // given
            final Order saved = orderRepository.save(createTestOrder());

            // when
            final ResponseEntity<Order> response = restTemplate.getForEntity(
                "/api/orders/{id}",
                Order.class,
                saved.getId()
            );

            // then
            assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
            assertThat(response.getBody().getId()).isEqualTo(saved.getId());
        }

        @Test
        @Story("Обработка ошибок")
        void whenNotFound_returns404() {
            // when
            final ResponseEntity<ErrorResponse> response = restTemplate.getForEntity(
                "/api/orders/{id}",
                ErrorResponse.class,
                "non-existent-id"
            );

            // then
            assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
        }
    }
}
```

<!-- /section:http -->

<!-- section:kafka -->

## 9. Kafka Integration Tests

```java
@Epic("Messaging")
@Feature("Order Events")
class OrderKafkaIntegrationTest extends BaseIntegrationTest {

    /** Topic для событий заказов. */
    private static final String ORDERS_TOPIC = "orders.events";

    /** Consumer для чтения сообщений из Kafka. */
    @Autowired
    private KafkaConsumer<String, OrderEvent> kafkaConsumer;

    @BeforeEach
    void subscribeToTopic() {
        kafkaConsumer.subscribe(List.of(ORDERS_TOPIC));
    }

    @Test
    @Story("Отправка событий")
    @Severity(SeverityLevel.CRITICAL)
    void createOrder_publishesOrderCreatedEvent() {
        // given
        final CreateOrderRequest request = createValidRequest();

        // when
        restTemplate.postForEntity("/api/orders", request, Order.class);

        // then — проверяем что событие ушло в Kafka
        await().atMost(Duration.ofSeconds(10)).untilAsserted(() -> {
            final ConsumerRecords<String, OrderEvent> records =
                kafkaConsumer.poll(Duration.ofMillis(100));

            assertThat(records).isNotEmpty();

            final OrderEvent event = records.iterator().next().value();
            assertThat(event.getType()).isEqualTo("ORDER_CREATED");
            assertThat(event.getOrderId()).isNotBlank();
        });
    }

    @Test
    @Story("Обработка входящих событий")
    void paymentCompletedEvent_updatesOrderStatus() {
        // given
        final Order order = orderRepository.save(createTestOrder());
        final PaymentCompletedEvent event = new PaymentCompletedEvent(order.getId());

        // when — отправляем событие в Kafka
        kafkaTemplate.send("payments.events", event.getOrderId(), toJson(event));

        // then — проверяем что заказ обновился в БД
        await().atMost(Duration.ofSeconds(10)).untilAsserted(() -> {
            final Order updated = orderRepository.findById(order.getId()).orElseThrow();
            assertThat(updated.getStatus()).isEqualTo(OrderStatus.PAID);
        });
    }
}
```

<!-- /section:kafka -->

<!-- section:jdbc -->

## 10. JDBC Integration Tests

```java
@Epic("Persistence")
@Feature("OrderRepository")
class OrderRepositoryIntegrationTest extends BaseIntegrationTest {

    @Nested
    @DisplayName("Custom queries")
    class CustomQueries {

        @Test
        @Story("Поиск по статусу")
        void findByStatus_returnsMatchingOrders() {
            // given
            orderRepository.saveAll(List.of(
                createOrderWithStatus(OrderStatus.CREATED),
                createOrderWithStatus(OrderStatus.CREATED),
                createOrderWithStatus(OrderStatus.SHIPPED)
            ));

            // when
            final List<Order> created = orderRepository.findByStatus(OrderStatus.CREATED);

            // then
            assertThat(created).hasSize(2);
            assertThat(created).allMatch(o -> o.getStatus() == OrderStatus.CREATED);
        }

        @Test
        @Story("Поиск по клиенту")
        void findByCustomerId_returnsCustomerOrders() {
            // given
            orderRepository.saveAll(List.of(
                createOrderForCustomer("customer-1"),
                createOrderForCustomer("customer-1"),
                createOrderForCustomer("customer-2")
            ));

            // when
            final List<Order> orders = orderRepository.findByCustomerId("customer-1");

            // then
            assertThat(orders).hasSize(2);
        }

        @Test
        @Story("Агрегация")
        void calculateTotalByCustomer_returnsCorrectSum() {
            // given
            orderRepository.saveAll(List.of(
                createOrderWithTotal("customer-1", BigDecimal.valueOf(100)),
                createOrderWithTotal("customer-1", BigDecimal.valueOf(200)),
                createOrderWithTotal("customer-2", BigDecimal.valueOf(500))
            ));

            // when
            final BigDecimal total = orderRepository.calculateTotalByCustomer("customer-1");

            // then
            assertThat(total).isEqualByComparingTo(BigDecimal.valueOf(300));
        }
    }

    @Nested
    @DisplayName("Transactions")
    class Transactions {

        @Test
        @Story("Rollback при ошибке")
        void whenExceptionThrown_rollbacksTransaction() {
            // given
            final int initialCount = (int) orderRepository.count();

            // when & then
            assertThatThrownBy(() -> orderService.createOrderWithFailingStep(createValidRequest()))
                .isInstanceOf(RuntimeException.class);

            // verify rollback
            assertThat(orderRepository.count()).isEqualTo(initialCount);
        }
    }
}
```

<!-- /section:jdbc -->

<!-- section:wiremock -->

## 11. External API Tests (WireMock)

```java
@Epic("External Integrations")
@Feature("Payment Gateway")
@WireMockTest(httpPort = 8089)
class PaymentGatewayIntegrationTest extends BaseIntegrationTest {

    @Test
    @Story("Успешная оплата")
    void processPayment_whenGatewayReturnsSuccess_updatesOrder() {
        // given
        final Order order = orderRepository.save(createTestOrder());

        stubFor(post(urlEqualTo("/api/payments"))
            .willReturn(aResponse()
                .withStatus(200)
                .withHeader("Content-Type", "application/json")
                .withBody("""
                    {
                        "transactionId": "txn-123",
                        "status": "SUCCESS"
                    }
                    """)));

        // when
        final ResponseEntity<Order> response = restTemplate.postForEntity(
            "/api/orders/{id}/pay",
            null,
            Order.class,
            order.getId()
        );

        // then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody().getStatus()).isEqualTo(OrderStatus.PAID);

        verify(postRequestedFor(urlEqualTo("/api/payments"))
            .withRequestBody(containing(order.getId())));
    }

    @Test
    @Story("Ошибка шлюза")
    void processPayment_whenGatewayFails_returns502() {
        // given
        final Order order = orderRepository.save(createTestOrder());

        stubFor(post(urlEqualTo("/api/payments"))
            .willReturn(aResponse()
                .withStatus(500)
                .withBody("Internal Server Error")));

        // when
        final ResponseEntity<ErrorResponse> response = restTemplate.postForEntity(
            "/api/orders/{id}/pay",
            null,
            ErrorResponse.class,
            order.getId()
        );

        // then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_GATEWAY);
    }

    @Test
    @Story("Таймаут")
    void processPayment_whenGatewayTimeout_returns504() {
        // given
        final Order order = orderRepository.save(createTestOrder());

        stubFor(post(urlEqualTo("/api/payments"))
            .willReturn(aResponse()
                .withFixedDelay(5000)  // Timeout
                .withStatus(200)));

        // when
        final ResponseEntity<ErrorResponse> response = restTemplate.postForEntity(
            "/api/orders/{id}/pay",
            null,
            ErrorResponse.class,
            order.getId()
        );

        // then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.GATEWAY_TIMEOUT);
    }
}
```

<!-- /section:wiremock -->

---

<!-- section:mockito -->

# Part 3: Unit тесты с Mocks (для Coverage)

## 12. Mockito для Edge Cases

```java
/**
 * Unit тесты для добития coverage.
 * Edge cases, которые сложно воспроизвести в интеграционных тестах.
 */
@Epic("Unit Tests")
@Feature("OrderService")
@ExtendWith(MockitoExtension.class)
class OrderServiceUnitTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private PaymentGateway paymentGateway;

    @Mock
    private NotificationService notificationService;

    @InjectMocks
    private OrderService orderService;

    @Nested
    @DisplayName("Edge cases")
    class EdgeCases {

        @Test
        @Story("Concurrent modification")
        void cancel_whenConcurrentUpdate_retriesAndSucceeds() {
            // given
            final Order order = createTestOrder();
            when(orderRepository.findById(order.getId()))
                .thenReturn(Optional.of(order));
            when(orderRepository.save(any()))
                .thenThrow(new OptimisticLockingFailureException("Concurrent update"))
                .thenReturn(order.withStatus(OrderStatus.CANCELLED));

            // when
            final Order result = orderService.cancel(order.getId());

            // then
            assertThat(result.getStatus()).isEqualTo(OrderStatus.CANCELLED);
            verify(orderRepository, times(2)).save(any());
        }

        @Test
        @Story("Notification failure")
        void createOrder_whenNotificationFails_stillSavesOrder() {
            // given
            final CreateOrderRequest request = createValidRequest();
            final Order savedOrder = createTestOrder();

            when(orderRepository.save(any())).thenReturn(savedOrder);
            doThrow(new RuntimeException("Email service down"))
                .when(notificationService).sendOrderCreatedNotification(any());

            // when
            final Order result = orderService.createOrder(request);

            // then — заказ сохранён несмотря на ошибку уведомления
            assertThat(result).isNotNull();
            verify(orderRepository).save(any());
        }

        @Test
        @Story("Partial payment")
        void processPayment_whenPartiallyPaid_updatesRemainingAmount() {
            // given
            final Order order = createOrderWithTotal(BigDecimal.valueOf(1000));
            when(orderRepository.findById(order.getId())).thenReturn(Optional.of(order));
            when(paymentGateway.charge(any())).thenReturn(
                new PaymentResult(BigDecimal.valueOf(500), PaymentStatus.PARTIAL)
            );

            // when
            orderService.processPayment(order.getId());

            // then
            verify(orderRepository).save(argThat(o ->
                o.getRemainingAmount().equals(BigDecimal.valueOf(500))
            ));
        }
    }

    @Nested
    @DisplayName("Validation branches")
    class ValidationBranches {

        @Test
        void createOrder_withNullRequest_throwsException() {
            assertThatThrownBy(() -> orderService.createOrder(null))
                .isInstanceOf(IllegalArgumentException.class);
        }

        @Test
        void createOrder_withNegativePrice_throwsException() {
            // given
            final CreateOrderRequest request = CreateOrderRequest.builder()
                .customerId("customer-1")
                .items(List.of(new ItemDto("item-1", BigDecimal.valueOf(-100))))
                .build();

            // when & then
            assertThatThrownBy(() -> orderService.createOrder(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("price");
        }
    }
}
```

<!-- /section:mockito -->

---

<!-- section:e2e -->

# Part 4: UI/E2E Testing (Selenide + Testcontainers)

## 13. Base E2E Test Class

Для проектов с frontend — E2E тесты через **Selenide** и **BrowserWebDriverContainer**.

```java
/**
 * Базовый класс для E2E тестов.
 * Поднимает headless браузер в Docker/Podman контейнере.
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@ActiveProfiles("test")
public abstract class BaseE2ETest {

    /** Порт приложения — Spring Boot назначает при запуске. */
    @LocalServerPort
    protected int port;

    /**
     * Браузер в контейнере.
     * seleniarm — для ARM64 (Apple M1/M2/M3).
     * VNC доступен на порту 5900 для отладки.
     */
    @Container
    static BrowserWebDriverContainer<?> browser = new BrowserWebDriverContainer<>(
            DockerImageName.parse("seleniarm/standalone-chromium:latest")
                .asCompatibleSubstituteFor("selenium/standalone-chrome"))
        .withCapabilities(chromeOptions());

    /** Chrome опции для headless режима. */
    private static ChromeOptions chromeOptions() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments(
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1920,1080"
        );
        return options;
    }

    @BeforeAll
    static void setupSelenide() {
        // Подключаем Selenide к браузеру в контейнере
        Configuration.remote = browser.getSeleniumAddress().toString();

        // Allure интеграция для скриншотов
        SelenideLogger.addListener("AllureSelenide",
            new AllureSelenide()
                .screenshots(true)
                .savePageSource(true)
        );
    }

    @BeforeEach
    void setupBaseUrl() {
        // host.containers.internal — для Podman (localhost не работает из контейнера)
        Configuration.baseUrl = "http://host.containers.internal:" + port;

        // Таймауты
        Configuration.timeout = 10_000;
        Configuration.pageLoadTimeout = 30_000;
    }

    @AfterAll
    static void tearDown() {
        SelenideLogger.removeListener("AllureSelenide");
    }
}
```

### Важные моменты

| Аспект | Решение |
|--------|---------|
| **ARM64 Mac** | `seleniarm/standalone-chromium` вместо `selenium/standalone-chrome` |
| **Podman** | `host.containers.internal` вместо `localhost` |
| **Headless** | `--no-sandbox`, `--disable-gpu`, `--disable-dev-shm-usage` |
| **Allure** | `AllureSelenide` для скриншотов и page source |

## 14. E2E Test Example

```java
@Epic("UI")
@Feature("Каталог")
class CatalogPageIT extends BaseE2ETest {

    @Nested
    @DisplayName("Каталог товаров")
    class CatalogTests {

        @Test
        @Story("Загрузка каталога")
        @Severity(SeverityLevel.CRITICAL)
        void catalogPage_loadsSuccessfully() {
            // when
            open("/catalog");

            // then
            $("h1").shouldHave(text("Каталог"));
            $$(".product-card").shouldHave(sizeGreaterThan(0));
        }

        @Test
        @Story("Поиск товара")
        void searchProduct_findsMatchingItems() {
            // given
            open("/catalog");

            // when
            $("[data-testid='search-input']").setValue("Java");
            $("[data-testid='search-button']").click();

            // then
            $$(".product-card").shouldHave(sizeGreaterThan(0));
            $$(".product-card").first()
                .shouldHave(text("Java"));
        }

        @Test
        @Story("Фильтрация")
        void filterByCategory_showsOnlyMatchingProducts() {
            // given
            open("/catalog");

            // when
            $("[data-testid='category-filter']").click();
            $("[data-value='programming']").click();

            // then
            $$(".product-card").forEach(card ->
                card.$(".category").shouldHave(text("Programming"))
            );
        }
    }

    @Nested
    @DisplayName("Карточка товара")
    class ProductCardTests {

        @Test
        @Story("Переход к товару")
        void clickOnProduct_opensProductPage() {
            // given
            open("/catalog");
            String productName = $$(".product-card").first()
                .$(".product-name").getText();

            // when
            $$(".product-card").first().click();

            // then
            $("h1").shouldHave(text(productName));
            $(".product-details").shouldBe(visible);
        }

        @Test
        @Story("Добавление в корзину")
        void addToCart_updatesCartBadge() {
            // given
            open("/catalog");

            // when
            $$(".product-card").first()
                .$("[data-testid='add-to-cart']").click();

            // then
            $("[data-testid='cart-badge']").shouldHave(text("1"));
        }
    }
}
```

## 15. E2E с авторизацией

```java
@Epic("UI")
@Feature("Личный кабинет")
class UserProfileIT extends BaseE2ETest {

    @BeforeEach
    void login() {
        open("/login");
        $("[data-testid='email']").setValue("test@example.com");
        $("[data-testid='password']").setValue("password123");
        $("[data-testid='login-button']").click();

        // Ждём редирект после успешной авторизации
        $("h1").shouldHave(text("Личный кабинет"));
    }

    @Test
    @Story("Профиль пользователя")
    void userProfile_showsUserData() {
        // then
        $("[data-testid='user-email']").shouldHave(text("test@example.com"));
        $("[data-testid='user-name']").shouldBe(visible);
    }

    @Test
    @Story("Редактирование профиля")
    void editProfile_savesChanges() {
        // when
        $("[data-testid='edit-profile']").click();
        $("[data-testid='user-name-input']").setValue("New Name");
        $("[data-testid='save-button']").click();

        // then
        $(".success-message").shouldBe(visible);
        $("[data-testid='user-name']").shouldHave(text("New Name"));
    }
}
```

## 16. Page Objects (опционально)

```java
/** Page Object для страницы каталога. */
public class CatalogPage {

    public static void open() {
        Selenide.open("/catalog");
    }

    public static SelenideElement searchInput() {
        return $("[data-testid='search-input']");
    }

    public static SelenideElement searchButton() {
        return $("[data-testid='search-button']");
    }

    public static ElementsCollection productCards() {
        return $$(".product-card");
    }

    @Step("Поиск товара: {query}")
    public static void search(String query) {
        searchInput().setValue(query);
        searchButton().click();
    }

    @Step("Фильтрация по категории: {category}")
    public static void filterByCategory(String category) {
        $("[data-testid='category-filter']").click();
        $("[data-value='" + category + "']").click();
    }
}
```

Использование:
```java
@Test
void searchProduct_findsItems() {
    CatalogPage.open();
    CatalogPage.search("Java");
    CatalogPage.productCards().shouldHave(sizeGreaterThan(0));
}
```

## 17. Dependencies для E2E

```xml
<!-- Selenide -->
<dependency>
    <groupId>com.codeborne</groupId>
    <artifactId>selenide</artifactId>
    <version>7.2.2</version>
    <scope>test</scope>
</dependency>

<!-- Testcontainers Selenium -->
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>selenium</artifactId>
    <scope>test</scope>
</dependency>

<!-- Allure Selenide -->
<dependency>
    <groupId>io.qameta.allure</groupId>
    <artifactId>allure-selenide</artifactId>
    <version>${allure.version}</version>
    <scope>test</scope>
</dependency>
```

## 18. Docker Images для разных платформ

```java
// Универсальный способ — определяем архитектуру
private static DockerImageName getBrowserImage() {
    String arch = System.getProperty("os.arch").toLowerCase();

    if (arch.contains("aarch64") || arch.contains("arm")) {
        // ARM64: Apple M1/M2/M3, Linux ARM
        return DockerImageName.parse("seleniarm/standalone-chromium:latest")
            .asCompatibleSubstituteFor("selenium/standalone-chrome");
    } else {
        // x86_64: Intel/AMD
        return DockerImageName.parse("selenium/standalone-chrome:latest");
    }
}

@Container
static BrowserWebDriverContainer<?> browser = new BrowserWebDriverContainer<>(getBrowserImage())
    .withCapabilities(chromeOptions());
```

---

# Part 5: Test Data Builders

## 19. Переиспользуемые builders

```java
/**
 * Builders для тестовых данных.
 * Вынесены в отдельный класс для переиспользования.
 */
public final class TestDataBuilders {

    private TestDataBuilders() {}

    // ─────────────────────────────────────────────────────────────
    // Orders
    // ─────────────────────────────────────────────────────────────

    /** Создаёт валидный запрос на создание заказа. */
    public static CreateOrderRequest createValidRequest() {
        return CreateOrderRequest.builder()
            .customerId("customer-" + UUID.randomUUID())
            .items(List.of(
                new ItemDto("product-1", BigDecimal.valueOf(100)),
                new ItemDto("product-2", BigDecimal.valueOf(200))
            ))
            .build();
    }

    /** Создаёт тестовый заказ с дефолтными значениями. */
    public static Order createTestOrder() {
        return Order.builder()
            .id("order-" + UUID.randomUUID())
            .customerId("customer-1")
            .status(OrderStatus.CREATED)
            .total(BigDecimal.valueOf(300))
            .items(List.of(createTestItem()))
            .createdAt(Instant.now())
            .build();
    }

    /** Создаёт заказ с указанным статусом. */
    public static Order createOrderWithStatus(final OrderStatus status) {
        return createTestOrder().toBuilder()
            .status(status)
            .build();
    }

    /** Создаёт заказ для указанного клиента. */
    public static Order createOrderForCustomer(final String customerId) {
        return createTestOrder().toBuilder()
            .customerId(customerId)
            .build();
    }

    /** Создаёт заказ с указанной суммой. */
    public static Order createOrderWithTotal(final String customerId, final BigDecimal total) {
        return createTestOrder().toBuilder()
            .customerId(customerId)
            .total(total)
            .build();
    }

    /** Создаёт отправленный заказ (для тестов отмены). */
    public static Order createShippedOrder() {
        return createOrderWithStatus(OrderStatus.SHIPPED);
    }

    // ─────────────────────────────────────────────────────────────
    // Items
    // ─────────────────────────────────────────────────────────────

    /** Создаёт тестовый товар. */
    public static ItemDto createTestItem() {
        return new ItemDto("product-" + UUID.randomUUID(), BigDecimal.valueOf(100));
    }

    /** Создаёт валидный товар. */
    public static ItemDto createValidItem() {
        return createTestItem();
    }

    // ─────────────────────────────────────────────────────────────
    // JSON helpers
    // ─────────────────────────────────────────────────────────────

    private static final ObjectMapper MAPPER = new ObjectMapper()
        .registerModule(new JavaTimeModule())
        .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);

    /** Конвертирует объект в JSON. */
    @SneakyThrows
    public static String toJson(final Object obj) {
        return MAPPER.writeValueAsString(obj);
    }
}
```

Использование в тестах:
```java
import static com.example.TestDataBuilders.*;

class OrderServiceTest {

    @Test
    void createOrder_success() {
        // given
        final CreateOrderRequest request = createValidRequest();

        // when
        final Order result = orderService.createOrder(request);

        // then
        assertThat(result).isNotNull();
    }
}
```

<!-- /section:e2e -->

---

<!-- section:maven -->

# Part 6: Package Structure & Maven Configuration

## 20. Разделение Unit и Integration Tests

```
src/
├── main/java/
│   └── com/example/order/
│       ├── controller/
│       ├── service/
│       └── repository/
└── test/java/
    └── com/example/order/
        ├── unit/                          # Unit тесты (Surefire)
        │   ├── service/
        │   │   └── OrderServiceTest.java  # *Test.java
        │   └── TestDataBuilders.java
        └── integration/                   # Integration тесты (Failsafe)
            ├── BaseIntegrationTest.java
            ├── api/
            │   └── OrderControllerIT.java # *IT.java
            ├── kafka/
            │   └── OrderKafkaIT.java
            └── repository/
                └── OrderRepositoryIT.java
```

**Naming conventions:**
- `*Test.java` — Unit тесты → **Surefire** (mvn test)
- `*IT.java` — Integration тесты → **Failsafe** (mvn verify)

## 21. Properties

```xml
<properties>
    <jacoco.version>0.8.12</jacoco.version>
    <allure.version>2.29.0</allure.version>
    <aspectj.version>1.9.24</aspectj.version>
    <surefire.version>3.5.3</surefire.version>
    <failsafe.version>3.5.3</failsafe.version>

    <!-- JaCoCo пишет сюда свой -javaagent, пустой по умолчанию -->
    <argLine></argLine>
</properties>
```

## 22. JaCoCo Plugin

```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>${jacoco.version}</version>
    <executions>
        <!-- Пишет -javaagent в property argLine -->
        <execution>
            <id>prepare-agent</id>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>

        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

**Quality gate (в отдельном profile или в pluginManagement):**

```xml
<execution>
    <id>check</id>
    <phase>verify</phase>
    <goals>
        <goal>check</goal>
    </goals>
    <configuration>
        <rules>
            <rule>
                <element>BUNDLE</element>
                <limits>
                    <limit>
                        <counter>LINE</counter>
                        <value>COVEREDRATIO</value>
                        <minimum>0.80</minimum>
                    </limit>
                    <limit>
                        <counter>BRANCH</counter>
                        <value>COVEREDRATIO</value>
                        <minimum>0.80</minimum>
                    </limit>
                </limits>
            </rule>
        </rules>
        <excludes>
            <exclude>**/*Config.class</exclude>
            <exclude>**/*Properties.class</exclude>
            <exclude>**/Application.class</exclude>
        </excludes>
    </configuration>
</execution>
```

## 23. Surefire Plugin (Unit Tests)

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>${surefire.version}</version>
    <configuration>
        <!--
            ${argLine} = JaCoCo пишет сюда свой -javaagent
            -XX:+EnableDynamicAgentLoading = для Java 21+
            -javaagent:aspectjweaver = для Allure @Step
        -->
        <argLine>${argLine} -XX:+EnableDynamicAgentLoading -Dfile.encoding=${project.build.sourceEncoding} -javaagent:"${settings.localRepository}/org/aspectj/aspectjweaver/${aspectj.version}/aspectjweaver-${aspectj.version}.jar"</argLine>

        <includes>
            <include>**/*Test.java</include>
        </includes>
        <excludes>
            <exclude>**/*IT.java</exclude>
        </excludes>

        <systemPropertyVariables>
            <allure.results.directory>${project.build.directory}/allure-results</allure.results.directory>
        </systemPropertyVariables>
    </configuration>
    <dependencies>
        <dependency>
            <groupId>org.aspectj</groupId>
            <artifactId>aspectjweaver</artifactId>
            <version>${aspectj.version}</version>
        </dependency>
    </dependencies>
</plugin>
```

## 24. Failsafe Plugin (Integration Tests)

**Обычно в отдельном profile `integration-tests`:**

```xml
<profiles>
    <profile>
        <id>integration-tests</id>
        <build>
            <plugins>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-failsafe-plugin</artifactId>
                    <version>${failsafe.version}</version>
                    <executions>
                        <execution>
                            <goals>
                                <goal>integration-test</goal>
                                <goal>verify</goal>
                            </goals>
                        </execution>
                    </executions>
                    <configuration>
                        <argLine>${argLine} -XX:+EnableDynamicAgentLoading -Dfile.encoding=${project.build.sourceEncoding} -javaagent:"${settings.localRepository}/org/aspectj/aspectjweaver/${aspectj.version}/aspectjweaver-${aspectj.version}.jar"</argLine>

                        <includes>
                            <include>**/*IT.java</include>
                        </includes>

                        <systemPropertyVariables>
                            <allure.results.directory>${project.build.directory}/allure-results</allure.results.directory>
                        </systemPropertyVariables>
                    </configuration>
                    <dependencies>
                        <dependency>
                            <groupId>org.aspectj</groupId>
                            <artifactId>aspectjweaver</artifactId>
                            <version>${aspectj.version}</version>
                        </dependency>
                    </dependencies>
                </plugin>
            </plugins>
        </build>
    </profile>
</profiles>
```

## 25. Allure Maven Plugin

```xml
<plugin>
    <groupId>io.qameta.allure</groupId>
    <artifactId>allure-maven</artifactId>
    <version>2.15.2</version>
    <configuration>
        <reportVersion>${allure.version}</reportVersion>
        <resultsDirectory>${project.build.directory}/allure-results</resultsDirectory>
    </configuration>
</plugin>
```

## 26. Команды запуска

```bash
# Только unit тесты (быстро, без Docker)
mvn test

# Integration тесты (profile)
mvn verify -Pintegration-tests

# Coverage check (profile)
mvn verify -Pcoverage

# Allure отчёт
mvn allure:serve
```

## 27. Test Dependencies (pom.xml)

```xml
<dependencies>
    <!-- Spring Boot Test (JUnit 5 + Mockito + AssertJ) -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>

    <!-- Testcontainers -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-testcontainers</artifactId>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>postgresql</artifactId>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>kafka</artifactId>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>junit-jupiter</artifactId>
        <scope>test</scope>
    </dependency>

    <!-- Awaitility для async тестов -->
    <dependency>
        <groupId>org.awaitility</groupId>
        <artifactId>awaitility</artifactId>
        <scope>test</scope>
    </dependency>

    <!-- WireMock для external APIs -->
    <dependency>
        <groupId>org.wiremock</groupId>
        <artifactId>wiremock-standalone</artifactId>
        <version>3.3.1</version>
        <scope>test</scope>
    </dependency>

    <!-- Allure JUnit 5 -->
    <dependency>
        <groupId>io.qameta.allure</groupId>
        <artifactId>allure-junit5</artifactId>
        <version>${allure.version}</version>
        <scope>test</scope>
    </dependency>

    <!-- AspectJ для Allure @Step -->
    <dependency>
        <groupId>org.aspectj</groupId>
        <artifactId>aspectjweaver</artifactId>
        <version>${aspectj.version}</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

---

# Quick Checklist

**Структура теста:**
- [ ] Naming: `method_condition_expectedResult`
- [ ] Given-When-Then с комментариями
- [ ] AssertJ assertions (не JUnit)
- [ ] Allure: @Epic, @Feature, @Story, @Severity, @Step

**Организация:**
- [ ] @Nested классы для группировки по методам
- [ ] TestDataBuilders для переиспользования
- [ ] Разделение пакетов: `unit/` и `integration/`

**Naming conventions:**
- [ ] `*Test.java` — Unit тесты (Surefire, mvn test)
- [ ] `*IT.java` — Integration тесты (Failsafe, mvn verify)

**Интеграционные тесты (основная корзина):**
- [ ] Для нетипичного кода: Context7 → как реально используют API
- [ ] Создай оптимальные тестовые сценарии (не просто coverage)
- [ ] **Сначала позитивные** сценарии (happy path)
- [ ] **Затем критические негативные** (404, 400, 409, 401/403)
- [ ] **НЕ пиши бенчмарки** производительности (для JMeter/Gatling)
- [ ] **Podman** настроен: `DOCKER_HOST`, `TESTCONTAINERS_RYUK_DISABLED=true`
- [ ] BaseIntegrationTest с Testcontainers
- [ ] HTTP endpoints через TestRestTemplate
- [ ] Kafka через реальный брокер (Testcontainers)
- [ ] JDBC через реальный PostgreSQL (Testcontainers)
- [ ] External APIs через WireMock

**Unit тесты (для coverage):**
- [ ] Edge cases с Mockito
- [ ] Validation branches
- [ ] Error handling paths

**E2E тесты (если есть frontend):**
- [ ] Selenide + BrowserWebDriverContainer
- [ ] ARM64: `seleniarm/standalone-chromium` (Apple M1/M2/M3)
- [ ] x86_64: `selenium/standalone-chrome`
- [ ] Podman: `host.containers.internal` вместо localhost
- [ ] ChromeOptions: `--no-sandbox`, `--disable-gpu`, `--disable-dev-shm-usage`
- [ ] Allure-Selenide: скриншоты при падении
- [ ] Page Objects для переиспользования

**Maven plugins:**
- [ ] Properties: `<argLine></argLine>` (пустой, JaCoCo заполнит)
- [ ] JaCoCo: prepare-agent (пишет в argLine)
- [ ] Surefire/Failsafe argLine: `${argLine} -XX:+EnableDynamicAgentLoading -javaagent:"${settings.localRepository}/org/aspectj/aspectjweaver/${aspectj.version}/aspectjweaver-${aspectj.version}.jar"`
- [ ] Failsafe в profile `integration-tests`
- [ ] Allure: allure-maven для отчётов

**Coverage:**
- [ ] LINE ≥ 80%
- [ ] BRANCH ≥ 80%
- [ ] JaCoCo check на merged.exec

<!-- /section:maven -->
