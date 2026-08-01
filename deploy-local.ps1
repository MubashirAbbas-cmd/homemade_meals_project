# Local deploy helper for the Homemade Meals app

Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
pip install -r requirements.txt

Write-Host "Making migrations..."
python manage.py makemigrations
python manage.py migrate

Write-Host "Collecting static files..."
python manage.py collectstatic --noinput

Write-Host "Local setup complete. Run 'python manage.py runserver' to start the app."