import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL examples:
# - Railway Postgres:       postgres://USER:PASSWORD@HOST:PORT/DBNAME
# - SQL Server (Azure/VM):  mssql+pyodbc://USER:PASSWORD@HOST:1433/DBNAME?driver=ODBC+Driver+17+for+SQL+Server
# - Local dev (fallback):   sqlite:///./app.db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()