# Healthcare AI - Full Stack Application

A machine learning-powered healthcare application featuring a disease prediction model, an interactive frontend, and a FastAPI backend, designed for seamless deployment on Render.

## 📂 Architecture & Project Structure

The repository is structured as a full-stack monolith to simplify continuous deployment:

```text
Healthcare_AI/
│
├── main.py                  # ASGI entry point for Render (proxies to backend.main)
├── backend/                 # FastAPI application
│   ├── main.py              # Core API routing and StaticFiles mounting
│   ├── database.py          # SQLAlchemy engine, Neon Postgres pooling
│   ├── logic.py             # ML prediction logic and model loading
│   ├── models.py            # SQLAlchemy ORM definitions
│   └── schemas.py           # Pydantic validation schemas
│
├── frontend/                # Static HTML/CSS/JS interface
│   ├── index.html           # Main entry point (served by backend at `/`)
│   └── script.js            # Client-side logic (dynamic API routing)
│
├── data/                    # CSV datasets for reference/training
├── trained_model.pkl        # Serialized Random Forest Classifier
├── requirements.txt         # Pinned Python dependencies
└── Healthcare_Model_Training.ipynb  # Original model training pipeline
```

## 🚀 Deployment Pipeline (GitHub -> Render)

This application is configured for zero-downtime continuous deployment on **Render**, triggered via commits to **GitHub**.

### 1. Version Control (GitHub)
Push the repository to GitHub. The root `main.py` serves as the primary ASGI entry point, eliminating the need to alter Render's default root directory configurations.

### 2. Platform as a Service (Render)
Create a new **Web Service** on Render and link the GitHub repository.
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Frontend Integration
The frontend is served directly by the FastAPI backend via `fastapi.staticfiles.StaticFiles`. By mounting the `frontend/` directory to the root `/` path, CORS issues are eliminated and a single Render Web Service hosts the entire full-stack application.
- API URL in `frontend/script.js` is set to an empty string (`const API_URL = '';`) to dynamically resolve the host origin.

## 🗄️ Database Configuration (Neon Serverless Postgres)

The backend utilizes **Neon**, a serverless PostgreSQL database. To support Neon's aggressive connection dropping and SSL requirements, the SQLAlchemy engine in `backend/database.py` is configured with specific pooling parameters.

### Environment Variables
Configure the following in the Render dashboard (Environment Variables section):
- `DATABASE_URL`: Your Neon connection string (e.g., `postgresql://[user]:[password]@[host]/[dbname]?sslmode=require`)
- `SECRET_KEY`: Cryptographic key for JWT token generation.

*Note: The application includes internal middleware to automatically convert `postgres://` to `postgresql://` to maintain compatibility with modern SQLAlchemy versions, and automatically appends `sslmode=require` if absent.*

### Connection Pooling
The `create_engine` configuration implements:
- `pool_pre_ping=True`: Verifies connection vitality before query execution to seamlessly handle Neon's serverless idling.
- `pool_recycle=300`: Forcibly refreshes connections every 5 minutes.

## 📦 Dependency Highlights (`requirements.txt`)

Critical dependencies have been pinned to prevent downstream deployment crashes:
- `fastapi` & `uvicorn`: Core ASGI web framework and server.
- `psycopg2-binary`: PostgreSQL driver for SQLAlchemy.
- `email-validator`: Explicitly included to satisfy Pydantic's `EmailStr` dependencies.
- `bcrypt==4.0.1`: Strictly pinned to avoid breaking API changes in newer versions that cause `passlib` to throw fatal `AttributeError`/`ValueError` exceptions during password hashing operations.