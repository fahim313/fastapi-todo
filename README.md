# FastAPI Todo App

A simple **Todo App** built with **FastAPI**. Users can register, log in (with JWT), and then create, view, update, and delete their own todos. It uses **PostgreSQL** as the database and **Alembic** for database migrations.

## Features

- User registration and login with JWT tokens (`router/auth.py`)
- Admin-only routes (`router/admin.py`)
- User profile routes (`router/users.py`)
- Full CRUD for todos (Create, Read, Update, Delete)
- Each user can only see and manage their own todos
- Database migrations with Alembic
- Passwords are hashed (bcrypt / passlib)

## Tech Stack

| Category | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Auth | OAuth2 + JWT (python-jose) |
| Password Hashing | passlib, bcrypt |
| Validation | Pydantic v2 |
| Server | Uvicorn |

## Project Structure

```
fastapi-todo
├── main.py
├── database.py
├── models.py
├── router/
│   ├── auth.py
│   ├── admin.py
│   └── users.py
├── alembic/
├── alembic.ini
├── requirements.txt
├── .env
└── .gitignore
```

## Requirements

- Python 3.10+
- A running PostgreSQL server

## Installation

```bash
# 1. Clone the repo
git clone <repo-url>
cd <project-folder>

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Environment Variables (.env)

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<db_name>
```

> ⚠️ Never push your `.env` file to git — it should be listed in `.gitignore`.

## Database Migrations (Alembic)

```bash
# Create a new migration
alembic revision --autogenerate -m "message"

# Apply migrations
alembic upgrade head
```

## Running the App

```bash
uvicorn main:app --reload
```

Server will run at: `http://127.0.0.1:8000`
Swagger docs: `http://127.0.0.1:8000/docs`

## API Endpoints

### Todo (`main.py`) — Login required

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Get all todos of the logged-in user |
| GET | `/todo/{todo_id}` | Get one specific todo |
| POST | `/create` | Create a new todo |
| PUT | `/update/{todo_id}` | Update a todo |
| DELETE | `/delete/{todo_id}` | Delete a todo |

### Auth / Admin / Users
These endpoints are defined in `router/auth.py`, `router/admin.py`, and `router/users.py` — this is where you'll find registration, login (JWT token), admin-only actions, and user profile routes.

## Data Models

**Todos**
- `id`, `title`, `description`, `priority` (1-5), `complete`, `owner_id`

**Users**
- `id`, `email`, `username`, `firstname`, `lastname`, `hash_password`, `is_active`, `role`, `phone_number`

## Roadmap

- [ ] Add unit and integration tests (pytest is already in requirements.txt)
- [ ] Add pagination and filtering
- [ ] Dockerize the project

## License

This project is for learning purposes. Add a license (MIT/Apache 2.0, etc.) as needed.