# Design Document: ShopBug

## Overview

ShopBug is a Python/FastAPI/SQLite e-commerce backend with a dual purpose:

1. **Functional API** — a complete, testable e-commerce backend covering user authentication, product management, shopping cart, discount application, and order checkout.
2. **Research artefact** — after the correct implementation is verified, exactly 20 intentional, syntactically-valid but behaviourally-incorrect bugs are injected in a single commit. A ground-truth dataset records every bug's root cause, affected files, and a reproduction test.

The design is intentionally simple: one process, one SQLite file, no background tasks, no external services. Simplicity maximises the isolation and clarity of each injected bug.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐             │
│  │  Routes  │  │ Schemas  │  │  Models   │             │
│  │ (HTTP)   │  │(Pydantic)│  │(SQLAlchemy│             │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘             │
│       │              │              │                    │
│  ┌────▼──────────────▼──────────────▼─────┐             │
│  │               Services                  │             │
│  │  Auth │ Product │ Cart │ Discount │ Checkout│        │
│  └────────────────────┬────────────────────┘             │
│                        │                                 │
│  ┌─────────────────────▼──────────────────┐             │
│  │         SQLAlchemy ORM / SQLite         │             │
│  └────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

The application follows a layered architecture:

- **Routes** handle HTTP concerns (request parsing, response shaping, status codes).
- **Schemas** (Pydantic) perform input validation and serialisation.
- **Services** contain all business logic; they are the sole layer that modifies state.
- **Models** (SQLAlchemy ORM) declare database tables.
- **Database** (`database.py`) manages the engine, session factory, and `get_db` dependency.

---

## Components and Interfaces

### `app/main.py`
Creates the FastAPI application instance and registers all routers.

```python
app = FastAPI(title="ShopBug")
app.include_router(auth_router, prefix="/auth")
app.include_router(products_router, prefix="/products")
app.include_router(cart_router, prefix="/cart")
app.include_router(discount_router, prefix="/discounts")
app.include_router(checkout_router, prefix="/checkout")
```

### `app/database.py`
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./shopbug.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
```

### Routes

| Router | Prefix | Responsibilities |
|---|---|---|
| `auth.py` | `/auth` | POST `/register`, POST `/login` |
| `products.py` | `/products` | POST `/`, GET `/`, GET `/{id}`, GET `/search`, GET `/filter` |
| `cart.py` | `/cart` | POST `/add`, DELETE `/remove/{product_id}`, PUT `/update`, GET `/{user_id}` |
| `discount.py` | `/discounts` | POST `/create`, POST `/apply` |
| `checkout.py` | `/checkout` | POST `/` |

### Services

#### `auth_service.py`
```python
def register_user(db: Session, email: str, password: str) -> User
def login_user(db: Session, email: str, password: str) -> User
```

#### `product_service.py`
```python
def create_product(db: Session, data: ProductCreate) -> Product
def get_product(db: Session, product_id: int) -> Product
def get_all_products(db: Session) -> list[Product]
def search_products(db: Session, query: str) -> list[Product]
def filter_by_category(db: Session, category: str) -> list[Product]
```

#### `cart_service.py`
```python
def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int) -> CartItem
def remove_from_cart(db: Session, user_id: int, product_id: int) -> None
def update_cart_item(db: Session, user_id: int, product_id: int, quantity: int) -> CartItem
def get_cart_items(db: Session, user_id: int) -> list[CartItem]
def get_cart_subtotal(db: Session, user_id: int) -> float
```

#### `discount_service.py`
```python
def create_discount(db: Session, data: DiscountCreate) -> Discount
def apply_discount(subtotal: float, discount: Discount) -> float
def calculate_discount_amount(subtotal: float, discount: Discount) -> float
```

#### `checkout_service.py`
```python
TAX_RATE = 0.10  # 10%

