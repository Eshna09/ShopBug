# Implementation Plan: ShopBug

## Overview

Implement the ShopBug e-commerce backend in three broad phases:
1. **Correct Implementation** — build all functional components so that all tests pass.
2. **Bug Injection** — introduce exactly 20 intentional bugs in a single commit.
3. **Research Dataset** — produce the ground-truth JSON/CSV/Markdown artefacts and validation script.

All code is Python 3.11+, FastAPI, SQLAlchemy (SQLite), Pydantic v2, pytest, and Hypothesis.

---

## Tasks

- [ ] 1. Project scaffold and infrastructure
  - Create the full directory tree: `app/`, `app/models/`, `app/schemas/`, `app/routes/`, `app/services/`, `tests/`, `tests/reproduction_tests/`, `dataset/`, `dataset/bug_reports/`, `scripts/`
  - Create `app/__init__.py`, `app/models/__init__.py`, `app/schemas/__init__.py`, `app/routes/__init__.py`, `app/services/__init__.py`
  - Write `requirements.txt` with pinned versions: fastapi, uvicorn, sqlalchemy, pydantic, python-dotenv, passlib[bcrypt], pytest, pytest-asyncio, httpx, hypothesis
  - Write `.env.example` documenting `DATABASE_URL` and `TAX_RATE`
  - Write `.gitignore` excluding `__pycache__/`, `*.pyc`, `*.db`, `.env`, `venv/`, `.pytest_cache/`
  - Write `app/database.py`: SQLAlchemy engine, `SessionLocal`, `Base`, `get_db` dependency, `init_db()`
  - Write `app/main.py`: create FastAPI app, call `init_db()` on startup, register all five routers (stubs at this point)
  - Initialise git and make commit: "Initial project setup"
  - _Requirements: 13.1, 13.2, 13.4, 13.5_

- [ ] 2. Authentication — models, schemas, service, routes
  - [ ] 2.1 Write `app/models/user.py`: `User` SQLAlchemy model (id, email UNIQUE, hashed_password)
    - _Requirements: 1.1_
  - [ ] 2.2 Write `app/schemas/user.py`: `UserCreate` (email, password), `UserResponse` (id, email), `LoginRequest` (email, password)
    - _Requirements: 1.3, 1.4_
  - [ ] 2.3 Write `app/services/auth_service.py`: `register_user` (hash password with bcrypt, check duplicate → HTTP 400), `login_user` (look up email → 404 if missing, bcrypt verify → 401 if wrong)
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3, 2.4_
  - [ ] 2.4 Write `app/routes/auth.py`: `POST /register` and `POST /login` endpoints wired to service functions
    - _Requirements: 1.1, 2.1_
  - [ ]* 2.5 Write `tests/test_auth.py` — example tests: register succeeds, duplicate email → 400, wrong password → 401, missing email → 422
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3_
  - [ ]* 2.6 Write property tests for auth in `tests/test_auth.py`
    - **Property 1: Password Hashing on Registration** — `@given(email=emails(), password=text(min_size=1))` — verify stored hash ≠ plaintext and bcrypt.checkpw succeeds
    - **Property 2: Duplicate Registration Rejection** — `@given(email=emails(), password=text(min_size=1))` — register once, register again → 400, DB has exactly one user
    - **Property 3: Correct-Password Login Succeeds** — `@given(...)` — register then login with same password → 200
    - **Property 4: Wrong-Password Login Fails** — `@given(...)` — register with P, login with W ≠ P → 401
    - **Validates: Requirements 1.1, 1.2, 2.1, 2.2, 2.4**
  - Commit: "Implement authentication"

