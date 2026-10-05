# ShopBug

A small e-commerce backend API built with FastAPI, SQLAlchemy, and SQLite. Provides user authentication, product management, shopping cart, discount system, and checkout functionality.

## Technology Stack

- **Python 3.11+**
- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **SQLite** — database
- **Pydantic** — data validation
- **passlib[bcrypt]** — password hashing
- **pytest** + **Hypothesis** — testing

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/shopbug.git
cd shopbug

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Copy the example environment file and adjust as needed:

```bash
cp .env.example .env
```

Environment variables:
- `DATABASE_URL` — SQLite database path (default: `sqlite:///./shopbug.db`)
- `TAX_RATE` — Tax rate applied at checkout (default: `0.10` = 10%)

## Running the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## API Endpoints

### Authentication (`/auth`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login with email and password |

### Products (`/products`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/products/` | Create a product |
| GET | `/products/` | List all available products |
| GET | `/products/{id}` | Get product by ID |
| GET | `/products/search?q=` | Search products by name (case-insensitive) |
| GET | `/products/filter?category=` | Filter products by category |

### Cart (`/cart`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/cart/add` | Add item to cart |
| DELETE | `/cart/remove/{product_id}?user_id=` | Remove item from cart |
| PUT | `/cart/update` | Update cart item quantity |
| GET | `/cart/{user_id}` | Get cart items for a user |

### Discounts (`/discounts`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/discounts/create` | Create a discount code |
| POST | `/discounts/apply` | Apply a discount to a subtotal |

### Checkout (`/checkout`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/checkout/?user_id=&discount_id=` | Checkout and create an order |

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run only unit and integration tests
pytest tests/ --ignore=tests/reproduction_tests -v

# Run dataset validation
python scripts/validate_dataset.py
```

## Project Structure

```
shopbug/
├── app/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routes/              # API route handlers
│   └── services/            # Business logic
├── tests/                   # Test suite
│   └── reproduction_tests/  # Bug reproduction tests
├── dataset/                 # Research dataset (evaluation-only)
├── scripts/                # Utility scripts
├── requirements.txt
├── .env.example
└── .gitignore
```

## License

MIT
