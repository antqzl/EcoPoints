# EcoPoints

EcoPoints is a local course project with a sustainability dashboard, an EcoPoints activity tracker, a reward shop, account settings, and a FastAPI plus MySQL backend. It is intended for classroom testing and demonstrations, not production deployment.

## Features

- Email and password login
- Local account registration
- Home page with activities, initiatives, points, and energy summaries
- Dashboard with energy trends, participation data, and leaderboards
- EcoPoints activity charts and monthly progress
- Rewards shop with point costs, stock status, redemption, and feedback
- Profile settings for name, email, phone, picture, language, font size, dark mode, and notifications
- Admin demo page with programme metrics and quick-action placeholders

## Project Structure

index.html: frontend pages and UI structure
style.css: frontend styling
script.js: navigation, authentication, registration, rewards, and settings logic
backend/app/main.py: FastAPI application and API routes
backend/app/models.py: SQLAlchemy database models
backend/app/schemas.py: request and response validation
backend/app/security.py: password hashing and JWT helpers
backend/app/database.py: database engine and sessions
backend/app/config.py: environment-based configuration
backend/requirements.txt: Python dependencies
sql/schema.sql: MySQL database and table creation script
seed_demo.py: optional local demo data loader
.env.example: safe configuration template
setup_venv.ps1: creates the project virtual environment
start_backend.ps1: starts the FastAPI development server

## Requirements

- Windows
- Python 3.11 or newer
- MySQL Server running locally
- PowerShell

Recommended virtual environment location:

D:\my_env\Project_ecopoint_venv

## Configuration

1. Copy .env.example to .env in the project root.
2. Edit .env and replace the database placeholders with your local MySQL username and password.

DATABASE_URL=mysql+pymysql://YOUR_USER:YOUR_PASSWORD@127.0.0.1:3306/ecopoints
SECRET_KEY=replace-with-a-long-random-local-key
ACCESS_TOKEN_EXPIRE_MINUTES=120
CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500

Never commit .env to GitHub. It contains private database credentials. The .gitignore file excludes it.

If the MySQL password contains characters such as @, :, /, ?, #, percent, or &, URL-encode those characters in DATABASE_URL.

## Database Setup

Open MySQL Workbench or the MySQL command line and run sql/schema.sql. It creates the ecopoints database and the users, initiatives, point_transactions, rewards, redemptions, and energy_readings tables.

If MySQL is installed at D:\mysql\server, the PowerShell command is:

Get-Content -Raw .\sql\schema.sql | & D:\mysql\server\bin\mysql.exe -u root -p

## First-Time Setup

From the project root, run:

Set-ExecutionPolicy -Scope Process Bypass
.\setup_venv.ps1

This creates the virtual environment and installs backend/requirements.txt.

After configuring MySQL and .env, optionally load demo content:

& D:\my_env\Project_ecopoint_venv\Scripts\python.exe .\seed_demo.py

The demo account is:

Email: sarah.tan@example.edu
Password: EcoPointsDemo123!

## Run the Application

Use two PowerShell windows.

Window 1, start the API:

cd C:\path\to\EcoPoints
.\start_backend.ps1

The API runs at http://127.0.0.1:8000. API documentation is at http://127.0.0.1:8000/docs.

Window 2, start the frontend:

cd C:\path\to\EcoPoints
& D:\my_env\Project_ecopoint_venv\Scripts\python.exe -m http.server 5500 --directory .

Open http://127.0.0.1:5500/index.html in a browser. Use the local HTTP server instead of opening index.html directly so frontend API requests work consistently.

Stop either server with Ctrl+C.

## Main API Endpoints

GET /health
POST /api/auth/login
POST /api/auth/register
GET /api/me
GET /api/initiatives
GET /api/rewards
POST /api/rewards/{reward_id}/redeem
GET /api/home/summary
GET /api/dashboard/summary

## Notes for Team Members

- Keep .env local and private. Upload .env.example instead.
- Do not upload the virtual environment, .git, __pycache__, or .pyc files.
- Google Sign-In is currently a placeholder and requires Google OAuth configuration.
- Admin quick actions are UI placeholders for future management endpoints.
- Profile preferences are stored locally in the browser for this course demo.
