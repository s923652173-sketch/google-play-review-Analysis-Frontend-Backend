from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.csv_service import ensure_data_files
from routers import apps, reviews, dashboard

ensure_data_files()

app = FastAPI(
    title="Google Play Review Analysis Backend",
    description="CSV-based backend for Google Play review sentiment trend analysis and product improvement recommendation.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(apps.router)
app.include_router(reviews.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"message": "Google Play Review Analysis Backend is running"}