- [ ] 3. Product management — models, schemas, service, routes
  - [ ] 3.1 Write `app/models/product.py`: `Product` SQLAlchemy model (id, name, category, price, stock, available)
    - _Requirements: 3.1, 3.4, 3.5_
  - [ ] 3.2 Write `app/schemas/product.py`: `ProductCreate`, `ProductResponse`, `ProductUpdate`
    - _Requirements: 3.2, 3.3_
  - [ ] 3.3 Write `app/services/product_service.py`: `create_product` (validate price > 0 → 400, stock ≥ 0 → 400, set available = stock > 0), `get_product` (404 if missing), `get_all_products` (filter available=True only), `search_products` (case-insensitive `.ilike()`), `filter_by_category` (exact match `==`)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 5.1, 5.2, 5.3_
  - [ ] 3.4 Write `app/routes/products.py`: `POST /`, `GET /`, `GET /{id}`, `GET /search?q=`, `GET /filter?category=`
    - _Requirements: 4.1, 4.2, 5.1, 5.2_
  - [ ]* 3.5 Write `tests/test_products.py` — example tests: create valid product, create with price=0 → 400, create with negative price → 400, get non-existent → 404, list returns only available, filter by category returns correct set
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 5.2, 5.3_
  - [ ]* 3.6 Write property tests for products in `tests/test_products.py`
    - **Property 5: Product Creation Round-Trip** — `@given(valid_product_payload())` — create then get-by-id returns same data
    - **Property 6: Product Availability Mirrors Stock** — `@given(stock=integers(min_value=0))` — available == (stock > 0)
    - **Property 7: Invalid Price Rejection** — `@given(price=one_of(just(0), floats(max_value=-0.01)))` — price ≤ 0 → 400
    - **Property 8: List Products Returns Only Available** — `@given(products=lists(product_strategy()))` — list endpoint only returns available products
    - **Property 9: Case-Insensitive Search** — `@given(name=text(min_size=1), query=...)` — search with varied case finds the product
    - **Property 10: Category Filter Exactness** — `@given(category=text(), products=lists(...))` — filter returns exactly matching category
    - **Validates: Requirements 3.1, 3.2, 3.4, 3.5, 4.1, 4.2, 5.1, 5.2**
  - Commit: "Implement product management"

- [ ] 4. Shopping cart — models, schemas, service, routes
  - [ ] 4.1 Write `app/models/cart.py`: `CartItem` SQLAlchemy model (id, user_id FK, product_id FK, quantity)
    - _Requirements: 6.1_
  - [ ] 4.2 Write `app/schemas/cart.py`: `CartItemCreate`, `CartItemResponse`, `CartItemUpdate`
    - _Requirements: 6.2, 6.3_
  - [ ] 4.3 Write `app/services/cart_service.py`:
    - `add_to_cart`: validate quantity > 0 → 400, validate quantity ≤ product.stock → 400, upsert CartItem
    - `remove_from_cart`: delete CartItem (404 if not found)
    - `update_cart_item`: same validations as add, update quantity
    - `get_cart_items(db, user_id)`: query CartItem filtered by user_id
    - `get_cart_subtotal(db, user_id)`: sum(item.product.price × item.quantity)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 7.1, 7.2_
  - [ ] 4.4 Write `app/routes/cart.py`: `POST /add`, `DELETE /remove/{product_id}`, `PUT /update`, `GET /{user_id}`
    - _Requirements: 6.1, 6.4, 6.6_
  - [ ]* 4.5 Write `tests/test_cart.py` — example tests: add item succeeds, add with quantity=0 → 400, add exceeding stock → 400, remove item, empty cart subtotal = 0
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 7.2_
  - [ ]* 4.6 Write property tests for cart in `tests/test_cart.py`
    - **Property 11: Cart Subtotal Formula** — `@given(items=lists(cart_item_strategy(), min_size=1))` — subtotal == Σ(price × quantity)
    - **Property 12: Invalid Cart Quantity Rejection** — `@given(quantity=one_of(just(0), integers(max_value=-1)))` — quantity ≤ 0 → 400, cart unchanged
    - **Property 16: Cart User Isolation** — `@given(user1_items=..., user2_items=...)` — each user's cart returns only their own items
    - **Validates: Requirements 6.2, 6.6, 7.1**
  - Commit: "Implement shopping cart"

