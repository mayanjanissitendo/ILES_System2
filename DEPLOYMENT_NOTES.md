# ILES Deployment Notes

## Backend Checklist

1. Install dependencies:

   ```bash
   pip install -r backend/requirements.txt
   ```

2. Set production environment variables:

   ```text
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=your-backend-domain.onrender.com
   CORS_ALLOWED_ORIGINS=https://your-frontend-domain.onrender.com
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=...
   DB_USER=...
   DB_PASSWORD=...
   DB_HOST=...
   DB_PORT=5432
   ```

3. Run migrations:

   ```bash
   cd backend
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. Start command:

   ```bash
   gunicorn config.wsgi:application
   ```

## Frontend Checklist

1. Install packages:

   ```bash
   cd frontend
   npm install
   ```

2. Set API URL:

   ```text
   VITE_API_BASE_URL=https://your-backend-domain.onrender.com/api/
   ```

3. Build command:

   ```bash
   npm run build
   ```

4. Publish directory:

   ```text
   frontend/dist
   ```

## Integration Test Flow

1. Admin creates users for student, workplace supervisor, academic supervisor, and admin.
2. Admin creates an internship placement.
3. Student creates a weekly log as draft.
4. Student submits the weekly log.
5. Workplace or academic supervisor reviews/approves the log.
6. Supervisor records evaluations.
7. Dashboard shows pending reviews, approved logs, and score breakdown.
