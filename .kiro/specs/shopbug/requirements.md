# Requirements Document

## Introduction

ShopBug is a controlled, intentionally-buggy e-commerce backend built with Python, FastAPI, and SQLite. The system serves two purposes: (1) a functional e-commerce API covering user authentication, product management, shopping cart, discount application, and checkout; and (2) a research platform that, after an initial correct implementation, receives exactly 20 carefully-designed software bugs so that AI bug-localization systems can be evaluated against a ground-truth dataset.

The project is structured so the correct implementation passes all tests before any bugs are introduced. Bugs are then injected in a single commit, each recorded in a structured ground-truth dataset. Code must look natural at all times — no markers, no revealing names, no syntactically invalid constructs.

## Glossary

- **User**: A registered account identified by a unique email address and a hashed password.
- **Product**: A catalogue item with a name, category, price, stock count, and availability flag.
- **Cart**: A per-user collection of CartItems linking a Product to a quantity.
- **CartItem**: A single line in a Cart associating one Product with a non-zero positive quantity.
- **Discount**: A promotional rule defined by a percentage, an optional minimum order amount, and an optional maximum discount cap.
- **Order**: A completed purchase record storing the user, a snapshot of items, and the final total after discount and tax.
- **Subtotal**: The sum of (unit_price × quantity) for all CartItems in a Cart.
- **Tax**: A fixed percentage applied to the post-discount subtotal.
- **Final Total**: subtotal − discount_amount + tax_amount.
- **Bug**: An intentional, syntactically-valid but behaviourally-incorrect code change introduced after the correct implementation is verified.
- **Reproduction Test**: An automated pytest test that fails on the buggy implementation and passes on the correct implementation for a specific Bug.
- **Ground-Truth Dataset**: The structured record (JSON, CSV, per-bug Markdown) that maps each Bug to its root cause, affected files, and reproduction test.
- **System**: The ShopBug FastAPI application.
- **Auth_Service**: The authentication service component.
- **Product_Service**: The product management service component.
- **Cart_Service**: The shopping cart service component.
- **Discount_Service**: The discount calculation service component.
- **Checkout_Service**: The checkout and order finalisation service component.
- **Validator**: The dataset validation script.

---

## Requirements

### Requirement 1: User Registration

**User Story:** As a new visitor, I want to register an account with my email and password, so that I can make purchases on the platform.

#### Acceptance Criteria

1. WHEN a registration request is received with a unique email and a non-empty password, THE Auth_Service SHALL create a new User record with the password stored as a bcrypt hash.
2. WHEN a registration request is received with an email that already exists in the database, THE Auth_Service SHALL reject the request and return an HTTP 400 error with a descriptive message.
3. WHEN a registration request is received with an empty or missing email, THE Auth_Service SHALL reject the request and return an HTTP 422 validation error.
4. WHEN a registration request is received with an empty or missing password, THE Auth_Service SHALL reject the request and return an HTTP 422 validation error.

---

### Requirement 2: User Login

**User Story:** As a registered user, I want to log in with my email and password, so that I can access my cart and place orders.

#### Acceptance Criteria

1. WHEN a login request is received with a valid email and the correct password, THE Auth_Service SHALL return an HTTP 200 response confirming authentication success.
2. WHEN a login request is received with a valid email and an incorrect password, THE Auth_Service SHALL return an HTTP 401 error.
3. WHEN a login request is received with an email that does not exist, THE Auth_Service SHALL return an HTTP 404 error.
4. THE Auth_Service SHALL compare the provided password against the stored bcrypt hash and SHALL grant access only when the comparison succeeds.

---

### Requirement 3: Product Creation

**User Story:** As an administrator, I want to create products with a name, category, price, and stock level, so that customers can browse and purchase them.

#### Acceptance Criteria

1. WHEN a product creation request is received with valid fields, THE Product_Service SHALL persist the product and return the created product record.
2. WHEN a product creation request is received with a price that is zero or negative, THE Product_Service SHALL reject the request and return an HTTP 400 error.
3. WHEN a product creation request is received with a stock value that is negative, THE Product_Service SHALL reject the request and return an HTTP 400 error.
4. WHEN a product is created with a stock value greater than zero, THE Product_Service SHALL set the product's availability flag to true.
5. WHEN a product is created with a stock value of zero, THE Product_Service SHALL set the product's availability flag to false.

---

