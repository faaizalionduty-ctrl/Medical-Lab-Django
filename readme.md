# Medical Lab (Fatima Lab) — Django Project

A Django application to manage patients, bills, tests, doctors, and payments for a medical laboratory.

This repository contains a minimal, ready-to-run Django site used to track lab tests, generate bills, and record payment transactions.

## Short overview
- Framework: Django (project configured in `medical_lab/`)
- Main apps: `dashboard`, `patients`, `labtests`, `doctors`
- Frontend: templates use Tailwind CSS and Choices.js (included via CDN in `templates/base.html`)
- Entry points: `manage.py` (development), `medical_lab/wsgi.py` (production)

## Requirements
- Python 3.10+ recommended
- See pinned dependencies in `requirements.txt`

## Quick start (development)
1. Create and activate a virtual environment
	 ```bash
	 python -m venv .venv
	 source .venv/bin/activate
	 ```
2. Install dependencies
	 ```bash
	 pip install -r requirements.txt
	 ```
3. Run migrations
	 ```bash
	 python manage.py migrate
	 ```
4. (Optional) Create a superuser
	 ```bash
	 python manage.py createsuperuser
	 ```
5. Start the development server
	 ```bash
	 python manage.py runserver
	 ```
6. Visit http://127.0.0.1:8000/ to view the site (root URLs are configured in `medical_lab/urls.py`).

## Database / migrations
- The project uses SQLite by default (check `medical_lab/settings.py`).
- Each app contains its own `migrations/` folder. After editing models run:
	```bash
	python manage.py makemigrations
	python manage.py migrate
	```

## Project layout (high level)
- Project root
	- `manage.py` — Django CLI entry
	- `Procfile` — deployment entry (Heroku-style)
	- `requirements.txt` — pinned Python dependencies
- Project package: `medical_lab/`
	- `settings.py`, `urls.py`, `wsgi.py`, `asgi.py`
- Apps
	- `patients/` — models and views for patients, bills, payment transactions
	- `labtests/` — lab test model and CRUD views
	- `doctors/` — doctor model and CRUD views
	- `dashboard/` — reporting and overviews
- Templates: `templates/` — base layout and app templates (see files under `templates/`) 

## Key implementation notes
- Payments are transaction-based: `PaymentTransaction` records payments and `Bill` computes `total_paid` and `amount_due` dynamically.
- Existing migrations reflect a refactor from a simple bill status/due_amount to the transaction model.
- Choices.js is used for searchable selects and is initialized in templates (check `templates/base.html`).

## Common commands
- Run dev server:
	```bash
	python manage.py runserver
	```
- Run tests:
	```bash
	python manage.py test
	```
- Make & apply migrations:
	```bash
	python manage.py makemigrations
	python manage.py migrate
	```

## Notes / Gotchas
- Time zone in `medical_lab/settings.py` is set to `Asia/Karachi`.
- The Django SECRET_KEY is stored in `settings.py` (suitable for development only). Move secrets to environment variables for production.
- `settings.py` contains a CSRF trusted origin for an ngrok URL — remove or update for your deployment.

## Where to look first
- Billing/payment flow: `patients/models.py` and `patients/views.py`.
- Lab test definitions and prices: `labtests/models.py` and `templates/labtests/`.
- To change UI layout: `templates/base.html` and the app templates under `templates/`.

## Next steps (suggested)
- Add a `CONTRIBUTING.md` describing development workflow.
- Add a `.env.example` and update `settings.py` to read secrets from environment variables.
- Add a simple `Dockerfile` and `docker-compose.yml` for local development.

## License
No license file is included. Add a `LICENSE` if you plan to publish or share this repository.

---

If you'd like, I can also add a `CONTRIBUTING.md`, a `.env.example`, and a `Dockerfile` now — tell me which one to add first.

