from fastapi import APIRouter
import pandas as pd

from config import APPS_CSV, REVIEWS_CSV
from services.csv_service import read_csv, save_csv
from services.review_collector import collect_reviews_from_google_play
from services.sentiment_service import analyse_sentiment

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
)


@router.post("/collect/{app_id}")
def collect_reviews(
    app_id: str,
    months_back: int = 12,
    reviews_per_month: int = 100
):
    apps_df = read_csv(APPS_CSV)

    app_row = apps_df[apps_df["app_id"] == app_id]

    if app_row.empty:
        return {
            "error": "App not found. Please add the app first."
        }

    app_name = app_row.iloc[0]["app_name"]

    raw_reviews = collect_reviews_from_google_play(
        app_package_name=app_id,
        months_back=months_back,
        reviews_per_month=reviews_per_month
    )

    rows = []

    for item in raw_reviews:
        content = item.get("content")

        if not content:
            continue

        sentiment_label, sentiment_score = analyse_sentiment(content)

        rows.append({
            "app_id": app_id,
            "app_name": app_name,
            "user_name": item.get("user_name"),
            "content": content,
            "score": item.get("score"),
            "review_date": item.get("review_date"),
            "sentiment_label": sentiment_label,
            "sentiment_score": sentiment_score,
            "word_count": len(str(content).split())
        })

    new_reviews_df = pd.DataFrame(rows)

    old_reviews_df = read_csv(REVIEWS_CSV)

    combined_df = pd.concat(
        [old_reviews_df, new_reviews_df],
        ignore_index=True
    )

    combined_df = combined_df.drop_duplicates(
        subset=["app_id", "content", "review_date"],
        keep="last"
    )

    save_csv(combined_df, REVIEWS_CSV)

    return {
        "message": "Reviews collected and analysed successfully",
        "app_id": app_id,
        "app_name": app_name,
        "months_back": months_back,
        "reviews_per_month": reviews_per_month,
        "collected_count": len(rows),
        "total_saved_count": len(combined_df)
    }


@router.get("/{app_id}")
def get_reviews(app_id: str):
    reviews_df = read_csv(REVIEWS_CSV)

    if reviews_df.empty:
        return []

    app_reviews = reviews_df[reviews_df["app_id"] == app_id]
    return app_reviews.fillna("").to_dict(orient="records")