### Requirement 4: Product Retrieval

**User Story:** As a customer, I want to browse available products and retrieve product details, so that I can decide what to buy.

#### Acceptance Criteria

1. WHEN a request is made to list all products, THE Product_Service SHALL return only products whose availability flag is true.
2. WHEN a request is made to retrieve a product by its ID and the product exists, THE Product_Service SHALL return that product's full details.
3. WHEN a request is made to retrieve a product by its ID and the product does not exist, THE Product_Service SHALL return an HTTP 404 error.

---

### Requirement 5: Product Search and Filter

**User Story:** As a customer, I want to search for products by name and filter by category, so that I can quickly find what I am looking for.

#### Acceptance Criteria

1. WHEN a search request is received with a query string, THE Product_Service SHALL return all products whose name contains the query string in a case-insensitive manner.
2. WHEN a filter request is received with a category name, THE Product_Service SHALL return only products whose category exactly matches the requested category.
3. WHEN a search or filter request matches no products, THE Product_Service SHALL return an empty list.

---

### Requirement 6: Cart Management

**User Story:** As a customer, I want to add, update, and remove items in my cart, so that I can prepare my order before checkout.

#### Acceptance Criteria

1. WHEN a request is received to add a product to a cart with a positive integer quantity, THE Cart_Service SHALL create or update the CartItem for that user and product.
2. WHEN a request is received to add a product to a cart with a quantity of zero or less, THE Cart_Service SHALL reject the request and return an HTTP 400 error.
3. WHEN a request is received to add a product to a cart with a quantity that exceeds the product's available stock, THE Cart_Service SHALL reject the request and return an HTTP 400 error.
4. WHEN a request is received to remove a product from a cart, THE Cart_Service SHALL delete the associated CartItem.
5. WHEN a request is received to update the quantity of a CartItem, THE Cart_Service SHALL update the quantity if it is positive and does not exceed stock.
6. WHEN a request is received to retrieve cart items for a user, THE Cart_Service SHALL return all CartItems belonging to that user.

---

### Requirement 7: Cart Subtotal Calculation

**User Story:** As a customer, I want to see the subtotal of my cart, so that I know how much I will spend before discounts and tax.

#### Acceptance Criteria

1. WHEN the subtotal of a cart is requested, THE Cart_Service SHALL compute it as the sum of (product.price × cartitem.quantity) for each CartItem.
2. WHEN the cart contains no items, THE Cart_Service SHALL return a subtotal of zero.

---

### Requirement 8: Discount Application

**User Story:** As a customer, I want to apply a discount code to my cart, so that I can receive a price reduction.

#### Acceptance Criteria

1. WHEN a discount is applied to an order subtotal and the subtotal meets the minimum order amount, THE Discount_Service SHALL compute the discount amount as (subtotal × discount_percent / 100).
2. WHEN the computed discount amount exceeds the maximum discount cap, THE Discount_Service SHALL limit the discount amount to the maximum cap value.
3. WHEN the order subtotal is below the minimum order amount, THE Discount_Service SHALL apply no discount and return zero.
4. WHEN a discount with a percentage of 100 or greater is submitted, THE Discount_Service SHALL reject it and return an HTTP 400 error.
5. WHEN a discount with a negative percentage is submitted, THE Discount_Service SHALL reject it and return an HTTP 400 error.
6. WHEN a discount is applied, THE Discount_Service SHALL apply the discount percentage to the current subtotal, and the result SHALL be the post-discount price (subtotal minus discount amount).

---

### Requirement 9: Checkout and Order Creation

**User Story:** As a customer, I want to check out my cart to create an order with the correct final total, so that my purchase is recorded.

#### Acceptance Criteria

1. WHEN a checkout request is received for a cart with at least one item, THE Checkout_Service SHALL proceed with order creation.
2. WHEN a checkout request is received for an empty cart, THE Checkout_Service SHALL reject the request and return an HTTP 400 error.
3. WHEN a checkout request is received and a product in the cart has insufficient stock, THE Checkout_Service SHALL reject the request and return an HTTP 400 error.
4. WHEN an order is created, THE Checkout_Service SHALL compute the final total as: (subtotal − discount_amount) + tax_amount, where tax is applied to the post-discount subtotal.
5. WHEN an order is created, THE Checkout_Service SHALL persist the Order with the final total (subtotal − discount + tax) as the stored total_amount.
6. WHEN an order is created successfully, THE Checkout_Service SHALL decrement the stock of each purchased product by the purchased quantity.
7. WHEN an order is created, THE Checkout_Service SHALL pass the correct user's cart items to the order creation logic.

