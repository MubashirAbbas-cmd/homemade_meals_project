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
3. Run migrations:
   ```powershell
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
- `DATABASE_URL` = Render Postgres database URL

### 4. Add a Postgres database

1. Create a Render Postgres database service.
2. Copy the provided `DATABASE_URL` into your web service environment variables.

### 5. Final deploy steps

After Render finishes building, run these commands in the Render shell or deployment hook:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

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
