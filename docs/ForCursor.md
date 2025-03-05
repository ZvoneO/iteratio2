= Development Guide: Resource Planning Application

== Project Overview

=== **Brief Description**
The Resource Planning Application is a web-based system designed to manage projects, clients, and consultants efficiently. The platform includes an Admin Dashboard for user and resource management, role-based access control, and reporting tools. Users can create and manage projects, assign consultants, track progress, and generate reports for resource allocation.

=== **Main Goals and Objectives**
- **Provide a central system** for managing projects, clients, and consultants.
- **Role-based access control** to ensure users can only access relevant information.
- **Task and resource tracking** to enhance efficiency and project execution.
- **Data analytics and reporting** for better decision-making.
- **Integration capabilities** to support future expansions.

== Tech Stack

=== **Backend**
- **Flask (Python 3.x)** – Web framework
- **Flask-SQLAlchemy** – ORM for database interactions
- **Flask-Login** – Authentication management
- **SQLite** – Development database (optional upgrade to PostgreSQL for production)

=== **Frontend**
- **HTML + Jinja2** – Template rendering
- **CSS & JavaScript** – Frontend interactivity
- **Bootstrap** (Optional) – UI framework for styling

=== **Deployment**
- **Gunicorn** – WSGI server for production
- **Docker** (Optional) – Containerization
- **Heroku/AWS/DigitalOcean** – Hosting options

=== **Version Requirements**
- Python **3.9+**
- Flask **2.x**
- SQLite **3.x** (or PostgreSQL 14+ for production)
- Bootstrap **5.x** (if used)
- Node.js (optional for frontend enhancements)

== Code Standards

=== **Coding Style Guidelines**
- Follow **PEP 8** for Python code formatting.
- Use **Flask Blueprints** to structure modules cleanly.
- Consistent **indentation (4 spaces)** for Python.
- Use **docstrings** for function and module documentation.

=== **Naming Conventions**
- Variables and functions: **snake_case** (e.g., `get_project_data()`)
- Classes: **PascalCase** (e.g., `ProjectManager`)
- Constants: **UPPER_CASE** (e.g., `MAX_TASKS = 10`)
- Database tables: **snake_case** (e.g., `project_templates`)
- Routes: **dash-separated** (e.g., `/manage-projects`)

=== **File Structure Rules**
```plaintext
resource_planner/
│── app/
│   │── __init__.py
│   │── models.py
│   │── routes/
│   │   │── __init__.py
│   │   │── projects.py
│   │   │── clients.py
│   │   │── consultants.py
│   │── templates/
│   │── static/
│── config.py
│── run.py
│── requirements.txt
│── README.md
```

== Development Workflow

=== **Git Branching Strategy**
- `main` – Stable production-ready branch.
- `develop` – Active development branch.
- `feature/feature-name` – New features under development.
- `hotfix/fix-name` – Critical fixes applied to production.
- `release/version-x.y` – Pre-release stabilization.

=== **Code Review Process**
- All feature branches require a **pull request (PR)** before merging.
- **At least one reviewer** must approve the PR.
- PRs must pass **automated tests** before merging.

=== **Testing Requirements**
- **Unit tests:** Required for all API endpoints.
- **Integration tests:** For testing database interactions.
- **UI tests:** For core features using Selenium (optional).
- **Security tests:** Ensure role-based restrictions work correctly.

== Performance and Security

=== **Performance Benchmarks**
- API response time should be **< 300ms** for standard queries.
- Database queries must use **indexes where applicable**.
- Frontend should load under **2 seconds** on average.

=== **Security Guidelines**
- **User authentication** via Flask-Login with secure password hashing (bcrypt).
- **CSRF protection** enabled for all forms.
- **Data validation** for all user inputs to prevent SQL injection.
- **Role-based access control (RBAC)** to restrict unauthorized actions.
- **HTTPS enforced** for all environments.

This guide ensures best practices are followed during development to maintain code quality, security, and performance.