---

### Requirement 10: Intentional Bug Injection

**User Story:** As a researcher, I want exactly 20 intentional bugs injected after a verified correct implementation, so that I can evaluate AI bug-localization systems against a known ground truth.

#### Acceptance Criteria

1. THE System SHALL pass all automated tests before any bugs are introduced.
2. WHEN bugs are introduced, THE System SHALL contain exactly 20 bugs distributed across the categories: arithmetic, logic, boundary, input_validation, search_filter, data_handling, dependency, authentication, multi_interaction, and edge_case.
3. WHEN bugs are introduced, THE System SHALL contain exactly 6 easy, 8 medium, and 6 hard bugs as defined in the bug specification.
4. WHEN bugs are introduced, each bug SHALL be syntactically valid Python code that compiles without errors.
5. WHEN bugs are introduced, no source file, comment, or identifier SHALL contain markers such as "BUG", "buggy", or "intentional" that reveal the bug location.
6. WHEN bugs are introduced, each bug SHALL be independent of other bugs where possible, so that fixing one bug does not mask another.

---

### Requirement 11: Ground-Truth Dataset

**User Story:** As a researcher, I want a structured ground-truth dataset for each bug, so that I can measure how accurately an AI system localises bugs.

#### Acceptance Criteria

1. THE System SHALL provide a ground-truth record for each of the 20 bugs containing: bug_id, category, difficulty, issue_report_quality, issue_report, expected_behavior, actual_behavior, root_cause_file, root_cause_function, root_cause_lines, affected_files, root_cause_description, reproduction_steps, reproduction_test, and commit_hash.
2. THE System SHALL export the ground-truth dataset as both a JSON file at `dataset/bug_dataset.json` and a CSV file at `dataset/bug_dataset.csv`.
3. FOR EACH bug, THE System SHALL provide an individual Markdown bug report at `dataset/bug_reports/B{NNN}.md`.
4. THE System SHALL provide a top-level `BUG_DATASET.md` summary file describing the dataset schema and distribution.
5. FOR EACH bug, THE System SHALL provide a reproduction test at `tests/reproduction_tests/test_B{NNN}.py` that fails on the buggy implementation and passes on the correct implementation.

---

### Requirement 12: Dataset Validation

**User Story:** As a researcher, I want a validation script to verify the dataset's integrity, so that I can confirm it is complete and consistent before publishing.

#### Acceptance Criteria

1. WHEN the validation script is executed, THE Validator SHALL verify that every bug record has a unique bug_id.
2. WHEN the validation script is executed, THE Validator SHALL verify that every bug record contains a non-empty issue_report, category, difficulty, root_cause_file, and root_cause_function.
3. WHEN the validation script is executed, THE Validator SHALL verify that every root_cause_file listed in the dataset exists on disk.
4. WHEN the validation script is executed, THE Validator SHALL verify that every reproduction_test file listed in the dataset exists on disk.
5. WHEN the validation script is executed, THE Validator SHALL verify that the JSON and CSV exports contain the same set of bug IDs.
6. IF any validation check fails, THEN THE Validator SHALL print a descriptive error message identifying the failing bug_id and the failed check, and exit with a non-zero status code.
7. WHEN all validation checks pass, THE Validator SHALL print a confirmation message and exit with status code zero.

---

### Requirement 13: Project Infrastructure

**User Story:** As a developer or researcher, I want a clean, documented project structure with reproducible setup, so that I can run the application and tests reliably.

#### Acceptance Criteria

1. THE System SHALL provide a `requirements.txt` listing all dependencies with pinned versions.
2. THE System SHALL provide a `.env.example` file documenting all required environment variables.
3. THE System SHALL provide a `README.md` describing project setup, how to run the server, and how to run the tests without revealing bug locations.
4. THE System SHALL provide a `.gitignore` excluding Python bytecode, virtual environments, SQLite database files, and `.env` files.
5. THE System SHALL be committed to git following the prescribed commit sequence: "Initial project setup", "Implement authentication", "Implement product management", "Implement shopping cart", "Implement discount system", "Implement checkout", "Add test suite", "Introduce controlled bugs", "Prepare research dataset".