- [ ] 5. Discount system — models, schemas, service, routes
  - [ ] 5.1 Write `app/models/order.py` (needed for discount relationship): `Discount` and `Order` SQLAlchemy models
    - Discount: id, code UNIQUE, discount_percent, min_order_amount, max_discount_amount (nullable)
    - Order: id, user_id FK, items_snapshot (Text/JSON), subtotal, discount_amount, tax_amount, total_amount, created_at
    - _Requirements: 8.1, 9.5_
  - [ ] 5.2 Write `app/schemas/order.py`: `DiscountCreate`, `DiscountResponse`, `OrderResponse`
    - _Requirements: 8.4, 8.5_
  - [ ] 5.3 Write `app/services/discount_service.py`:
    - `create_discount`: validate 0 < discount_percent < 100 → 400 otherwise
    - `calculate_discount_amount(subtotal, discount)`: if subtotal < min_order_amount return 0; else raw = subtotal × percent / 100; if max_discount_amount is set and raw > max_discount_amount return max_discount_amount; else return raw
    - `apply_discount(subtotal, discount)`: return subtotal − calculate_discount_amount(subtotal, discount)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_
  - [ ] 5.4 Write `app/routes/discount.py`: `POST /create`, `POST /apply`
    - _Requirements: 8.1, 8.4_
  - [ ]* 5.5 Write `tests/test_discount.py` — example tests: 20% off ₹1000 → ₹800, cap enforcement, subtotal below minimum → no discount, 100% → 400, negative → 400
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  - [ ]* 5.6 Write property tests for discount in `tests/test_discount.py`
    - **Property 13: Discount Arithmetic Correctness** — `@given(subtotal=floats(min_value=0.01), percent=floats(min_value=0.01, max_value=99.99), ...)` — verify discount_amount == min(subtotal×percent/100, cap) and post-discount price == subtotal − discount_amount
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.6**
  - Commit: "Implement discount system"

- [ ] 6. Checkout — service and routes
  - [ ] 6.1 Write `app/services/checkout_service.py`:
    - `checkout(db, user_id, discount_id=None)`:
      1. `items = cart_service.get_cart_items(db, user_id)` — must pass user_id
      2. If no items → HTTP 400
      3. Validate each item's product.stock ≥ item.quantity → 400 if not
      4. `subtotal = cart_service.get_cart_subtotal(db, user_id)`
      5. If discount_id provided: fetch Discount, `discount_amount = discount_service.calculate_discount_amount(subtotal, discount)`; else discount_amount = 0
      6. `post_discount = subtotal − discount_amount`
      7. `tax_amount = post_discount × TAX_RATE`
      8. `total_amount = post_discount + tax_amount`
      9. Persist Order with all fields including `total_amount`
      10. Decrement `product.stock -= item.quantity` for each item; set `product.available = product.stock > 0`
      11. Return created Order
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_
  - [ ] 6.2 Write `app/routes/checkout.py`: `POST /checkout` wired to service
    - _Requirements: 9.1_
  - [ ]* 6.3 Write `tests/test_checkout.py` — example tests: full happy-path (item in cart, discount applied, correct total), empty cart → 400, insufficient stock → 400
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  - [ ]* 6.4 Write property tests for checkout in `tests/test_checkout.py`
    - **Property 14: Checkout Final Total Formula** — `@given(subtotal=..., discount_percent=..., tax_rate=just(0.10))` — total == post_discount × (1 + TAX_RATE)
    - **Property 15: Stock Decrement After Checkout** — `@given(stock=integers(min_value=1), quantity=...)` — stock after == stock before − quantity
    - **Validates: Requirements 9.4, 9.5, 9.6**
  - Commit: "Implement checkout"

- [ ] 7. Edge-case and cross-module test suite
  - [ ] 7.1 Write `tests/test_edge_cases.py` covering: product with stock=0 unavailable, cart-item quantity exceeds stock, discount at exactly minimum order amount boundary (≥ should apply, < should not), discount cap exactly equal to computed discount, checkout with mixed stock items
    - _Requirements: 3.5, 6.3, 8.2, 8.3, 9.3_
  - [ ] 7.2 Write `tests/conftest.py`: shared fixtures — `test_app`, `client` (TestClient with in-memory SQLite override), `db_session`, helper factories (`make_user`, `make_product`, `make_cart_item`, `make_discount`)
  - Commit: "Add test suite"

- [ ] 8. Checkpoint — all tests must pass before bugs are introduced
  - Run `pytest tests/ -v` and ensure zero failures. Resolve any failures before proceeding.

