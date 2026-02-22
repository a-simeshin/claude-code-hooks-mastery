# React Code Standards

<!-- section:core -->

## 1. Functional Components Only

Только функциональные компоненты. Классовые компоненты запрещены.

```tsx
// BAD: Классовый компонент — устаревший подход
class UserCard extends React.Component<UserCardProps> {
  render() {
    return <div>{this.props.name}</div>;
  }
}

// GOOD: Функциональный компонент с явной типизацией
interface UserCardProps {
  /** Имя пользователя для отображения. */
  name: string;
  /** Email для ссылки mailto. */
  email: string;
  /** Callback при клике на карточку. */
  onClick?: (userId: string) => void;
}

function UserCard({ name, email, onClick }: UserCardProps) {
  return (
    <div className="user-card" onClick={() => onClick?.(email)}>
      <h3>{name}</h3>
      <p>{email}</p>
    </div>
  );
}
```

**Правила:**
- Всегда `function` declaration (не `const Component = () => {}` для компонентов верхнего уровня)
- Props интерфейс объявляется отдельно, НАД компонентом
- `export` на самом компоненте или внизу файла, но единообразно в проекте

## 2. Custom Hooks Extraction

Логика выносится в кастомные хуки. Компонент — только рендер.

```tsx
// BAD: Логика размазана по компоненту
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    fetch(`/api/users/${userId}`)
      .then((res) => res.json())
      .then((data) => {
        if (!ignore) {
          setUser(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!ignore) {
          setError(err.message);
          setLoading(false);
        }
      });
    return () => { ignore = true; };
  }, [userId]);

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!user) return null;

  return <div>{user.name}</div>;
}

// GOOD: Хук отдельно, компонент отдельно
function useUser(userId: string) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    fetch(`/api/users/${userId}`)
      .then((res) => res.json())
      .then((data) => {
        if (!ignore) {
          setUser(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!ignore) {
          setError(err.message);
          setLoading(false);
        }
      });
    return () => { ignore = true; };
  }, [userId]);

  return { user, loading, error };
}

function UserProfile({ userId }: { userId: string }) {
  const { user, loading, error } = useUser(userId);

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!user) return null;

  return <div>{user.name}</div>;
}
```

**Правило:** Если в компоненте больше одного `useState` + `useEffect` — выноси в хук.

## 3. Props Typing with TypeScript Interfaces

Все пропсы типизируются через `interface`. Никаких `any`, `object`, inline типов.

```tsx
// BAD: Inline типы, any, нет документации
function OrderList({ orders, onSelect }: { orders: any[]; onSelect: any }) {
  return <ul>{orders.map((o) => <li key={o.id}>{o.name}</li>)}</ul>;
}

// BAD: React.FC — скрывает children, мешает дженерикам
const OrderList: React.FC<{ orders: Order[] }> = ({ orders }) => {
  return <ul>{orders.map((o) => <li key={o.id}>{o.name}</li>)}</ul>;
};

// GOOD: Явный interface, JSDoc комментарии
interface OrderListProps {
  /** Список заказов для отображения. */
  orders: Order[];
  /** Callback при выборе заказа. */
  onSelect: (orderId: string) => void;
  /** CSS класс для контейнера (опционально). */
  className?: string;
}

function OrderList({ orders, onSelect, className }: OrderListProps) {
  return (
    <ul className={className}>
      {orders.map((order) => (
        <li key={order.id} onClick={() => onSelect(order.id)}>
          {order.name} - {order.total}
        </li>
      ))}
    </ul>
  );
}
```

**Правила:**
- Не использовать `React.FC` — мешает дженерикам, устаревшая практика
- Children пробрасывать явно: `children: React.ReactNode`
- Event handlers типизировать: `onClick: (id: string) => void`, не `Function`

## 4. useState vs useReducer

`useState` для простых значений. `useReducer` для связанных состояний.

```tsx
// BAD: Множество связанных useState — легко рассинхронизировать
function RegistrationForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  async function handleSubmit() {
    setIsSubmitting(true);
    setErrors({});
    setIsSuccess(false);
    // Легко забыть сбросить одно из состояний...
  }
}

// GOOD: useReducer для связанных состояний формы
interface FormState {
  name: string;
  email: string;
  password: string;
  errors: Record<string, string>;
  status: "idle" | "submitting" | "success" | "error";
}

type FormAction =
  | { type: "SET_FIELD"; field: keyof FormState; value: string }
  | { type: "SUBMIT" }
  | { type: "SUCCESS" }
  | { type: "ERROR"; errors: Record<string, string> }
  | { type: "RESET" };

const initialState: FormState = {
  name: "",
  email: "",
  password: "",
  errors: {},
  status: "idle",
};

function formReducer(state: FormState, action: FormAction): FormState {
  switch (action.type) {
    case "SET_FIELD":
      return { ...state, [action.field]: action.value, errors: {} };
    case "SUBMIT":
      return { ...state, status: "submitting", errors: {} };
    case "SUCCESS":
      return { ...initialState, status: "success" };
    case "ERROR":
      return { ...state, status: "error", errors: action.errors };
    case "RESET":
      return initialState;
  }
}

function RegistrationForm() {
  const [state, dispatch] = useReducer(formReducer, initialState);
  // Все переходы состояний атомарны и предсказуемы
}
```

