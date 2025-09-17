# MUL GPA Calculator

Purple/white classic look matching the screenshot, 8-semester GPA calculator with editable Grade Points, Total GP per row, and GPA summary. Backend on FastAPI; frontend static + Pyodide (Python-in-browser). Data is seeded from your provided semester lists.

## Stack
- Frontend: Static HTML/CSS/JS + Pyodide (Python) — deploy on Vercel
- Backend: FastAPI + SQLAlchemy — deploy on Railway
- Database:
  - Recommended on Railway: PostgreSQL
  - Alternatively: SQL Server 2022 (host externally, e.g., Azure SQL). SQLAlchemy DSN supported. SQL Server DDL provided at the end of this README.

## Local Dev

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Choose a DB:
export DATABASE_URL=sqlite:///./app.db           # quick local
# OR Postgres: export DATABASE_URL=postgresql://USER:PASS@HOST:5432/DBNAME
# OR SQL Server: export DATABASE_URL="mssql+pyodbc://USER:PASS@HOST:1433/DBNAME?driver=ODBC+Driver+17+for+SQL+Server"

uvicorn app.main:app --reload