from fastapi import APIRouter

from config import APPS_CSV, REVIEWS_CSV
from services.csv_service import read_csv
from services.analysis_service import (
    get_monthly_sentiment_trend,
    sample_recent_reviews,
)
from services.llm_service import get_or_update_daily_recommendation

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/{app_id}")
def get_dashboard_data(app_id: str):
    apps_df = read_csv(APPS_CSV)
    reviews_df = read_csv(REVIEWS_CSV)

    app_row = apps_df[apps_df["app_id"] == app_id]

    if app_row.empty:
        return {"error": "App not found"}

    app_name = app_row.iloc[0]["app_name"]

    trend = get_monthly_sentiment_trend(
        reviews_df=reviews_df,
        app_id=app_id,
    )

    sampled_reviews = sample_recent_reviews(
        reviews_df=reviews_df,
        app_id=app_id,
        sample_size=10,
    )

    recommendation_result = get_or_update_daily_recommendation(
        app_id=app_id,
        app_name=app_name,
        sampled_reviews=sampled_reviews,
    )

    return {
        "app_id": app_id,
        "app_name": app_name,
        "trend_last_12_months": trend,
        "sampled_reviews_last_28_days": sampled_reviews,
        "recommendation": recommendation_result,
    }