def checkout(db: Session, user_id: int, discount_id: int | None = None) -> Order
```

---

## Data Models

### `User`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK, autoincrement |
| email | String | UNIQUE, NOT NULL |
| hashed_password | String | NOT NULL |

### `Product`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK, autoincrement |
| name | String | NOT NULL |
| category | String | NOT NULL |
| price | Float | NOT NULL, > 0 |
| stock | Integer | NOT NULL, >= 0 |
| available | Boolean | NOT NULL, default=True |

### `CartItem`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK, autoincrement |
| user_id | Integer | FK → users.id |
| product_id | Integer | FK → products.id |
| quantity | Integer | NOT NULL, > 0 |

### `Discount`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK, autoincrement |
| code | String | UNIQUE, NOT NULL |
| discount_percent | Float | NOT NULL, 0 < x < 100 |
| min_order_amount | Float | NOT NULL, default=0 |
| max_discount_amount | Float | nullable |

### `Order`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK, autoincrement |
| user_id | Integer | FK → users.id |
| items_snapshot | JSON/Text | NOT NULL |
| subtotal | Float | NOT NULL |
| discount_amount | Float | NOT NULL, default=0 |
| tax_amount | Float | NOT NULL |
| total_amount | Float | NOT NULL |
| created_at | DateTime | NOT NULL, default=now |

### Pydantic Schemas (summary)

Each model has three schema variants:
- `{Entity}Create` — fields accepted on creation (excludes id, server-generated fields)
- `{Entity}Response` — full fields returned to the client
- `{Entity}Update` — partial fields for update operations

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 0: Reflection Notes

After prework analysis, the following consolidations were made.

**Validates: Requirements 1.1, 2.1, 3.4, 3.5, 6.2, 6.5, 7.2, 8.6, 9.1**

- **2.4** (bcrypt comparison invariant) is fully subsumed by **Properties 3 and 4** (correct-password login succeeds; wrong-password login fails). Dropped as redundant.
- **3.4** (available=True when stock>0) and **3.5** (available=False when stock=0) are combined into **Property 6** (availability mirrors stock).
- **7.2** (empty cart subtotal = 0) is a degenerate case of **Property 9** (subtotal formula) — zero items produces zero naturally. Kept as an edge case in unit tests, not as a separate property.
- **9.1** (checkout proceeds for non-empty cart) is covered by the checkout round-trip **Property 14**.
- **6.5** (valid quantity update) is subsumed by **Property 7** (add-to-cart invariant).
- **8.6** (post-discount price formula) is subsumed by **Property 11** (discount arithmetic).

---

### Property 1: Password Hashing on Registration

*For any* valid email and non-empty password, after registering a user the password stored in the database SHALL NOT equal the plaintext password, and bcrypt verification of the plaintext against the stored hash SHALL succeed.

**Validates: Requirements 1.1**

---

### Property 2: Duplicate Registration Rejection

*For any* valid email and password pair, attempting to register a second user with the same email SHALL be rejected (HTTP 400), and the database SHALL still contain exactly one user with that email.

**Validates: Requirements 1.2**

---

### Property 3: Correct-Password Login Succeeds

*For any* registered user with email E and password P, submitting a login request with (E, P) SHALL succeed (HTTP 200).

**Validates: Requirements 2.1, 2.4**

---

### Property 4: Wrong-Password Login Fails

*For any* registered user with email E and password P, and any string W where W ≠ P, submitting a login request with (E, W) SHALL return HTTP 401.

**Validates: Requirements 2.2, 2.4**

---

### Property 5: Product Creation Round-Trip

*For any* valid product payload (name, category, price > 0, stock ≥ 0), creating a product and then retrieving it by ID SHALL return data equivalent to the creation payload.

**Validates: Requirements 3.1, 4.2**

---

### Property 6: Product Availability Mirrors Stock

*For any* product, after creation the availability flag SHALL be True if and only if stock > 0.

**Validates: Requirements 3.4, 3.5, 4.3, 13.3**

---

### Property 7: Invalid Price Rejection

*For any* price value p where p ≤ 0, a product creation request with that price SHALL be rejected (HTTP 400).

**Validates: Requirements 3.2**

---

### Property 8: List Products Returns Only Available

*For any* collection of products with mixed availability, the list-all-products endpoint SHALL return only products whose available flag is True.

**Validates: Requirements 4.1**

---

### Property 9: Case-Insensitive Search

*For any* product with name N and any query string Q such that Q is a substring of N (ignoring case), the search endpoint SHALL include that product in its results.

**Validates: Requirements 5.1**

---

### Property 10: Category Filter Exactness

*For any* category value C and any collection of products, the filter-by-category endpoint SHALL return exactly those products whose category equals C, and no products from other categories.

**Validates: Requirements 5.2**

---

### Property 11: Cart Subtotal Formula

*For any* cart containing N items where item i has unit price pᵢ and quantity qᵢ, the cart subtotal SHALL equal Σ(pᵢ × qᵢ).

**Validates: Requirements 7.1**

---

### Property 12: Invalid Cart Quantity Rejection

*For any* quantity value q where q ≤ 0, an add-to-cart request with that quantity SHALL be rejected (HTTP 400) and the cart SHALL remain unchanged.

**Validates: Requirements 6.2**

---

### Property 13: Discount Arithmetic Correctness

*For any* subtotal S, discount percentage P (0 < P < 100), optional minimum order amount M, and optional maximum cap C: if S ≥ M, the discount amount SHALL equal min(S × P / 100, C) when C is set, or S × P / 100 when C is not set; and the post-discount price SHALL equal S minus the discount amount.

**Validates: Requirements 8.1, 8.2, 8.3, 8.6**

---

### Property 14: Checkout Final Total Formula

*For any* non-empty cart with subtotal S, discount amount D, and tax rate T, the final total persisted in the Order SHALL equal (S − D) + (S − D) × T.

**Validates: Requirements 9.4, 9.5**

---

### Property 15: Stock Decrement After Checkout

*For any* checkout where product i is purchased in quantity qᵢ, after the order is created the stock of product i SHALL equal its pre-checkout stock minus qᵢ.

**Validates: Requirements 9.6**

---

### Property 16: Cart User Isolation

*For any* two distinct users U1 and U2 with different carts, retrieving cart items for U1 SHALL return only U1's items and SHALL NOT include any item belonging to U2.

**Validates: Requirements 6.6, 9.7**

---

## Error Handling

### HTTP Status Code Conventions

| Condition | Status |
|---|---|
| Successful creation | 201 Created |
| Successful retrieval / action | 200 OK |
| Validation failure (Pydantic) | 422 Unprocessable Entity |
| Business rule violation (duplicate user, invalid price, etc.) | 400 Bad Request |
| Resource not found | 404 Not Found |
| Authentication failure (wrong password) | 401 Unauthorized |

### Service-Level Error Strategy

- Services raise `HTTPException` directly (acceptable for a small single-process app).
- No bare `except Exception` blocks — only targeted exceptions are caught.
- Pydantic schemas handle syntactic validation (type, presence); services handle semantic validation (uniqueness, business rules).

### Database Error Strategy

- SQLAlchemy `IntegrityError` is caught in services that perform uniqueness checks and re-raised as HTTP 400.
- All sessions are managed via the `get_db` dependency which guarantees `db.close()` in a `finally` block.

---

## Testing Strategy

### Framework and Configuration

- **pytest** with **pytest-fastapi** (`TestClient` from `starlette.testclient`)
- **Hypothesis** for property-based testing (pure Python, runs 100 iterations per test by default; configured to `max_examples=200` for robustness)
- In-memory SQLite (`sqlite:///:memory:`) for all tests — fast, isolated, zero file-system side effects
- Each test function gets a fresh database via a `db_session` fixture that creates tables before the test and drops them after