**Когда какой:**
- `useState`: булевы флаги, строки, отдельные числа
- `useReducer`: формы, wizards, корзины, любые связанные состояния

## 5. useEffect Cleanup and Dependencies

Всегда cleanup. Зависимости — явные и минимальные.

```tsx
// BAD: Нет cleanup — утечка памяти, race condition
useEffect(() => {
  fetch(`/api/users/${userId}`)
    .then((res) => res.json())
    .then((data) => setUser(data));
}, [userId]);

// BAD: Объект в зависимостях — бесконечный цикл
useEffect(() => {
  fetchData(filters);
}, [filters]); // filters = { page: 1, search: '' } — новый объект каждый рендер!

// GOOD: Cleanup для отмены запроса и предотвращения race condition
useEffect(() => {
  let ignore = false;
  const controller = new AbortController();

  async function fetchUser() {
    try {
      const response = await fetch(`/api/users/${userId}`, {
        signal: controller.signal,
      });
      const data = await response.json();
      if (!ignore) {
        setUser(data);
      }
    } catch (error) {
      if (!ignore && error instanceof Error && error.name !== "AbortError") {
        setError(error.message);
      }
    }
  }

  fetchUser();

  return () => {
    ignore = true;
    controller.abort();
  };
}, [userId]);

// GOOD: Примитивные зависимости вместо объектов
useEffect(() => {
  fetchData({ page, search });
}, [page, search]); // Примитивы — стабильные зависимости
```

**Правила:**
- Каждый `useEffect` ОБЯЗАН иметь cleanup (или явный комментарий почему не нужен)
- В зависимостях только примитивы, стабильные refs, или мемоизированные значения
- Пустой массив `[]` = выполнить один раз при маунте

## 6. useMemo/useCallback — Only When Needed

НЕ оборачивай все подряд. Мемоизация нужна в конкретных случаях.

```tsx
// BAD: Бессмысленная мемоизация — overhead без пользы
function UserList({ users }: { users: User[] }) {
  const sortedUsers = useMemo(() => users.sort(byName), [users]);
  const handleClick = useCallback(() => {
    console.log("clicked");
  }, []);

  return <div onClick={handleClick}>{sortedUsers.map(renderUser)}</div>;
}

// GOOD: useMemo только для тяжелых вычислений
function DataGrid({ rows, filters }: DataGridProps) {
  // Тяжелая фильтрация + сортировка тысяч строк — мемоизация оправдана
  const processedRows = useMemo(
    () => rows.filter(matchesFilters(filters)).sort(bySortKey),
    [rows, filters]
  );

  return <Table rows={processedRows} />;
}

// GOOD: useCallback при передаче в мемоизированный дочерний компонент
function ParentComponent() {
  const [count, setCount] = useState(0);

  // Без useCallback ExpensiveChild будет ре-рендериться при каждом изменении count
  const handleSubmit = useCallback((data: FormData) => {
    api.submit(data);
  }, []);

  return (
    <>
      <button onClick={() => setCount((c) => c + 1)}>{count}</button>
      <ExpensiveChild onSubmit={handleSubmit} />
    </>
  );
}

const ExpensiveChild = memo(function ExpensiveChild({
  onSubmit,
}: {
  onSubmit: (data: FormData) => void;
}) {
  // Тяжелый рендер — memo + useCallback на пропсах оправданы
  return <HeavyForm onSubmit={onSubmit} />;
});
```

**Когда мемоизировать:**
- `useMemo`: фильтрация/сортировка больших массивов, тяжелые вычисления
- `useCallback`: callback передается в `memo()` компонент, или в зависимости `useEffect`
- **НЕ нужно:** простые вычисления, обработчики прямо на JSX элементах

## 7. Component Composition over Prop Drilling

Композиция вместо прокидывания пропсов через 3+ уровня.

```tsx
// BAD: Prop drilling — theme прокидывается через 3 компонента
function App() {
  const [theme, setTheme] = useState<Theme>("light");
  return <Layout theme={theme} setTheme={setTheme} />;
}
function Layout({ theme, setTheme }: LayoutProps) {
  return <Header theme={theme} setTheme={setTheme} />;
}
function Header({ theme, setTheme }: HeaderProps) {
  return <ThemeToggle theme={theme} setTheme={setTheme} />;
}

// GOOD: Context для глобального состояния (тема, авторизация, locale)
interface ThemeContextValue {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return context;
}

function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>("light");
  const value = useMemo(() => ({ theme, setTheme }), [theme]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

// Компонент берет данные из контекста, без prop drilling
function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  return (
    <button onClick={() => setTheme(theme === "light" ? "dark" : "light")}>
      {theme === "light" ? "Dark" : "Light"} mode
    </button>
  );
}

// GOOD: Composition pattern — передача children вместо prop drilling
function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="layout">
      <Sidebar />
      <main>{children}</main>
    </div>
  );
}

function App() {
  return (
    <Layout>
      <Dashboard />
    </Layout>
  );
}
```