- [ ] 9. Introduce the 20 intentional bugs
  - [ ] 9.1 Apply B001 in `app/services/discount_service.py` — change post-discount price formula so result is `price * rate` instead of `price * (1 - rate)` (arithmetic, easy)
    - _Bug ID: B001_
  - [ ] 9.2 Apply B002 in `app/services/checkout_service.py` — calculate tax on pre-discount subtotal instead of post-discount subtotal (arithmetic, medium)
    - _Bug ID: B002_
  - [ ] 9.3 Apply B003 in `app/services/auth_service.py` — reverse the password-verification condition so login succeeds on mismatch (logic, easy)
    - _Bug ID: B003_
  - [ ] 9.4 Apply B004 in `app/services/cart_service.py` — change quantity validation from `quantity <= 0` to `quantity < 0`, allowing zero-quantity items (boundary, easy)
    - _Bug ID: B004_
  - [ ] 9.5 Apply B005 in `app/services/product_service.py` — remove the `price > 0` guard, accepting negative prices (input_validation, easy)
    - _Bug ID: B005_
  - [ ] 9.6 Apply B006 in `app/services/product_service.py` — change `.ilike(f"%{query}%")` to `== query` in search, making search case-sensitive and exact (search_filter, medium)
    - _Bug ID: B006_
  - [ ] 9.7 Apply B007 in `app/services/product_service.py` — change `available == True` to `available == False` in `get_all_products`, returning only unavailable products (data_handling, medium)
    - _Bug ID: B007_
  - [ ] 9.8 Apply B008 in `app/services/discount_service.py` — change `subtotal < min_order_amount` to `subtotal <= min_order_amount`, so a cart equal to the minimum does not get the discount (boundary, medium)
    - _Bug ID: B008_
  - [ ] 9.9 Apply B009 in `app/services/cart_service.py` — change `product.price` to `product.stock` in the subtotal calculation (arithmetic, hard)
    - _Bug ID: B009_
  - [ ] 9.10 Apply B010 in `app/services/checkout_service.py` — invert the empty-cart guard so it rejects non-empty carts and allows empty carts through (logic, medium)
    - _Bug ID: B010_
  - [ ] 9.11 Apply B011 in `app/services/auth_service.py` — remove the duplicate-email existence check before inserting a new user (authentication, easy)
    - _Bug ID: B011_
  - [ ] 9.12 Apply B012 in `app/services/checkout_service.py` — call `get_cart_items(db)` without the `user_id` argument (dependency, hard)
    - _Bug ID: B012_
  - [ ] 9.13 Apply B013 in `app/services/product_service.py` — change `stock > 0` to `stock >= 0` in availability assignment, marking zero-stock products as available (edge_case, medium)
    - _Bug ID: B013_
  - [ ] 9.14 Apply B014 in `app/services/discount_service.py` — apply the max-cap check before computing the percentage (comparing `subtotal` against cap instead of computed amount), neutering the cap (logic, hard)
    - _Bug ID: B014_
  - [ ] 9.15 Apply B015 in `app/services/cart_service.py` — remove the `quantity > product.stock` stock-check when adding to cart (input_validation, medium)
    - _Bug ID: B015_
  - [ ] 9.16 Apply B016 in `app/services/checkout_service.py` — set `order.total_amount = subtotal` (ignoring discount and tax when persisting) (data_handling, hard)
    - _Bug ID: B016_
  - [ ] 9.17 Apply B017 in `app/services/product_service.py` — change `category == requested_category` to `category != requested_category` in `filter_by_category` (search_filter, medium)
    - _Bug ID: B017_
  - [ ] 9.18 Apply B018 in `app/services/discount_service.py` — change validation from `discount_percent >= 100` to `discount_percent > 100`, allowing 100% discount through (boundary, hard)
    - _Bug ID: B018_
  - [ ] 9.19 Apply B019 in `app/services/checkout_service.py` — remove or comment out the stock-decrement block after order creation (multi_interaction, hard)
    - _Bug ID: B019_
  - [ ] 9.20 Apply B020 in `app/services/auth_service.py` — replace bcrypt hash storage with plaintext (or a fixed-salt hash), breaking password verification after any hash mismatch (logic, easy)
    - _Bug ID: B020_
  - Commit: "Introduce controlled bugs"

