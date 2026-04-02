from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine, SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.record import FinancialRecord  # noqa: F401 — ensure table is registered
from app.routers import auth, users, records, dashboard


def seed_admin():
    """Seed a default admin user if one doesn't exist."""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@zorvyn.com").first()
        if not existing:
            admin = User(
                email="admin@zorvyn.com",
                hashed_password=hash_password("admin123"),
                full_name="Zorvyn Admin",
                role="admin",
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    seed_admin()
    yield
    # Shutdown — nothing needed


app = FastAPI(
    title="Zorvyn Finance API",
    version="1.0.0",
    description="Finance Data Processing and Access Control Backend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "Zorvyn Finance API is running", "docs": "/docs"}