**Правила:**
- Prop drilling через 2+ промежуточных компонента = рефактори
- Context для: темы, auth, locale, feature flags
- `children` pattern для layout компонентов

## 8. Error Boundaries with Fallback UI

Каждая крупная секция UI обернута в Error Boundary.

```tsx
// BAD: Одна ошибка роняет все приложение
function App() {
  return (
    <div>
      <Header />
      <Dashboard />  {/* Ошибка здесь сломает весь App */}
      <Footer />
    </div>
  );
}

// GOOD: Error boundary изолирует ошибки, класс — единственный допустимый случай
interface ErrorBoundaryProps {
  /** Fallback UI при ошибке. */
  fallback: React.ReactNode;
  /** Вложенные компоненты. */
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("ErrorBoundary caught:", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

// Использование: каждая секция изолирована
function App() {
  return (
    <div>
      <Header />
      <ErrorBoundary fallback={<p>Dashboard failed to load</p>}>
        <Dashboard />
      </ErrorBoundary>
      <ErrorBoundary fallback={<p>Sidebar failed to load</p>}>
        <Sidebar />
      </ErrorBoundary>
      <Footer />
    </div>
  );
}
```

**Правило:** Error Boundary — единственный случай, когда допускается классовый компонент (React пока не имеет хукового аналога для `getDerivedStateFromError`).

## 9. Suspense for Async Operations

`Suspense` + `React.lazy` для code splitting. `Suspense` + data fetching через фреймворк.

```tsx
// BAD: Ручной loading стейт для каждого компонента
function App() {
  const [DashboardModule, setDashboard] = useState<React.ComponentType | null>(null);

  useEffect(() => {
    import("./Dashboard").then((mod) => setDashboard(() => mod.default));
  }, []);

  if (!DashboardModule) return <Spinner />;
  return <DashboardModule />;
}

// GOOD: React.lazy + Suspense для code splitting
const Dashboard = lazy(() => import("./Dashboard"));
const Settings = lazy(() => import("./Settings"));
const Analytics = lazy(() => import("./Analytics"));

function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Suspense>
  );
}

// GOOD: Вложенный Suspense для гранулярного loading
function DashboardPage() {
  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <Suspense fallback={<ChartSkeleton />}>
        <RevenueChart />
      </Suspense>
      <Suspense fallback={<TableSkeleton />}>
        <OrdersTable />
      </Suspense>
    </div>
  );
}
```

**Правила:**
- `React.lazy()` для всех route-level компонентов
- `Suspense` с осмысленным fallback (skeleton, не просто spinner)
- Вложенный `Suspense` для параллельной загрузки секций

## 10. Key Prop and List Rendering

Ключи должны быть стабильными и уникальными. Никаких `index` для динамических списков.

```tsx
// BAD: Index как ключ — баги при сортировке, удалении, вставке
function TodoList({ todos }: { todos: Todo[] }) {
  return (
    <ul>
      {todos.map((todo, index) => (
        <li key={index}>{todo.text}</li>  // При удалении элемента React перепутает состояния
      ))}
    </ul>
  );
}

// BAD: Нестабильный ключ — ре-маунт каждый рендер
function TodoList({ todos }: { todos: Todo[] }) {
  return (
    <ul>
      {todos.map((todo) => (
        <li key={Math.random()}>{todo.text}</li>  // Новый ключ = новый DOM узел каждый раз
      ))}
    </ul>
  );
}

// GOOD: Стабильный уникальный ID из данных
function TodoList({ todos }: { todos: Todo[] }) {
  if (todos.length === 0) {
    return <EmptyState message="No todos yet" />;
  }

  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>
          <TodoItem todo={todo} />
        </li>
      ))}
    </ul>
  );
}

// OK: Index допустим ТОЛЬКО для статических списков (меню, навигация)
const NAV_ITEMS = ["Home", "About", "Contact"] as const;

function NavMenu() {
  return (
    <nav>
      {NAV_ITEMS.map((item, index) => (
        <a key={index} href={`/${item.toLowerCase()}`}>{item}</a>
      ))}
    </nav>
  );
}
```

**Правила:**
- `key` = уникальный ID из данных (`todo.id`, `user.uuid`)
- `index` как ключ допустим ТОЛЬКО если список статичный и не сортируется/фильтруется
- Всегда проверять пустой список — рендерить EmptyState

<!-- /section:core -->

---

<!-- section:nextjs -->

## 11. Server vs Client Components

По умолчанию все компоненты серверные. `'use client'` только когда нужна интерактивность.