- [ ] 10. Write reproduction tests
  - [ ] 10.1 Write `tests/reproduction_tests/test_B001.py` — apply 20% discount to ₹1000, assert result == 800 (not 200)
    - _Bug ID: B001, Requirements: 8.1, 8.6_
  - [ ] 10.2 Write `tests/reproduction_tests/test_B002.py` — apply discount then check tax is on post-discount amount
    - _Bug ID: B002, Requirements: 9.4_
  - [ ] 10.3 Write `tests/reproduction_tests/test_B003.py` — register with password "correct", login with "wrong" should fail (401), login with "correct" should succeed (200)
    - _Bug ID: B003, Requirements: 2.1, 2.2_
  - [ ] 10.4 Write `tests/reproduction_tests/test_B004.py` — add product with quantity=0, assert HTTP 400 is returned
    - _Bug ID: B004, Requirements: 6.2_
  - [ ] 10.5 Write `tests/reproduction_tests/test_B005.py` — create product with price=-10, assert HTTP 400
    - _Bug ID: B005, Requirements: 3.2_
  - [ ] 10.6 Write `tests/reproduction_tests/test_B006.py` — create product "Laptop", search "laptop", assert product appears in results
    - _Bug ID: B006, Requirements: 5.1_
  - [ ] 10.7 Write `tests/reproduction_tests/test_B007.py` — create available product, call list-products, assert it appears
    - _Bug ID: B007, Requirements: 4.1_
  - [ ] 10.8 Write `tests/reproduction_tests/test_B008.py` — set min_order=500, apply discount to cart of exactly 500, assert discount is applied
    - _Bug ID: B008, Requirements: 8.3_
  - [ ] 10.9 Write `tests/reproduction_tests/test_B009.py` — add product (price=100, stock=5) qty=2 to cart, assert subtotal == 200 (not 10)
    - _Bug ID: B009, Requirements: 7.1_
  - [ ] 10.10 Write `tests/reproduction_tests/test_B010.py` — checkout with non-empty cart should succeed, not return 400
    - _Bug ID: B010, Requirements: 9.1_
  - [ ] 10.11 Write `tests/reproduction_tests/test_B011.py` — register same email twice, assert second call returns 400
    - _Bug ID: B011, Requirements: 1.2_
  - [ ] 10.12 Write `tests/reproduction_tests/test_B012.py` — user A and user B have different carts; checkout as user A; order should reflect user A's items
    - _Bug ID: B012, Requirements: 9.7_
  - [ ] 10.13 Write `tests/reproduction_tests/test_B013.py` — create product with stock=0, assert available==False
    - _Bug ID: B013, Requirements: 3.5_
  - [ ] 10.14 Write `tests/reproduction_tests/test_B014.py` — compute discount where percent would exceed cap; assert returned discount == cap
    - _Bug ID: B014, Requirements: 8.2_
  - [ ] 10.15 Write `tests/reproduction_tests/test_B015.py` — add quantity > stock to cart, assert HTTP 400
    - _Bug ID: B015, Requirements: 6.3_
  - [ ] 10.16 Write `tests/reproduction_tests/test_B016.py` — checkout with discount+tax, assert order.total_amount == final total (not subtotal)
    - _Bug ID: B016, Requirements: 9.5_
  - [ ] 10.17 Write `tests/reproduction_tests/test_B017.py` — create Electronics and Books products, filter by Electronics, assert only Electronics returned
    - _Bug ID: B017, Requirements: 5.2_
  - [ ] 10.18 Write `tests/reproduction_tests/test_B018.py` — create discount with percent=100, assert HTTP 400
    - _Bug ID: B018, Requirements: 8.4_
  - [ ] 10.19 Write `tests/reproduction_tests/test_B019.py` — checkout product with stock=5 qty=2, assert stock is 3 after checkout
    - _Bug ID: B019, Requirements: 9.6_
  - [ ] 10.20 Write `tests/reproduction_tests/test_B020.py` — register with password "abc", call login with password "abc", assert 200 (not 401)
    - _Bug ID: B020, Requirements: 2.1_

