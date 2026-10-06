# ShopBug

A small e-commerce application with a FastAPI backend and a React frontend.

The backend provides user authentication, product management, a shopping cart,
a discount system, and checkout. The frontend is a modern React + Vite +
Tailwind CSS single-page application that connects to the backend API.

> **Interactive API docs (Swagger)** remain available at
> `http://127.0.0.1:8000/docs` for backend development and testing.
> The frontend at `http://localhost:5173` is the user-facing application.

---

## Technology Stack

| Layer      | Technologies                                   |
|------------|------------------------------------------------|
| Backend    | Python 3.11+, FastAPI, SQLAlchemy, SQLite, Pydantic v2 |
| Frontend   | React 18, Vite 5, Tailwind CSS 3, React Router 6 |
| Testing    | pytest, Hypothesis                             |

---

## Project Structure

```
shopbug/
├── app/                      # FastAPI backend (existing, unchanged)
│   ├── main.py               # FastAPI app + CORS + router registration
│   ├── database.py           # SQLAlchemy engine, session, init_db
│   ├── models/               # SQLAlchemy ORM models
│   ├── schemas/               # Pydantic request/response schemas
│   ├── routes/               # API route handlers (auth, products, cart, discount, checkout)
│   └── services/             # Business logic
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/       # Header, Footer, ProductCard
│   │   ├── context/          # AuthContext (user state)
│   │   ├── pages/            # Home, Products, Cart, Orders, Login, Register
│   │   ├── services/         # api.js — centralized API calls
│   │   ├── App.jsx           # Router + layout
│   │   ├── main.jsx          # React entry point
│   │   └── index.css         # Tailwind base + component styles
│   ├── .env                  # VITE_API_URL (gitignored)
│   ├── .env.example
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── scripts/                  # seed_data.py + validate_dataset.py
├── tests/                    # Backend test suite
├── dataset/                  # Research dataset (evaluation-only)
├── requirements.txt
├── .env.example
└── README.md
```

---

## 1. Backend Installation

```bash
# From the project root
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Backend Startup

```bash
# From the project root (with venv activated)
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## 3. Frontend Installation

```bash
cd frontend
npm install
```

## 4. Frontend Startup

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## 5. Seeding Sample Data

After starting the backend at least once (so the database tables are created),
seed sample products and discount codes:

```bash
# From the project root (with venv activated)
python scripts/seed_data.py
```

This populates the database with 12 sample products across 6 categories
and 2 discount codes (`SAVE10` = 10% off, `WELCOME20` = 20% off, capped at $50).

## 6. Environment Variables

### Backend (`.env` in project root)

Copy `.env.example` to `.env`:

| Variable       | Default                    | Description                        |
|----------------|----------------------------|------------------------------------|
| `DATABASE_URL` | `sqlite:///./shopbug.db`   | SQLite database path               |
| `TAX_RATE`     | `0.10`                     | Tax rate at checkout (10%)         |

### Frontend (`frontend/.env`)

Copy `frontend/.env.example` to `frontend/.env`:

| Variable       | Default                   | Description                        |
|----------------|---------------------------|------------------------------------|
| `VITE_API_URL` | `http://127.0.0.1:8000`   | Backend API base URL               |

## 7. How the Frontend Communicates with the Backend

The frontend uses a centralized API service layer at `frontend/src/services/api.js`.
All HTTP calls go through this module — no component calls `fetch` directly.

- The backend URL is read from the `VITE_API_URL` environment variable.
- CORS is configured in `app/main.py` to allow the Vite dev-server origins
  (`http://localhost:5173` and `http://127.0.0.1:5173`).
- Authentication state (user id + email) is stored in `localStorage` so it
  persists across page refreshes.

### API endpoints used by the frontend

| Method | Path                               | Purpose                |
|--------|------------------------------------|------------------------|
| POST   | `/auth/register`                   | Register a new user    |
| POST   | `/auth/login`                      | Login                  |
| GET    | `/products/`                       | List all products      |
| GET    | `/products/search?q=`              | Search products        |
| POST   | `/cart/add`                        | Add item to cart       |
| GET    | `/cart/{user_id}`                  | Get cart items         |
| PUT    | `/cart/update`                     | Update cart quantity   |
| DELETE | `/cart/remove/{product_id}?user_id=` | Remove item from cart |
| POST   | `/discounts/apply`                | Apply a discount       |
| POST   | `/checkout/?user_id=&discount_id=` | Checkout / create order|

## 8. Accessing Swagger for API Testing

Swagger UI (interactive API documentation) is available at:

```
http://127.0.0.1:8000/docs
```

This is useful for testing backend endpoints directly. The frontend does not
use or require Swagger — it is a standalone React application.

---

## Running Tests

```bash
# Backend tests
pytest tests/ -v

# Dataset validation
python scripts/validate_dataset.py
```

## License

MIT