```tsx
// BAD: 'use client' на каждом компоненте — теряется смысл SSR
'use client';  // Не нужен! Нет интерактивности

import { db } from '@/lib/db';

export default function UserList() {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    fetch('/api/users').then(r => r.json()).then(setUsers);
  }, []);

  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}

// GOOD: Server Component — прямой доступ к данным, нет useState/useEffect
import { db } from '@/lib/db';

export default async function UserList() {
  // Прямой запрос к БД — никаких API routes, никаких useEffect
  const users = await db.user.findMany({ orderBy: { name: 'asc' } });

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}

// GOOD: 'use client' только для интерактивного компонента
'use client';

import { useState } from 'react';

interface SearchInputProps {
  /** Callback при изменении поискового запроса. */
  onSearch: (query: string) => void;
}

export function SearchInput({ onSearch }: SearchInputProps) {
  const [query, setQuery] = useState('');

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setQuery(e.target.value);
    onSearch(e.target.value);
  }

  return <input value={query} onChange={handleChange} placeholder="Search..." />;
}
```

**Когда `'use client'`:**
- `useState`, `useReducer`, `useEffect` и другие хуки
- Event handlers (`onClick`, `onChange`)
- Browser APIs (`localStorage`, `window`)
- Сторонние библиотеки без серверной поддержки

**Когда Server Component (по умолчанию):**
- Получение данных (fetch, DB запросы)
- Доступ к серверным ресурсам (файловая система, env)
- Рендер статического контента

## 12. App Router File Conventions

Каждый файл в `app/` имеет определенное назначение. Не путать.

```
app/
  layout.tsx      — Общий layout (оборачивает children), сохраняется между навигациями
  page.tsx        — UI для данного route сегмента
  loading.tsx     — Suspense fallback (показывается при загрузке page)
  error.tsx       — Error boundary для route сегмента (ОБЯЗАН быть 'use client')
  not-found.tsx   — UI для 404 (вызывается через notFound())
  template.tsx    — Как layout, но ре-маунтится при навигации (редко нужен)
```

```tsx
// app/layout.tsx — Root layout, ОБЯЗАТЕЛЕН
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'My App',
  description: 'Application description',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}

// app/dashboard/page.tsx — Server Component по умолчанию
export default async function DashboardPage() {
  const stats = await fetchDashboardStats();
  return <DashboardView stats={stats} />;
}

// app/dashboard/loading.tsx — Показывается пока page загружается
export default function DashboardLoading() {
  return <DashboardSkeleton />;
}

// app/dashboard/error.tsx — ОБЯЗАН быть 'use client'
'use client';

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function DashboardError({ error, reset }: ErrorPageProps) {
  return (
    <div>
      <h2>Something went wrong</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

## 13. Server Actions for Mutations

Server Actions для изменения данных. Не для чтения.

```tsx
// BAD: API route + fetch для простого создания записи
// app/api/posts/route.ts
export async function POST(request: Request) {
  const data = await request.json();
  const post = await db.post.create({ data });
  return Response.json(post);
}

// app/posts/page.tsx
'use client';
function CreatePost() {
  async function handleSubmit(data: FormData) {
    await fetch('/api/posts', { method: 'POST', body: JSON.stringify(data) });
  }
}

// GOOD: Server Action — прямой вызов серверной функции
// app/posts/actions.ts
'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { db } from '@/lib/db';

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  if (!title || !content) {
    return { error: 'Title and content are required' };
  }

  await db.post.create({
    data: { title, content },
  });

  revalidatePath('/posts');
  redirect('/posts');
}

// app/posts/new/page.tsx — Server Component с формой
import { createPost } from '../actions';

export default function NewPostPage() {
  return (
    <form action={createPost}>
      <input name="title" required />
      <textarea name="content" required />
      <button type="submit">Create Post</button>
    </form>
  );
}

// GOOD: Server Action в клиентском компоненте с useActionState
'use client';

import { useActionState } from 'react';
import { createPost } from '../actions';

function CreatePostForm() {
  const [state, formAction, isPending] = useActionState(createPost, null);

  return (
    <form action={formAction}>
      <input name="title" required disabled={isPending} />
      <textarea name="content" required disabled={isPending} />
      {state?.error && <p className="error">{state.error}</p>}
      <button type="submit" disabled={isPending}>
        {isPending ? 'Creating...' : 'Create Post'}
      </button>
    </form>
  );
}
```

## 14. Data Fetching in Server Components

В Server Components данные получаем напрямую. Никаких useEffect!

```tsx
// BAD: useEffect в Server Component — не работает
export default async function PostsPage() {
  const [posts, setPosts] = useState([]);  // Ошибка! Хуки в Server Component нельзя
  useEffect(() => { fetch(...)}, []);       // Ошибка!
}

// GOOD: Прямой async/await в Server Component
import { db } from '@/lib/db';

