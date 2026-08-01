# Homemade Meals Django App

This Django project is now prepared for production deployment on a platform like Render.

## What was added

- `requirements.txt` for dependencies
- `Procfile` for Gunicorn startup
- `.gitignore` to ignore local files
- `core/settings.py` updated for environment-based production settings
- `whitenoise` configured for static files
- `dj-database-url` configured for production database URL

## Local setup

1. Activate your virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
2. Install Python packages:
   ```powershell
   pip install -r requirements.txt
   ```
3. Create any missing migrations and apply them:
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Collect static files:
   ```powershell
   python manage.py collectstatic --noinput
   ```
5. Run locally:
   ```powershell
   python manage.py runserver
   ```

## Before deployment

1. Create a GitHub repository and push this project to the `main` branch.
2. Open a Cloudinary account and copy your `cloud_name`, `api_key`, and `api_secret`.
3. Use the `.env.example` file as a template for your production variables.
4. Confirm `DEBUG=False` and `DJANGO_SECRET_KEY` is set to a strong secret in production.

## Deploying to Render

### 1. Push code to GitHub

```powershell
git add .
git commit -m "Prepare project for deployment"
git branch -M main
git remote add origin https://github.com/yourusername/yourrepo.git
git push -u origin main
```

### 2. Create a Render web service

1. Go to https://render.com and sign in.
2. Click **New** → **Web Service**.
3. Connect your GitHub account and choose this repository.
4. Configure the service:
   - Branch: `main`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn core.wsgi:application`

### 3. Add environment variables on Render

Set these values in Render's Environment section:

- `DJANGO_SECRET_KEY` = a long secret string
- `DJANGO_DEBUG` = `False`
- `DJANGO_ALLOWED_HOSTS` = `your-app-name.onrender.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS` = `https://your-app-name.onrender.com`
- `DATABASE_URL` = Render Postgres database URL
- `DJANGO_USE_CLOUDINARY` = `True`
- `CLOUDINARY_CLOUD_NAME` = your Cloudinary cloud name
- `CLOUDINARY_API_KEY` = your Cloudinary API key
- `CLOUDINARY_API_SECRET` = your Cloudinary API secret

### 4. Add a Postgres database

1. Create a Render Postgres database service.
2. Copy the provided `DATABASE_URL` into your web service environment variables.

### 5. Final deploy steps

After Render finishes building, run these commands in the Render shell or deployment hook:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## Render files included in this repo

- `.render.yaml` — Render service configuration
- `runtime.txt` — Python runtime version
- `Procfile` — Gunicorn startup command

## Example `.env.example`

```text
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,your-app-name.onrender.com
DATABASE_URL=postgres://user:password@host:port/dbname
```

## Common mistakes to avoid

- Do not leave `DEBUG = True` in production
- Do not commit your real `SECRET_KEY` to GitHub
- Make sure the live host is in `ALLOWED_HOSTS`
- Do not deploy without `gunicorn` and `whitenoise` configured
- Do not use local `sqlite3` as the production database if you want a stable live site

## Live URL

After successful deploy, Render will provide a URL like:

`https://your-app-name.onrender.com`

Use that URL to share the site with clients.
