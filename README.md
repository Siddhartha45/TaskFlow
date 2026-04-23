# TaskFlow API

A fully fledged backend REST API for task and project management — built with Django, DRF, Celery, and Docker.

Users can create projects, add tasks to each project, receive automatic email reminders for upcoming tasks, and export tasks related to a project in Excel file.

---

## Tech Stack

| Category | Technologies |
|---|---|
| Backend | Django, Django REST Framework |
| Database | PostgreSQL |
| Auth | JWT (SimpleJWT) |
| Task Queue | Celery, Redis |
| Data Export | Pandas, openpyxl |
| Container | Docker, Docker Compose |

---

## Features

- **JWT Authentication** — Register, login, and refresh tokens
- **Project Management** — Full CRUD for projects
- **Task Management** — Full CRUD with `status` (todo / in_progress / done) and `priority` (low / medium / high)
- **Task Filtering** — Filter by status, priority, or due_date
- **Email Reminders** — Celery Beat runs daily at 9:00 UTC, sends reminders for tasks due tomorrow
- **Excel Export** — Download all tasks in a project as `.xlsx` using Pandas
- **Fully Dockerized** — One command starts all 5 services (db, web, redis, celery_worker, celery_beat)

---

## How It Works

### Email Reminders (Celery)

1. Celery Beat triggers `task_reminder()` daily at 9:00 UTC
2. Queries all tasks where `due_date = tomorrow` and `status != done`
3. Groups tasks by project owner
4. Sends one email per user listing all their upcoming tasks

### Excel Export (Pandas)

1. User calls `GET /api/projects/{id}/tasks/export/`
2. Server filters tasks for that project
3. Pandas builds a DataFrame and writes it to Excel
4. Browser downloads the file as `{project_name}.xlsx`

### Permissions

- Users can only access their own projects and tasks
- All endpoints require a valid JWT token

---

## Prerequisites

- Docker Desktop
- Git

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Siddhartha45/TaskFlow.git
cd TaskFlow
```

Create a `.env` file in the project root and set the required environment variables. See the [Environment Variables](#environment-variables) section for reference.

```bash
# Then start all services
docker compose up --build
```

The API will be available at **http://localhost:8000**

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/login/` | Get JWT access + refresh tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |

### Projects

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/projects/` | List all projects (user's own) |
| POST | `/api/projects/` | Create a project |
| GET | `/api/projects/{id}/` | Retrieve a project |
| PUT | `/api/projects/{id}/` | Update a project |
| DELETE | `/api/projects/{id}/` | Delete a project |

### Tasks

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/projects/{project_id}/tasks/` | List tasks in a project |
| POST | `/api/projects/{project_id}/tasks/` | Create a task |
| GET | `/api/projects/{project_id}/tasks/{id}/` | Retrieve a task |
| PUT | `/api/projects/{project_id}/tasks/{id}/` | Update a task |
| DELETE | `/api/projects/{project_id}/tasks/{id}/` | Delete a task |

### Task Filters

Append query parameters to the GET tasks endpoint:

```
/api/projects/1/tasks/?status=todo
/api/projects/1/tasks/?priority=high
/api/projects/1/tasks/?due_date=2026-04-15
/api/projects/1/tasks/?status=in_progress&priority=high
/api/projects/1/tasks/?status=in_progress&priority=high&due_date=2026-04-15
```

### Export

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/projects/{project_id}/tasks/export/` | Download all tasks of that particular project as Excel (`.xlsx`) |

---

## Environment Variables

Create a `.env` file in the project root:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DB_NAME=taskflow_db
DB_USER=taskflow_db_user
DB_PASSWORD=your-db-password
DB_HOST=db
DB_PORT=5432

# Redis / Celery
REDIS_URL=redis://redis:6379/0

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

> For production: set `DEBUG=False` and switch `EMAIL_BACKEND` in `settings.py` to SMTP.

---

## Project Structure

```
TaskFlow/
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements.txt
├── .dockerignore
├── .gitignore
├── .env
├── taskflow/           # Main app
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── accounts/
│   ├── models.py        # Custom User
│   ├── views.py         # Register
│   └── urls.py
└── tasks/
    ├── models.py        # Project, Task
    ├── views.py         # CRUD, Export
    ├── serializers.py
    ├── tasks.py         # Celery email task reminder
    └── urls.py
```

---

## Running Without Docker

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start only the database and Redis via Docker
docker compose up -d db redis

# Run migrations and start Django
python manage.py migrate
python manage.py runserver

# In separate terminals:
celery -A taskflow worker --loglevel=info
celery -A taskflow beat --loglevel=info
```