- [ ] 11. Build the ground-truth research dataset
  - [ ] 11.1 Write `dataset/bug_dataset.json` containing all 20 bug records with fields: bug_id, category, difficulty, issue_report_quality, issue_report, expected_behavior, actual_behavior, root_cause_file, root_cause_function, root_cause_lines, affected_files, root_cause_description, reproduction_steps, reproduction_test, commit_hash (set to "TBD" initially)
    - _Requirements: 11.1, 11.2_
  - [ ] 11.2 Write `dataset/bug_dataset.csv` with the same 20 records (flat representation, lists as semicolon-separated strings)
    - _Requirements: 11.2_
  - [ ] 11.3 Write individual bug report Markdown files `dataset/bug_reports/B001.md` through `dataset/bug_reports/B020.md`, each containing: Bug ID, Category, Difficulty, Issue Report Quality, Issue Report, Expected Behavior, Actual Behavior, Root Cause Description, Reproduction Steps
    - _Requirements: 11.3_
  - [ ] 11.4 Write `BUG_DATASET.md` top-level summary: schema description, distribution tables (by category, difficulty, quality, scope), how to use the dataset
    - _Requirements: 11.4_
  - [ ] 11.5 Write `dataset/README.md` explaining the dataset structure and how researchers should use it
    - _Requirements: 11.4_
  - Commit: "Prepare research dataset"

- [ ] 12. Validation script
  - [ ] 12.1 Write `scripts/validate_dataset.py`:
    - Load `dataset/bug_dataset.json` and parse CSV from `dataset/bug_dataset.csv`
    - Check all bug_ids are unique
    - Check each record has non-empty: issue_report, category, difficulty, root_cause_file, root_cause_function
    - Check each root_cause_file exists on disk
    - Check each reproduction_test file exists on disk
    - Check JSON and CSV contain the same set of bug_ids
    - Print pass/fail per check; exit non-zero on any failure
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_
  - [ ]* 12.2 Write unit tests for validate_dataset.py in `tests/test_edge_cases.py`: crafted valid dataset passes, missing file fails, duplicate ID fails, JSON/CSV mismatch fails
    - _Requirements: 12.1, 12.3, 12.4, 12.5, 12.6_

- [ ] 13. Final checkpoint — run full test suite and validator
  - Run `pytest tests/ -v` on the correct codebase (before bug injection) — assert zero failures.
  - Run `pytest tests/reproduction_tests/ -v` on the correct codebase — all 20 reproduction tests should PASS (they assert correct behaviour).
  - After bug injection commit, run `pytest tests/reproduction_tests/ -v` — all 20 should FAIL (confirming bugs are active).
  - Run `python scripts/validate_dataset.py` — must exit 0.
  - Write `README.md` with setup instructions, how to run the server (`uvicorn app.main:app`), how to run the tests, and a description of the dataset without revealing bug locations.
  - Ensure all tests pass, ask the user if questions arise.
  - _Requirements: 13.3, 10.1_

---

## Task Dependency Graph

```json
{
  "waves": [
    {"wave": 1, "tasks": ["1"]},
    {"wave": 2, "tasks": ["2"]},
    {"wave": 3, "tasks": ["3"]},
    {"wave": 4, "tasks": ["4"]},
    {"wave": 5, "tasks": ["5"]},
    {"wave": 6, "tasks": ["6"]},
    {"wave": 7, "tasks": ["7", "8"]},
    {"wave": 8, "tasks": ["9"]},
    {"wave": 9, "tasks": ["10", "11"]},
    {"wave": 10, "tasks": ["12", "13"]}
  ]
}
```

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Checkpoints (tasks 8 and 13) ensure incremental validation
- Property tests use **Hypothesis** (`@given` / `@settings(max_examples=200)`) — tagged with `# Feature: shopbug, Property N: <text>`
- Reproduction tests are self-contained; they must not import each other
- Bug changes must be minimal, natural-looking, and non-commenting — one or two characters changed per bug is ideal
- The `commit_hash` field in `dataset/bug_dataset.json` should be updated after the bug-injection commit is made