export default async function PostsPage() {
  // Прямой запрос к БД — нет API route, нет useEffect
  const posts = await db.post.findMany({
    orderBy: { createdAt: 'desc' },
    take: 20,
  });

  return (
    <div>
      <h1>Posts</h1>
      {posts.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}

// GOOD: Fetch с контролем кеширования
export default async function StatsPage() {
  // Статические данные — кешируются навсегда (по умолчанию)
  const config = await fetch('https://api.example.com/config', {
    cache: 'force-cache',
  }).then((r) => r.json());

  // Динамические данные — не кешируются
  const stats = await fetch('https://api.example.com/stats', {
    cache: 'no-store',
  }).then((r) => r.json());

  // Данные с ревалидацией каждые 60 секунд
  const posts = await fetch('https://api.example.com/posts', {
    next: { revalidate: 60 },
  }).then((r) => r.json());

  return <Dashboard config={config} stats={stats} posts={posts} />;
}
```

## 15. Metadata API for SEO

Метаданные через `export const metadata` или `generateMetadata`.

```tsx
// BAD: <Head> из next/head — это Pages Router, не App Router
import Head from 'next/head';

export default function Page() {
  return (
    <>
      <Head><title>My Page</title></Head>
      <div>Content</div>
    </>
  );
}

// GOOD: Статические метаданные
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Dashboard | My App',
  description: 'Application dashboard with analytics and metrics',
  openGraph: {
    title: 'Dashboard',
    description: 'View your analytics',
    type: 'website',
  },
};

export default function DashboardPage() {
  return <Dashboard />;
}

// GOOD: Динамические метаданные (зависят от params)
interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const post = await db.post.findUnique({ where: { slug } });

  if (!post) {
    return { title: 'Post Not Found' };
  }

  return {
    title: `${post.title} | Blog`,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: post.coverImage ? [{ url: post.coverImage }] : [],
    },
  };
}

export default async function PostPage({ params }: PageProps) {
  const { slug } = await params;
  const post = await db.post.findUnique({ where: { slug } });
  if (!post) notFound();
  return <PostView post={post} />;
}
```

## 16. Route Handlers (API Routes)

Route handlers для внешних API, webhooks. Для внутренних мутаций — Server Actions.

```tsx
// app/api/webhooks/stripe/route.ts — Webhook endpoint
import { NextRequest, NextResponse } from 'next/server';
import { headers } from 'next/headers';

export async function POST(request: NextRequest) {
  const body = await request.text();
  const headersList = await headers();
  const signature = headersList.get('stripe-signature');

  if (!signature) {
    return NextResponse.json({ error: 'Missing signature' }, { status: 400 });
  }

  try {
    const event = verifyStripeWebhook(body, signature);
    await handleStripeEvent(event);
    return NextResponse.json({ received: true });
  } catch (error) {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
  }
}

// app/api/users/[id]/route.ts — REST endpoint для внешних клиентов
import { NextRequest, NextResponse } from 'next/server';

interface RouteParams {
  params: Promise<{ id: string }>;
}

export async function GET(_request: NextRequest, { params }: RouteParams) {
  const { id } = await params;
  const user = await db.user.findUnique({ where: { id } });

  if (!user) {
    return NextResponse.json({ error: 'User not found' }, { status: 404 });
  }

  return NextResponse.json(user);
}
```

## 17. Middleware Patterns

Middleware для auth, redirects, i18n. Выполняется ДО рендеринга.

```tsx
// middleware.ts — в корне проекта (рядом с app/)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Пропускаем статику и API
  if (pathname.startsWith('/_next') || pathname.startsWith('/api')) {
    return NextResponse.next();
  }

  // Auth check
  const token = request.cookies.get('auth-token')?.value;

  if (!token && pathname.startsWith('/dashboard')) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // i18n: Redirect to default locale
  const locale = request.cookies.get('locale')?.value ?? 'ru';
  const response = NextResponse.next();
  response.headers.set('x-locale', locale);

  return response;
}

// matcher — указывает на каких путях запускать middleware
export const config = {
  matcher: [
    // Все пути кроме статики
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
```

## 18. Caching and Revalidation

`revalidatePath` и `revalidateTag` для инвалидации кеша после мутаций.

```tsx
// BAD: Нет ревалидации — данные устаревают
'use server';

export async function updatePost(id: string, data: PostData) {
  await db.post.update({ where: { id }, data });
  // Страница показывает старые данные!
}

// GOOD: revalidatePath — инвалидирует кеш для конкретного пути
'use server';

import { revalidatePath } from 'next/cache';

export async function updatePost(id: string, data: PostData) {
  await db.post.update({ where: { id }, data });

  revalidatePath('/posts');           // Инвалидирует страницу списка
  revalidatePath(`/posts/${id}`);     // Инвалидирует страницу поста
}

// GOOD: revalidateTag — инвалидирует по тегу (гибче)
import { revalidateTag } from 'next/cache';

// При получении данных — присваиваем тег
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: { tags: ['posts'] },
  });
  return res.json();
}

async function getPost(id: string) {
  const res = await fetch(`https://api.example.com/posts/${id}`, {
    next: { tags: ['posts', `post-${id}`] },
  });
  return res.json();
}

// При мутации — инвалидируем по тегу
export async function updatePost(id: string, data: PostData) {
  await db.post.update({ where: { id }, data });
  revalidateTag(`post-${id}`);  // Только конкретный пост
}