### Test File Layout

```
tests/
├── conftest.py               # shared fixtures: app, client, db_session
├── test_auth.py              # Requirements 1, 2
├── test_products.py          # Requirements 3, 4, 5
├── test_cart.py              # Requirements 6, 7
├── test_discount.py          # Requirement 8
├── test_checkout.py          # Requirement 9
├── test_edge_cases.py        # boundary and error conditions across all modules
└── reproduction_tests/
    ├── test_B001.py … test_B020.py
```

### Property Test Configuration

Each property-based test is tagged with a comment header:

```python
# Feature: shopbug, Property N: <property_text>
@given(...)
@settings(max_examples=200)
def test_property_N_title(...):
    ...
```

### Dual Testing Approach

- **Unit / example tests**: verify specific behaviours, exact error codes, edge cases, and cross-module wiring.
- **Property tests**: verify universal correctness across randomly-generated inputs. Each of the 16 correctness properties maps to exactly one property-based test.

### Reproduction Tests

Each `tests/reproduction_tests/test_B{NNN}.py` contains a single test that:
1. Sets up the specific scenario that triggers the bug.
2. Asserts the *expected* (correct) behaviour.
3. On the correct codebase → **PASSES**.
4. On the buggy codebase → **FAILS** with a clear assertion error.

Reproduction tests are deliberately kept separate from the main test suite so researchers can run `pytest tests/reproduction_tests/` independently.

### Bug Injection Protocol

1. Run `pytest tests/` — all tests must pass on the correct codebase.
2. Apply all 20 bug patches in a single commit `"Introduce controlled bugs"`.
3. Run `pytest tests/` again — the main suite should now show failures.
4. Run `pytest tests/reproduction_tests/` — all 20 reproduction tests should fail (confirming each bug is active).
5. Record commit hash in `dataset/bug_dataset.json`.
6. Run `python scripts/validate_dataset.py` — must exit 0.