export async function deletePost(id: string) {
  await db.post.delete({ where: { id } });
  revalidateTag('posts');  // Весь список постов
}
```

## 19. Dynamic Routes and generateStaticParams

Динамические сегменты `[slug]` и pre-rendering через `generateStaticParams`.

```tsx
// app/posts/[slug]/page.tsx
import { notFound } from 'next/navigation';
import { db } from '@/lib/db';

interface PostPageProps {
  params: Promise<{ slug: string }>;
}

// Статическая генерация для известных slugs
export async function generateStaticParams() {
  const posts = await db.post.findMany({ select: { slug: true } });
  return posts.map((post) => ({ slug: post.slug }));
}

export default async function PostPage({ params }: PostPageProps) {
  const { slug } = await params;
  const post = await db.post.findUnique({ where: { slug } });

  if (!post) {
    notFound(); // Вернет 404 через app/posts/[slug]/not-found.tsx
  }

  return (
    <article>
      <h1>{post.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: post.contentHtml }} />
    </article>
  );
}

// app/posts/[slug]/not-found.tsx
export default function PostNotFound() {
  return (
    <div>
      <h2>Post not found</h2>
      <p>The post you are looking for does not exist.</p>
    </div>
  );
}
```

## 20. Parallel Routes and Intercepting Routes

Параллельные маршруты для сложных layout. Intercepting routes для модалок.

```
app/
  @analytics/       — Параллельный slot (рендерится одновременно с page)
    page.tsx
    loading.tsx
  @sidebar/          — Второй параллельный slot
    page.tsx
  layout.tsx         — Получает slots как props
  page.tsx
```

```tsx
// app/layout.tsx — Параллельные routes как props
interface DashboardLayoutProps {
  children: React.ReactNode;
  analytics: React.ReactNode;  // @analytics slot
  sidebar: React.ReactNode;    // @sidebar slot
}

export default function DashboardLayout({
  children,
  analytics,
  sidebar,
}: DashboardLayoutProps) {
  return (
    <div className="dashboard-layout">
      <aside>{sidebar}</aside>
      <main>{children}</main>
      <section>{analytics}</section>
    </div>
  );
}

// Intercepting routes для модалок:
// app/posts/(..)posts/[id]/page.tsx — перехватывает /posts/[id] из feed
// Показывает пост в модалке при навигации из списка,
// но полную страницу при прямом заходе по URL
```

<!-- /section:nextjs -->

---

<!-- section:vite -->

## 21. React Router v7 Setup

`createBrowserRouter` + `RouterProvider`. Объектная конфигурация маршрутов.

```tsx
// BAD: Старый JSX-based роутинг
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </BrowserRouter>
  );
}

// GOOD: createBrowserRouter с объектной конфигурацией
import { createBrowserRouter, RouterProvider } from 'react-router';

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    errorElement: <RootError />,
    children: [
      {
        index: true,
        element: <HomePage />,
        loader: homeLoader,
      },
      {
        path: 'posts',
        element: <PostsLayout />,
        children: [
          {
            index: true,
            element: <PostsList />,
            loader: postsLoader,
          },
          {
            path: ':postId',
            element: <PostDetail />,
            loader: postDetailLoader,
            action: postAction,
          },
        ],
      },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}
```

## 22. Route Loaders and Actions

Loaders для GET-данных, Actions для мутаций. Вместо useEffect для data fetching.

```tsx
// BAD: useEffect для загрузки данных в компоненте
function PostsList() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/posts').then(r => r.json()).then(setPosts).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spinner />;
  return <ul>{posts.map(p => <li key={p.id}>{p.title}</li>)}</ul>;
}

// GOOD: Loader загружает данные ДО рендера компонента
import { useLoaderData, type LoaderFunctionArgs } from 'react-router';

// Loader — выполняется до рендера, данные доступны сразу
export async function postsLoader({ request }: LoaderFunctionArgs) {
  const url = new URL(request.url);
  const page = url.searchParams.get('page') ?? '1';

  const response = await fetch(`/api/posts?page=${page}`, {
    signal: request.signal,  // Отмена при навигации
  });

  if (!response.ok) {
    throw new Response('Failed to load posts', { status: response.status });
  }

  return response.json();
}

// Action — обрабатывает POST/PUT/DELETE
export async function createPostAction({ request }: LoaderFunctionArgs) {
  const formData = await request.formData();
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  const response = await fetch('/api/posts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content }),
  });

  if (!response.ok) {
    return { error: 'Failed to create post' };
  }

  return { success: true };
}

// Компонент — чистый рендер, данные уже загружены
function PostsList() {
  const posts = useLoaderData() as Post[];

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

## 23. Lazy Loading with React.lazy + Suspense

Ленивая загрузка route-level компонентов. Не мелких UI элементов.

```tsx
// BAD: Все компоненты в бандле — огромный initial load
import { HomePage } from './pages/HomePage';
import { DashboardPage } from './pages/DashboardPage';
import { SettingsPage } from './pages/SettingsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';

// GOOD: lazy() для route-level компонентов
const HomePage = lazy(() => import('./pages/HomePage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));

// GOOD: React Router v7 встроенный lazy
const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        path: 'dashboard',
        lazy: () => import('./pages/DashboardPage'),
        // Модуль экспортирует: Component, loader, action, errorElement
      },
      {
        path: 'settings',
        lazy: () => import('./pages/SettingsPage'),
      },
      {
        path: 'analytics',
        lazy: {
          // Гранулярный lazy — загружаем loader и Component раздельно
          loader: async () => (await import('./pages/analytics.loader')).loader,
          Component: async () => (await import('./pages/AnalyticsPage')).default,
        },
      },
    ],
  },
]);

// GOOD: Suspense с осмысленным fallback
function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <RouterProvider router={router} />
    </Suspense>
  );
}
```

**Правила:**
- `lazy()` только для страниц и крупных модулей, не для кнопок и иконок
- React Router v7 `lazy` предпочтительнее `React.lazy` для routes
- Fallback = skeleton страницы, не пустой спиннер

## 24. Environment Variables (VITE_ prefix)

Клиентские переменные ОБЯЗАНЫ иметь префикс `VITE_`. Типизация через `env.d.ts`.

```tsx
// BAD: Нет VITE_ префикса — переменная не попадет в клиентский бандл
// .env
DATABASE_URL=postgres://...
API_KEY=secret-key

// console.log(import.meta.env.API_KEY) → undefined!

// GOOD: Префикс VITE_ для клиентских, без префикса для серверных
// .env
VITE_API_URL=https://api.example.com
VITE_APP_TITLE=My App
DATABASE_URL=postgres://...     # Только на сервере (build scripts)

// GOOD: Типизация через env.d.ts
// src/env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_APP_TITLE: string;
  readonly VITE_FEATURE_FLAGS: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// Использование — типизировано, автокомплит работает
const API_URL = import.meta.env.VITE_API_URL;
```

## 25. Proxy Configuration for API Calls

Dev proxy чтобы не сталкиваться с CORS. Относительные пути в коде.

```tsx
// BAD: Хардкод URL — разные для dev и prod, CORS проблемы
async function fetchPosts() {
  const response = await fetch('http://localhost:8080/api/posts');
  return response.json();
}

// GOOD: Относительные пути + Vite proxy
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8080',
        ws: true,
      },
    },
  },
});

// В коде — всегда относительные пути
async function fetchPosts(): Promise<Post[]> {
  const response = await fetch('/api/posts');  // Proxy перенаправит на :8080
  if (!response.ok) {
    throw new Error(`Failed to fetch posts: ${response.status}`);
  }
  return response.json();
}
```

## 26. Code Splitting Strategies

Разделение кода по маршрутам и тяжелым зависимостям.

```tsx
// BAD: Одна точка входа — все в одном бандле
import { Chart } from 'chart.js';    // 200KB!
import { Editor } from 'monaco-editor'; // 2MB!

// GOOD: Динамический импорт тяжелых зависимостей
const ChartComponent = lazy(() =>
  import('./components/Chart').then((mod) => ({ default: mod.Chart }))
);

// GOOD: Manual chunks в vite.config.ts
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Вендорные библиотеки в отдельный чанк (кешируется независимо)
          'vendor-react': ['react', 'react-dom'],
          'vendor-router': ['react-router'],
          'vendor-charts': ['chart.js', 'recharts'],
          'vendor-ui': ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu'],
        },
      },
    },
  },
});

// GOOD: Функциональное разделение — чанк для каждого feature модуля
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react')) return 'vendor-react';
            if (id.includes('chart')) return 'vendor-charts';
            return 'vendor'; // Все остальные npm пакеты
          }
        },
      },
    },
  },
});
```

## 27. Path Aliases Configuration

Алиасы вместо относительных путей `../../../`. Настройка в vite.config.ts + tsconfig.json.

```tsx
// BAD: Относительные импорты — хрупкие, нечитаемые
import { Button } from '../../../components/ui/Button';
import { useAuth } from '../../../../hooks/useAuth';
import { formatDate } from '../../../utils/format';

// GOOD: Алиасы через @/
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/hooks/useAuth';
import { formatDate } from '@/utils/format';
```

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});

// tsconfig.json (для TypeScript автокомплита)
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

## 28. CSS Modules and Tailwind Setup

CSS Modules для изоляции стилей. Tailwind для утилитарного подхода. Не смешивать.

```tsx
// BAD: Глобальные CSS классы — конфликты имен
import './UserCard.css';  // .card { } — может конфликтовать с другим .card

function UserCard() {
  return <div className="card">...</div>;
}

// GOOD вариант A: CSS Modules — изоляция по умолчанию
// UserCard.module.css
// .card { padding: 1rem; border: 1px solid #e5e7eb; border-radius: 8px; }
// .title { font-weight: 600; }

import styles from './UserCard.module.css';

function UserCard({ name }: { name: string }) {
  return (
    <div className={styles.card}>
      <h3 className={styles.title}>{name}</h3>
    </div>
  );
}

// GOOD вариант B: Tailwind CSS — утилитарные классы
function UserCard({ name }: { name: string }) {
  return (
    <div className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
      <h3 className="font-semibold text-lg">{name}</h3>
    </div>
  );
}

// GOOD: clsx/cn для условных классов (с Tailwind)
import { clsx } from 'clsx';

interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  children: React.ReactNode;
}

function Button({ variant, size = 'md', disabled, children }: ButtonProps) {
  return (
    <button
      className={clsx(
        'rounded font-medium transition-colors',
        {
          'bg-blue-600 text-white hover:bg-blue-700': variant === 'primary',
          'bg-gray-200 text-gray-800 hover:bg-gray-300': variant === 'secondary',
          'bg-red-600 text-white hover:bg-red-700': variant === 'danger',
        },
        {
          'px-2 py-1 text-sm': size === 'sm',
          'px-4 py-2 text-base': size === 'md',
          'px-6 py-3 text-lg': size === 'lg',
        },
        disabled && 'opacity-50 cursor-not-allowed'
      )}
      disabled={disabled}
    >
      {children}
    </button>
  );
}
```

## 29. Build Optimization

Анализ бандла, tree-shaking, оптимизация ассетов.

```ts
// vite.config.ts — Production оптимизация
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    // Минимальный target для меньшего полифилов
    target: 'es2020',
    // Размер warning
    chunkSizeWarningLimit: 500,
    // Source maps для production debugging (опционально)
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom'],
          'vendor-router': ['react-router'],
        },
      },
    },
  },
  // Оптимизация зависимостей для dev server
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router'],
  },
});
```

```bash
# Анализ бандла — обязательно перед production release
npx vite-bundle-visualizer

# Проверка размера
npx vite build --report
```

**Правила:**
- manualChunks для вендоров — кешируются отдельно от app кода
- `optimizeDeps.include` для быстрого dev server старта
- Проверять размер бандла перед каждым PR с новой зависимостью

## 30. HMR and Fast Refresh

Vite HMR работает автоматически. Не ломай его неправильными экспортами.

```tsx
// BAD: Смешивание компонентов и не-компонентов в одном файле ломает Fast Refresh
// utils-and-components.tsx
export const API_URL = '/api';  // Не компонент

export function UserCard() {    // Компонент
  return <div>User</div>;
}
// Vite Fast Refresh НЕ сработает — файл содержит смешанные экспорты

// GOOD: Разделяй компоненты и утилиты
// constants.ts
export const API_URL = '/api';

// UserCard.tsx — только компонент
export function UserCard() {
  return <div>User</div>;
}

// GOOD: Один компонент = один файл
// components/
//   UserCard.tsx        — компонент
//   UserCard.module.css — стили (опционально)
//   UserCard.test.tsx   — тесты
//   index.ts            — реэкспорт
```

**Правила:**
- Один файл = один компонент (или один хук)
- Константы, типы, утилиты — в отдельных файлах
- Не использовать `export default` и named exports в одном файле для компонентов

<!-- /section:vite -->

---

# Quick Checklist

Before submitting React/TypeScript code:

**Core React (all projects):**
- [ ] Функциональные компоненты only (class только для ErrorBoundary)
- [ ] Props типизированы через interface (не inline, не any)
- [ ] Не используется `React.FC` — обычная function declaration
- [ ] Сложная логика вынесена в custom hooks
- [ ] useEffect имеет cleanup и корректные зависимости
- [ ] useMemo/useCallback только где реально нужно (не везде)
- [ ] Нет prop drilling через 2+ компонента — используется Context или composition
- [ ] Error Boundaries оборачивают крупные секции UI
- [ ] Suspense с skeleton fallback для lazy-loaded компонентов
- [ ] Стабильные key для динамических списков (не index, не random)

**Next.js App Router:**
- [ ] Server Components по умолчанию, `'use client'` только для интерактивности
- [ ] Правильные file conventions (page.tsx, layout.tsx, loading.tsx, error.tsx)
- [ ] Server Actions для мутаций (не API routes для внутренних операций)
- [ ] Data fetching в Server Components (async/await, не useEffect)
- [ ] Metadata через `export const metadata` или `generateMetadata`
- [ ] `revalidatePath`/`revalidateTag` после мутаций
- [ ] `generateStaticParams` для динамических routes (SSG)
- [ ] error.tsx компоненты имеют `'use client'`

**Vite SPA:**
- [ ] `createBrowserRouter` с объектной конфигурацией (не JSX routes)
- [ ] Route loaders для data fetching (не useEffect)
- [ ] Lazy loading для route-level компонентов
- [ ] `VITE_` префикс для клиентских env переменных + env.d.ts типизация
- [ ] Proxy настроен в vite.config.ts, код использует относительные пути
- [ ] Manual chunks для вендорных библиотек
- [ ] Path aliases `@/` в vite.config.ts + tsconfig.json
- [ ] Один файл = один компонент (для Fast Refresh)
